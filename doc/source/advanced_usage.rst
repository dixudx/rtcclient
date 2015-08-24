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

Here are several examples.

**Example 1**: Query all the defects with tags "bvt" whose state is not "Closed"

Note: here defects' state "default_workflow.state.s1" means "Closed".

    >>> query_str = 'dc:type="defect" and rtc_cm:state!="default_workflow.state.s1" and dc:subject="bvt"'

**Example 2**: Query all the defects which are modified after 18:42:30 on Dec. 02, 2008

Note: here defects' state "default_workflow.state.s1" means "Closed".

    >>> query_str = 'dc:type="defect" and dc:modified>="12-02-2008T18:42:30"'

.. [2] `Change Management Query Syntax <http://open-services.net/bin/view/Main/CmQuerySyntaxV1>`_
