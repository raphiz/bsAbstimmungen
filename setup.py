#!/usr/bin/env python
# encoding: utf-8

import os

from setuptools import setup, find_packages

setup(
    name="bsAbstimmungen",
    version="0.1.0",
    packages=['bsAbstimmungen'],
    author="Raphael Zimmermann",
    author_email="dev@raphael.li",
    url="https://github.com/raphiz/bsAbstimmungen",
    description="",
    long_description=open('./README.md').read(),
    license="MIT",
    platforms=["Linux", "BSD", "MacOS"],
    include_package_data=True,
    zip_safe=False,
    install_requires=open('./requirements.txt').read(),
    tests_require=open('./requirements-dev.txt').read(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        "Programming Language :: Python :: Implementation :: CPython",
        'Development Status :: 4 - Beta',
    ],
)
