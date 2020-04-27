#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages


setup(
    name='wazo-calld-conference',
    version='0.0.2',
    description='Wazo extend API conference for calld',
    author='Sylvain Boily',
    author_email='sylvain@wazo.io',
    url='http://www.wazo.io/',
    license='GPLv3',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'wazo_calld_conference': ['api.yml'],
    },
    entry_points={
        'wazo_calld.plugins': [
            'conference_ext = wazo_calld_conference.plugin:Plugin'
        ],
    },
)
