#!/usr/bin/env python
import asyncio
import async_timeout
import aiohttp
import random
import aiofiles
import json
import re
import pymongo
import logging
from pymongo import MongoClient


logging.basicConfig(filename="app.log", level=logging.INFO)


def open_save_file(path, mode, data_string=None, callback=None):
    """Return string or array or [type]callback
    RW string to files. Modes are: r w
    """
    with open(path, mode=mode, encoding="utf-8") as f:
        output = ""
        if mode is "r":
            output = f.read()
        elif mode is "w":
            f.write(data_string)
            output = data_string
        f.close()
        if callback is None:
            return output
        else:
            return callback(output)


@DeprecationWarning
async def bound_fetch(sem, session, url, method="GET", postdata="",  **headers):
    """Deprecated, search aiohttp semaphore.
    """
    async with sem:
        await fetch(session, url, method, postdata, **headers)


async def fetch(session, url, method="GET", postdata="",  **headers):
    """Return string
    fetch using aiohttp, methods are: GET POST PUT
    """
    try:
        if headers is None:
            headers = {}
        headers["User-Agent"] = "Private Scrapper: github.com/bernzJ/sentiment_analysis"
        headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        headers["Accept-Language"] = "en-US,en;q=0.5"
        with async_timeout.timeout(30):
            if method == "GET" and postdata != "":
                async with session.request(method, url, headers=headers, params=postdata) as response:
                    # print(response.request_info.url)
                    return await response.text()
            else:
                async with session.request(method, url, headers=headers, data=postdata) as response:
                    return await response.text()
    except Exception as e:
        logging.error("Error: {}\nArgs: {}".format(str(e), e.args))
        return "Error"


def log_error(error):
    """Return None
    Public extension of logger class, param must be string.
    """
    logging.error(error)


def is_json(data):
    """Return string or dict
    Try to load (string)param as json, on fail return param.
    """
    try:
        return json.loads(data)
    except:
        return data


def mongo_client():
    """Return mongo_client object.
    Load mongo config: username, password, authSource, host
    """
    mongo_settings = json.loads(open_save_file("./mongo.json", "r"))
    if type(mongo_settings) is dict:
        return MongoClient(mongo_settings["host"], username=mongo_settings["username"],
                           password=mongo_settings["password"], authSource=mongo_settings["authSource"])
    return MongoClient()


def exist_key_database(key_name, client=None):
    """Return bool
    Check if key exists as index in db.
    """
    try:
        if not client:
            client = mongo_client()
        db = client.reddit_mind.post
        if key_name in db.index_information():
            return True
        else:
            return False
    except Exception as e:
        logging.error("Error: {}\nArgs: {}".format(str(e), e.args))


def save_database(data_json):
    """Return mongodb inserted data information.
    Try to insert data into mongo doc, log catch error.
    """
    try:
        client = mongo_client()
        db = client.reddit_mind.post
        return db.insert_one(data_json)
    except Exception as e:
        logging.error("Error: {}\nArgs: {}".format(str(e), e.args))


def has_keyword(list_post, fields, keywords):
    """Return list
    Search list childs for a dict containing a specific keyword.
    """
    results = []
    for field in fields:
        if field in list_post:
            for keyword in keywords:
                if keyword.upper() in list_post[field].upper():
                    results.append(field)
    return results


def parse_reddit_url(url):
    """Return dict or None
    Try to parse url into reddit style.
    """
    segments = url.split("/")
    if len(segments) is not 7:
        logging.error("Invalid sub-reddit url: {}".format(url))
        return None
    return {
        "id": segments[4],
        "sub-reddit": segments[2],
        "safe_title": segments[5]
    }
