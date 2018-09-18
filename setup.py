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
    scripts=['cli.py'],
    packages=find_packages(),
    entry_points={
    	'console_scripts': ['mtp-interactive=cli:main']
    }
)


#!/usr/bin/env python

# from setuptools import setup

# setup(
#     name="torch-crypto",
#     version='0.1.0',
#     description="Command-line Cryptanalysis",
#     author='Cameron Lonsdale',
#     author_email='cameron.lonsdale@gmail.com',
#     url='https://github.com/CameronLonsdale/torch',
#     license='MIT',
#     install_requires=['click', 'lantern'],
#     scripts=['torch.py'],
#     entry_points={
#         'console_scripts': ['torch=torch:cli']
#     }
# )