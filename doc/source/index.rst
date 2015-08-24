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

**IMPORTANT NOTE: THIS IS NOT AN OFFICIAL Python-based RTC Client.**

This library can help you:

* Interacts with an RTC server to retrieve objects which contain the detailed information/configuration, including Project Areas, Team Areas, Workitems, etc
* Creates all kinds of Workitems through self-customized templates or Copies from some existing Workitems
* Add comments to the retrieved Workitems
* Query Workitems using specified filtered rules
* Logs all the activities and messages during your operation


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
