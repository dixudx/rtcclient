.. _advanced_usage:


Advanced Usage
==============

This document covers some of rtcclient more advanced features.


.. _query_syntax:

Query Syntax [2]_
-----------------

The following section describes the basic query syntax.


**Comparison Operators**

* ``=`` : test for equality of a term,
* ``!=`` : test for inequality of a term,
* ``<`` : test less-than,
* ``>`` : test greater-than,
* ``<=`` : test less-than or equal,
* ``>=`` : test greater-than or equal,
* ``in`` : test for equality of any of the terms.


**Boolean Operators**

* ``and`` : conjunction


**Query Modifiers**

* ``/sort`` : set the sort order for returned items


**BNF**

::

    query      ::= (term (boolean_op term)*)+ modifiers
    term       ::= (identifier operator)? value+ | (identifier "in")? in_val
    operator   ::= "=" | "!=" | "<" | ">" | "<=" | ">="
    boolean_op ::= "and"
    modifiers  ::= sort?
    sort       ::= "/sort" "=" identifier
    identifier ::= word (":" word)?
    in_val     ::= "[" value ("," value)* "]"
    value      ::= (integer | string)
    word       ::= /any sequence of letters and numbers, starting with a letter/
    string     ::= '"' + /any sequence of characters/ + '"'
    integer    ::= /any sequence of integers/


**Notes**

1. a word consists of any character with the Unicode class Alpha (alpha-numeric) as well as the characters ".", "-" and "_".
2. a string may include the quote character if preceded by the escape character "\", as in "my \"quoted\" example".


.. _query_compose:

Compose your Query String
-------------------------

Based on the above :ref:`query syntax <query_syntax>`, it is easy to compose
your own query string.

**Important Note**: For the `identifier` in :ref:`query syntax <query_syntax>`, please refer
to :ref:`field alias <field_alias>` and
:ref:`Built-in Attributes <workitemattrs_table>`.

Here are several examples.

**Example 1**: Query all the defects with tags "bvt" whose state is not "Closed"

Note: here defects' state "default_workflow.state.s1" means "Closed". This
may vary in your customized workitem type.

    >>> query_str = ('dc:type="defect" and '
                     'rtc_cm:state!="default_workflow.state.s1" and '
                     'dc:subject="bvt"')

**Example 2**: Query all the defects which are modified after 18:42:30 on Dec. 02, 2008

Note: here defects' state "default_workflow.state.s1" means "Closed".

    >>> query_str = 'dc:type="defect" and dc:modified>="12-02-2008T18:42:30"'

**Example 3**: Query all the defects with tags "bvt" or "testautomation"

    >>> query_str = 'dc:type="defect" and dc:subject in ["bvt", "testautomation"]'

**Example 4**: Query all the defects owned/created/modified by "tester@email.com"

    >>> user_url = "https://your_domain:9443/jts/users/tester@email.com"
    >>> query_str = 'dc:type="defect" and rtc_cm:ownedBy="%s"' % user_url
    >>> query_str = 'dc:type="defect" and dc:creator="%s"' % user_url
    >>> query_str = 'dc:type="defect" and rtc_cm:modifiedBy="%s"' % user_url

Note: please replace `your_domain` with your actual RTC server domain.

**Example 5**: Query all the defects whose severity are "Critical"

    >>> projectarea_name="My ProjectArea"
    >>> severity = myclient.getSeverity("Critical",
                                        projectarea_name=projectarea_name)
    >>> query_str = 'dc:type="defect" and oslc_cm:severity="%s"' % severity.url

**Example 6**: Query all the defects whose priority are "High"

    >>> projectarea_name="My ProjectArea"
    >>> priority = myclient.getPriority("High",
                                        projectarea_name=projectarea_name)
    >>> query_str = 'dc:type="defect" and oslc_cm:priority="%s"' % priority.url

**Example 7**: Query all the defects whose FiledAgainst are "FiledAgainstDemo"

    >>> projectarea_name="My ProjectArea"
    >>> filedagainst = myclient.getFiledAgainst("FiledAgainstDemo",
                                                projectarea_name=projectarea_name)
    >>> query_str = 'dc:type="defect" and rtc_cm:filedAgainst="%s"' % filedagainst.url

.. [2] `Change Management Query Syntax <http://open-services.net/bin/view/Main/CmQuerySyntaxV1>`_
