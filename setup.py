from setuptools import setup

setup(
    name="sentiment_analysis",
    version="1.0",
    description="Update this.",
    author="Ben J",
    author_email="benje@hotmail.ca",
    packages=["sentiment_analysis"],
    install_requires=["aiohttp", "aiofiles", "pymongo"],  # external packages as dependencies
)