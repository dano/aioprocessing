import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
import aioprocessing

with open("README.rst") as f:
    readme = f.read()

setup(
    name="aioprocessing",
    version=aioprocessing.version,
    packages=find_packages(exclude=["tests"]),
    author="Dan O'Reilly",
    author_email="oreilldf@gmail.com",
    description=" A Python 3.3+ library that integrates the multiprocessing module with asyncio.",
    zip_safe=False,
    license="BSD",
    keywords="asyncio multiprocessing coroutine",
    url="https://github.com/dano/aioprocessing",
    long_description=readme,
)


