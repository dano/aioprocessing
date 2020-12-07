from setuptools import setup, find_packages
import aioprocessing

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name="aioprocessing",
    version=aioprocessing.version,
    packages=find_packages(exclude=["tests"]),
    author="Dan O'Reilly",
    author_email="oreilldf@gmail.com",
    description=(
        "A Python 3.5+ library that integrates "
        "the multiprocessing module with asyncio."
    ),
    zip_safe=False,
    license="BSD",
    keywords="asyncio multiprocessing coroutine",
    url="https://github.com/dano/aioprocessing",
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
