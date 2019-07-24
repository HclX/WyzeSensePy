#!/usr/bin/env python

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wyzesense",
    version="0.0.4",
    author="Xuan Xing",
    author_email="hclxing@gmail.com",
    description="WyzeSense gateway library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HclX/WyzeSensePy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
