
#!/usr/bin/env python
import asyncio
import async_timeout
import aiohttp
import random
import aiofiles
import json
import re
import logging
import helpers

from pymongo import MongoClient
from time import sleep


async def save_database(data_json):
    client = MongoClient()
    db = client.reddit_mind
    db.post.insert_one(data_json)


async def queue_analyze_data(session, results, apis):
    for result in results:
        analyzed = [{"Error"}]
        tries = 0
        while [data for data in analyzed if "Error" in data]:
            if "body" in result["obj"]:
                analyzed = await analyze_data(session, result["obj"]["title"], apis)
            else:
                analyzed = await analyze_data(session, result["obj"]["title"], apis)
            if tries >= 10:
                break
            tries += 1
        result["obj"] = analyzed
        await save_database(result["obj"])


async def analyze_data(session, data_string, apis):
    analyzed = []
    for api in apis:
        if "json_data" in api and "data_string" in api["json_data"]:
            api["json_data"]["data_string"] = data_string
        analyzed.append({"api": api["name"], "data": await helpers.fetch(session, api["url"], api["method"], api["json_data"], **api["headers"])})
    print("[**] Analyze api data: {}".format(analyzed))
    return analyzed


async def scrap_comments(session, subreddit, apis):
    subreddit_dict = helpers.parse_reddit_url(subreddit)
    json_dict = json.loads(await helpers.fetch(session, "https://www.reddit.com/r/{}/comments/{}.json?".format(subreddit_dict["sub-reddit"], subreddit_dict["id"])))

    print("[**] scrapped comments ..")
    results = []
    for data in json_dict:
        for children in data["data"]["children"]:
            saved_data = {}
            if "title" in children["data"]:
                saved_data["title"] = children["data"]["title"]
            saved_data["url"] = children["data"]["url"]
            saved_data["ups"] = children["data"]["ups"]
            saved_data["downs"] = children["data"]["downs"]
            saved_data["score"] = children["data"]["score"]
            saved_data["author"] = children["data"]["author"]
            saved_data["created_utc"] = children["data"]["created_utc"]
            results.append(saved_data)
    return results


async def get_new_subs(session, after=None):
    url = "https://www.reddit.com/r/all/new/"
    if after:
        url = "https://www.reddit.com/r/all/new/?count=25&after={}".format(
            after)
    dom = await helpers.fetch(session, url)
    if not dom:
        return "Out of data !"
    return re.findall("data-inbound-url=\"(.*?)\" ", dom, re.DOTALL)


async def queue():
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:

        matches = []
        tasks = []
        apis = json.loads(helpers.open_save_file("./api.json", "r"))
        last_id = matches[len(matches) - 1]

        print("[**] Init, got {} matches ..".format(len(matches) - 1))
        while True:
            if not matches:
                matches = await get_new_subs(session, last_id)
                if matches == "Out of data !":
                    print("[***] Out of matches, stopping ..")
                    return
                last_id = matches[len(matches) - 1]
                print("[**] Got new matches ..")
            match = matches.pop()
            task = asyncio.ensure_future(
                scrap_comments(session, match, apis))
            tasks.append(task)
            results = await asyncio.gather(*tasks)
            queue_analyze_data(session, results, apis)


def main():
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(queue())
    loop.run_until_complete(future)


if __name__ == '__main__':
    main()
