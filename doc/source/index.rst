.. rtcclient documentation master file, created by
   sphinx-quickstart on Mon Aug 17 17:21:28 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to rtcclient's documentation!
=====================================

IBM® Rational Team Concert™, is built on the Jazz platform, allowing
application development teams to use one tool to plan across teams, code,
run standups, plan sprints, and track work. For more info, please refer
to here_.

.. _here: http://www.ibm.com/developerworks/downloads/r/rtc/

**IMPORTANT NOTE: This is NOT an official-released Python-based RTC Client.**

This library can help you:

* Interacts with an RTC server to retrieve objects which contain the detailed information/configuration, including **Project Areas**, **Team Areas**, **Workitems** and etc;
* Creates all kinds of **Workitems** through self-customized templates or copies from some existing **Workitems**;
* Performs some actions on the retrieved **Workitems**, including get/add **Comments**, get/add/remove **Subscribers**/**Children**/**Parent** and etc;
* Query **Workitems** using specified filtered rules or directly from your saved queries;
* Logs all the activities and messages during your operation;


Python & Rational Team Concert Versions
---------------------------------------

This project has been tested against multiple Python versions, such as 2.7, 3.5, 3.6, 3.7, 3.8 and 3.9.

Currently the newest release of **rtcclient** is **0.7.0**, which works well with ``Rational Team Concert`` 6.0.6.1 and ``ELM`` 7.0.

For ``Rational Team Concert`` with version **5.0.1**, **5.0.2**, it is suggested to install **rtcclient** with version **0.6.0**.

Important Links
---------------

* Support and bug-reports: https://github.com/dixudx/rtcclient/issues?q=is%3Aopen+sort%3Acomments-desc

* Project source code: https://github.com/dixudx/rtcclient

* Project documentation: https://readthedocs.org/projects/rtcclient/


User Guide
==========

.. toctree::
   :maxdepth: 2

   authors
   introduction
   workitem_attr
   installation
   quickstart
   advanced_usage


API Documentation
=================

.. toctree::
   :maxdepth: 2

   client
   projectarea
   workitem
   query
   template
   models


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
