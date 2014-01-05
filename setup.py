#!/usr/bin/env python

import sys
import os
from distutils.core import setup


setup(name="rdbhdb",
      version='0.9.5',
      description="DB API module for accessing hosted databases at www.rdbhost.com",
      author='David Keeney, Kris Sundaram',
      author_email='dkeeney@rdbhost.com, sundram@hotmail.com',
      maintainer='David Keeney',
      maintainer_email='dkeeney@rdbhost.com',
      url='http://www.rdbhost.com/',
      package_dir={'rdbhdb':'lib'},
      install_requires=['urllib3 >= 1.5'],
      packages=['rdbhdb'],
      long_description="""
      Rdbhost hosts PostgreSQL databases, queried through HTTP 
      (it is a web service). This module provides a DB API 2 API 
      to access rdbhost.com hosted databases from your application.
      Uses gzip compression to conserve bandwidth and time. Can
      be used on Google Appengine or any other Python platform.      
      """,
      classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License (GPL)',
      'Programming Language :: Python :: 2',
      'Programming Language :: Python :: 3',
      ]
     )
