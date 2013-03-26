# -*- coding: UTF-8 -*-
"""
@author: Yangminghua
@version: $
"""
from distutils.core import setup
import py2exe
import sys

setup(
    service=['BrokerService'],
    options={
        'py2exe': {'includes': 'decimal','bundle_files':1
        }},
    zipfile=None,
    data_files=[(".", ["config.ini"])]

)