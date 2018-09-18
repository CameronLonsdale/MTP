#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='mtp-interactive',
    version='1.0.0',
    description='Interactive Many Time Pad',
    author='Cameron Lonsdale',
    author_email='cameron.lonsdale@gmail.com',
    url='https://github.com/CameronLonsdale/Many-Time-Pad-Interactive',
    license='MIT',
    packages=find_packages(),
    scripts=['cli.py'],
    entry_points={
    	'console_scripts': ['mtp-interactive=cli:main']
    }
)
