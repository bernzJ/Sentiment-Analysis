from setuptools import setup

setup(
    name="sentiment_analysis",
    version="1.0",
    description="Analytic tool allowing to analyze reddit new posts/comments feed searching for specific keywords/sentences to be then sent to score apis like mashape.",
    author="Ben J",
    author_email="benje@hotmail.ca",
    packages=["sentiment_analysis"],
    install_requires=["aiohttp", "aiofiles", "pymongo"],  # external packages as dependencies
)
