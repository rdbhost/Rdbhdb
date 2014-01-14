#!/usr/bin/env python

import sys
import os
from distutils.core import setup


setup(name="rdbhdb",
      version='0.9.6',
      description="DB API module for accessing hosted databases at www.rdbhost.com",
      author='David Keeney, Kris Sundaram',
      author_email='dkeeney@rdbhost.com, sundram@hotmail.com',
      maintainer='David Keeney',
      maintainer_email='dkeeney@rdbhost.com',
      url='http://www.rdbhost.com/',
      package_dir={'rdbhdb':'lib/rdbhdb'},
      install_requires=['urllib3 >= 1.5'],
      extras_require={'asyncio': ['asyncio', 'aiohttp']},
      packages=['rdbhdb'],
      long_description="""
      Rdbhost hosts PostgreSQL databases, queried through HTTP 
      (it is a web service). This module provides a DB API 2 API 
      to access rdbhost.com hosted databases from your application.
      Uses gzip compression to conserve bandwidth and time. Can
      be used on Google Appengine or any other Python platform.
      Starting with version 0.9.6, supports asyncio.
      """,
      classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 2',
      'Programming Language :: Python :: 3',
#      'Framework :: Asyncio',
      ],
      license='MIT'
     )
