#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='mtp',
    version='1.1.0',
    description='Many-Time Pad Interactive',
    author='Cameron Lonsdale',
    author_email='cameron.lonsdale@gmail.com',
    url='https://github.com/CameronLonsdale/MTP',
    license='MIT',
    packages=find_packages(),
    scripts=['cli.py'],
    install_requires=[
        "urwid==2.1.2"
    ],
    entry_points={
    	'console_scripts': ['mtp=cli:main']
    }
)
