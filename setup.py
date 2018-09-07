# (C) Copyright 2018 Enthought, Inc., Austin, TX
# All rights reserved.
#

from setuptools import setup, find_packages

setup(
    name='brood_diff',
    version='0.3.0',
    url='',
    author='Maxwell Grady',
    author_email='mgrady@enthought.com',
    description='Calculate the diff between two brood indices',
    packages=find_packages(),
    install_requires=['requests', 'click'],
    include_package_data=True,
)
