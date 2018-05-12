#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages


setup(
    name='wazo-ctid-conference',
    version='0.0.1',
    description='Wazo CTI conference',
    author='Sylvain Boily',
    author_email='sylvain@wazo.io',
    url='http://www.wazo.io/',
    license='GPLv3',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'wazo_ctid_conference': ['api.yml'],
    },
    entry_points={
        'xivo_ctid_ng.plugins': [
            'conference = wazo_ctid_conference.plugin:Plugin'
        ],
    },
)
