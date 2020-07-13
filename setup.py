#!/usr/bin/env python

from distutils.core import setup

setup(
    name="github-copy",
    version="0.0.2",
    description="Copy files from one GitHub repo to another and perform transformations on the files during the copy process",
    url="https://github.com/GSA/github-copy",
    packages=["github-copy",],
    scripts=[
        "github-copy/__main__.py",
        "github-copy/transformers/prefix.py",
    ],
    entry_points={"console_scripts": ["github-copy = github_copy:main"]},
)
