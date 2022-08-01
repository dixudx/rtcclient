#!/usr/bin/env python
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages

CLIENT_VERSION = "0.8.3"
PACKAGE_NAME = "rtcclient"
DEVELOPMENT_STATUS = "5 - Production/Stable"


def readme():
    with open('README.rst') as f:
        return f.read()


with open('requirements.txt') as f:
    REQUIRES = f.read().splitlines()

with open('test-requirements.txt') as f:
    TESTS_REQUIRES = f.read().splitlines()

setup(
    name=PACKAGE_NAME,
    version=CLIENT_VERSION,
    description="RTCClient for Rational Team Concert",
    author_email="stephenhsu90@gmail.com",
    author="Di Xu",
    license="Apache License Version 2.0",
    url="https://github.com/dixudx/rtcclient",
    keywords=["rtcclient", "Rational Team Concert", "RTC"],
    install_requires=REQUIRES,
    tests_require=TESTS_REQUIRES,
    packages=find_packages(exclude=['tests.*', 'tests']),
    include_package_data=True,
    long_description=readme(),
    python_requires='>=3.6',
    classifiers=[
        "Development Status :: %s" % DEVELOPMENT_STATUS,
        "Topic :: Utilities",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
