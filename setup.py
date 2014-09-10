import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "aioprocessing",
    version = '0.0.1',
    packages = find_packages(exclude=["tests"]),

    author = "Dan O'Reilly",
    author_email = "oreilldf@gmail.com",
    description = """
    A Python 3.3+ library that integrates the [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) module with [asyncio](https://docs.python.org/3/library/asyncio.html).

    """,
    license = "BSD",
    keywords = "asyncio multiprocessing coroutine",
    url = "https://github.com/dano/aioprocessing",
    long_description = """
    aioprocessing provides non-blocking coroutine versions of many blocking instance methods on objects in the `multiprocessing` library. Here's an example showing non-blocking usage of `Event`, `Queue`, and `Lock`
""",
)


