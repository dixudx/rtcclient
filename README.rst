rtcclient
=========

.. image:: https://readthedocs.org/projects/rtcclient/badge/?version=latest
    :target: https://readthedocs.org/projects/rtcclient

.. image:: https://img.shields.io/pypi/v/rtcclient.svg
    :target: https://pypi.python.org/pypi/rtcclient

.. image:: https://api.travis-ci.org/dixudx/rtcclient.svg?branch=master
    :target: https://pypi.python.org/pypi/rtcclient

.. image:: https://img.shields.io/badge/slack-rtcclient-blue.svg
    :target: https://rtcclient.slack.com

.. image:: https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg
    :target: https://saythanks.io/to/dixudx

A Python-based Client/API for Rational Team Concert (RTC)

About this library
------------------

IBM® Rational Team Concert™, is built on the Jazz platform, allowing
application development teams to use one tool to plan across teams, code,
run standups, plan sprints, and track work. For more info, please refer
to here_.

.. _here: http://www.ibm.com/developerworks/downloads/r/rtc/

**IMPORTANT NOTE: This is NOT an official-released Python-based RTC Client.**

This library can help you:

* Interacts with an RTC server to retrieve objects which contain the detailed information/configuration, including **Project Areas**, **Team Areas**, **Workitems** and etc;
* Creates all kinds of **Workitems** through self-customized templates or copies from some existing **Workitems**;
* Performs some actions on the retrieved **Workitems**, including get/add **Comments**, get/add/remove **Subscribers**/**Children**/**Parent**, get/upload **Attachments** and etc;
* Query **Workitems** using specified filtered rules or directly from your saved queries;
* Logs all the activities and messages during your operation;


Python & Rational Team Concert Versions
---------------------------------------

This project has been tested against multiple Python versions, such as 2.7, 3.5, 3.6, 3.7, 3.8 and 3.9.

Currently the newest release of **rtcclient** is **0.7.0**, which works well with ``Rational Team Concert`` 6.0.6.1 and ``ELM`` 7.0.

For ``Rational Team Concert`` with version **5.0.1**, **5.0.2**, it is suggested to install **rtcclient** with version **0.6.0**.

Important Links
---------------

Support and bug-reports:
https://github.com/dixudx/rtcclient/issues?q=is%3Aopen+sort%3Acomments-desc

Project source code: https://github.com/dixudx/rtcclient

Project documentation: https://readthedocs.org/projects/rtcclient/


Installation
------------

To install rtcclient, simply:

.. code-block:: bash

    $ pip install rtcclient


Example
-------

RTCClient is intended to map the objects in RTC (e.g. Project Areas,
Team Areas, Workitems) into easily managed Python objects:

.. code-block:: python

    >>> from rtcclient.utils import setup_basic_logging
    >>> from rtcclient import RTCClient
    # you can remove this if you don't need logging
    # default debug logging for console output
    >>> setup_basic_logging()
    # url ends with jazz
    >>> url = "https://your_domain:9443/jazz"
    >>> username = "your_username"
    >>> password = "your_password"
    # if your rtc server is behind a proxy, remember to set "proxies"
    # explicitly. detailed can be found in quick start of the doc
    # if your url ends with ccm, set ends_with_jazz to False
    # refer to issue #68 for detailed explanation
    >>> myclient = RTCClient(url, username, password, ends_with_jazz=True)
    # it will be faster if returned properties is specified
    # see in below query example
    >>> wk = myclient.getWorkitem(123456) # get a workitem whose id is 123456
    # get all workitems
    # If both projectarea_id and projectarea_name are None, all the workitems
    # in all ProjectAreas will be returned
    >>> workitems_list = myclient.getWorkitems(projectarea_id=None,
                                               projectarea_name=None)
    >>> myquery = myclient.query # query class
    >>> projectarea_name = "your_projectarea_name"
    # customize your query string
    # below query string means: query all the workitems with title "use case 1"
    >>> myquerystr = 'dc:title="use case 1"'
    # specify the returned properties: title, id, state, owner
    # This is optional. All properties will be returned if not specified
    >>> returned_prop = "dc:title,dc:identifier,rtc_cm:state,rtc_cm:ownedBy"
    >>> queried_wis = myquery.queryWorkitems(query_str=myquerystr,
                                             projectarea_name=projectarea_name,
                                             returned_properties=returned_prop)


Testing
-------

Using a virtualenv is recommended. Setuptools will automatically fetch
missing test dependencies.

If you have installed the tox_ on your system already, you can run
the tests using pytest_ with the following command:

.. _tox: https://pypi.python.org/pypi/tox
.. _pytest: http://pytest.org/latest/

.. code-block:: bash

    virtualenv
    source .venv/bin/active
    (venv) tox -e test
    (venv) tox -e flake
    (venv) tox -e pycodestyle
