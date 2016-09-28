.. _quickstart:

Quick Start
===========

Eager to get started? This page gives a good introduction in how to get started
with rtcclient.

First, make sure that:

* rtcclient is :ref:`installed <install>`
* rtcclient is up-to-date


RTCClient is intended to map the objects in RTC (e.g. Project Areas,
Team Areas, Workitems) into easily managed Python objects

Let's get started with some simple examples.


Setup Logging
-------------

You can choose to enable logging during the using of rtcclient. Default logging
is for console output. You can also add your own `logging.conf` to store all
the logs to your specified files.

    >>> from rtcclient.utils import setup_basic_logging
    # you can remove this if you don't need logging
    >>> setup_basic_logging()


Add a Connection to the RTC Server
----------------------------------

Adding a connection with RTC Server is very simple.

Begin by importing the `RTCClient` module::

    >>> from rtcclient import RTCClient

Now, let's input the url, username and password of this to-be-connected
RTC Server. For this example,

    >>> url = "https://your_domain:9443/jazz"
    >>> username = "your_username"
    >>> password = "your_password"
    >>> myclient = RTCClient(url, username, password)

If your url ends with **ccm**, set `ends_with_jazz` to `False`,
refer to **issue #68** for detailed explanation.

About Proxies
-------------

If your RTC Server is behind a proxy, you need to set `proxies` explicitly.

HTTP Proxies
~~~~~~~~~~~~

    >>> url = "https://your_domain:9443/jazz"
    >>> username = "your_username"
    >>> password = "your_password"
    # example http proxy
    >>> proxies = {
            'http': 'http://10.10.1.10:3128',
            'https': 'http://10.10.1.10:1080',
        }
    >>> myclient = RTCClient(url, username, password, proxies=proxies)

SOCKS Proxies
~~~~~~~~~~~~
In addition to basic HTTP proxies, proxies using the SOCKS protocol are also
supported.

    >>> url = "https://your_domain:9443/jazz"
    >>> username = "your_username"
    >>> password = "your_password"
     # example socks proxy
    >>> proxies = {
            "http": "socks5://127.0.0.1:1080",
            "https": "socks5://user:pass@host:port"
        }
    >>> myclient = RTCClient(url, username, password, proxies=proxies)


Get a Workitem
--------------

You can get a workitem by calling
:class:`rtcclient.workitem.Workitem.getWorkitem`. The attributes of a workitem
can be accessed through **dot notation** and **dictionary**.

Some common attributes are listed in
:ref:`Built-in Attributes <workitemattrs_table>`.

For example,

    >>> wk = myclient.getWorkitem(123456)
    # get a workitem whose id is 123456
    # this also works: getting the workitem using the equivalent string
    >>> wk2 = myclient.getWorkitem("123456")
    # wk equals wk2
    >>> wk == wk2
    True
    >>> wk
    <Workitem 123456>
    >>> str(wk)
    '141488'
    >>> wk.identifier
    u'141488'
    # access the attributes through dictionary
    >>> wk["title"]
    u'title demo'
    # access the attributes through dot notation
    >>> wk.title
    u'title demo'
    >>> wk.state
    u'Closed'
    >>> wk.description
    u'demo description'
    >>> wk.creator
    u'tester1@email.com'
    >>> wk.created
    u'2015-07-16T08:02:30.658Z'
    >>> wk.comments
    [u'comment test 0', u'add comment test 1', u'add comment test 2']


About Returned Properties
-------------------------

You can also customize your preferred properties to be returned
by specifying **returned_properties** when the called methods have
this optional parameter, which can also **GREATLY IMPROVE** the performance
of this client especially when getting or querying lots of workitems.

For the meanings of these attributes, please refer to
:ref:`Built-in Attributes <workitemattrs_table>`.

Important Note: **returned_properties** is an advanced parameter, the
returned properties can be found in `instance_obj.field_alias.values()`,
e.g. `myworkitem1.field_alias.values()`. If you don't care the performance,
just leave it alone with `None`.

.. _field_alias:

    >>> import pprint
    # print the field alias
    >>> pprint.pprint(wk2.field_alias, width=1)
    {u'affectedByDefect': u'calm:affectedByDefect',
     u'affectsExecutionResult': u'calm:affectsExecutionResult',
     u'affectsPlanItem': u'calm:affectsPlanItem',
     u'apply_step': u'rtc_cm:apply_step',
     u'archived': u'rtc_cm:archived',
     u'blocksTestExecutionRecord': u'calm:blocksTestExecutionRecord',
     u'comments': u'rtc_cm:comments',
     u'contextId': u'rtc_cm:contextId',
     u'correctedEstimate': u'rtc_cm:correctedEstimate',
     u'created': u'dc:created',
     u'creator': u'dc:creator',
     u'description': u'dc:description',
     u'due': u'rtc_cm:due',
     u'elaboratedByArchitectureElement': u'calm:elaboratedByArchitectureElement',
     u'estimate': u'rtc_cm:estimate',
     u'filedAgainst': u'rtc_cm:filedAgainst',
     u'foundIn': u'rtc_cm:foundIn',
     u'identifier': u'dc:identifier',
     u'implementsRequirement': u'calm:implementsRequirement',
     u'modified': u'dc:modified',
     u'modifiedBy': u'rtc_cm:modifiedBy',
     u'ownedBy': u'rtc_cm:ownedBy',
     u'plannedFor': u'rtc_cm:plannedFor',
     u'priority': u'oslc_cm:priority',
     u'progressTracking': u'rtc_cm:progressTracking',
     u'projectArea': u'rtc_cm:projectArea',
     u'relatedChangeManagement': u'oslc_cm:relatedChangeManagement',
     u'relatedExecutionRecord': u'calm:relatedExecutionRecord',
     u'relatedRequirement': u'calm:relatedRequirement',
     u'relatedTestCase': u'calm:relatedTestCase',
     u'relatedTestPlan': u'calm:relatedTestPlan',
     u'relatedTestScript': u'calm:relatedTestScript',
     u'relatedTestSuite': u'calm:relatedTestSuite',
     u'resolution': u'rtc_cm:resolution',
     u'resolved': u'rtc_cm:resolved',
     u'resolvedBy': u'rtc_cm:resolvedBy',
     u'schedule': u'oslc_pl:schedule',
     u'severity': u'oslc_cm:severity',
     u'startDate': u'rtc_cm:startDate',
     u'state': u'rtc_cm:state',
     u'subject': u'dc:subject',
     u'subscribers': u'rtc_cm:subscribers',
     u'teamArea': u'rtc_cm:teamArea',
     u'testedByTestCase': u'calm:testedByTestCase',
     u'timeSheet': u'rtc_cm:timeSheet',
     u'timeSpent': u'rtc_cm:timeSpent',
     u'title': u'dc:title',
     u'trackedWorkItem': u'oslc_cm:trackedWorkItem',
     u'tracksChanges': u'calm:tracksChanges',
     u'tracksRequirement': u'calm:tracksRequirement',
     u'tracksWorkItem': u'oslc_cm:tracksWorkItem',
     u'type': u'dc:type'}

Note: these field aliases may differ due to the type of workitems. But most of
the common-used attributes will stay unchanged.

The `returned_properties` is a string **composed by the above values with
comma separated**.

It will run faster if `returned_properties` is specified. Because the client
will only get/request the attributes you specified.

    >>> returned_properties = "dc:title,dc:identifier,rtc_cm:state,rtc_cm:ownedBy"
    # specify the returned properties: title, identifier, state, owner
    # This is optional. All properties will be returned if not specified
    >>> wk_rp = myclient.getWorkitem(123456,
                                     returned_properties=returned_properties)
    >>> wk_rp.identifier
    u'141488'
    # access the attributes through dictionary
    >>> wk_rp["title"]
    # access the attributes through dot notation
    u'title demo'
    >>> wk_rp.title
    u'title demo'
    >>> wk_rp.state
    u'Closed'
    >>> wk_rp.ownedBy
    u'tester1@email.com'


Add a Comment to a Workitem
---------------------------

After getting the :class:`rtcclient.workitem.Workitem` object, you can add a
comment to this workitem by calling :class:`addComment`.

    >>> mycomment = wk.addComment("add comment test 3")
    >>> mycomment
    <Comment 3>
    >>> mycomment.created
    u'2015-08-22T03:55:00.839Z'
    >>> mycomment.creator
    u'tester1@email.com'
    >>> mycomment.description
    u'add comment test 3'
    >>> str(mycomment)
    '3'


Get all Workitems
-----------------

All workitems can be fetched by calling
:class:`rtcclient.client.RTCClient.getWorkitems`. It will take
a long time to fetch all the workitems in some certain project areas if there
are already many existing workitems.

If both `projectarea_id` and `projectarea_name` are None, all the workitems
in all project areas will be returned.

    >>> workitems_list = myclient.getWorkitems(projectarea_id=None,
                                               projectarea_name=None,
                                               returned_properties=returned_properties)
    # get all workitems in a specific project area
    >>> projectarea_name = "my_projectarea_name"
    >>> workitems_list2 = myclient.getWorkitems(projectarea_name=projectarea_name,
                                                returned_properties=returned_properties)


Query Workitems
---------------

After customizing your query string, all the workitems meet the conditions
will be fetched.

    >>> myquery = myclient.query # query class
    >>> projectarea_name = "my_projectarea_name"
    # customize your query string
    # below query string means: query all the workitems with title "use case 1"
    >>> myquerystr = 'dc:title="use case 1"'
    >>> returned_prop = "dc:title,dc:identifier,rtc_cm:state,rtc_cm:ownedBy"
    >>> queried_wis = myquery.queryWorkitems(myquerystr,
                                             projectarea_name=projectarea_name,
                                             returned_properties=returned_prop)

More detailed and advanced syntax on querying, please refer to
:ref:`query syntax <query_syntax>`.


Query Workitems by Saved Query
------------------------------

You may have created several customized queries through RTC Web GUI or got
some saved queries created by other team members. Using these saved queries

    >>> myquery = myclient.query # query class
    >>> saved_query_url = 'http://test.url:9443/jazz/xxxxxxxx&id=xxxxx'
    >>> projectarea_name = "my_projectarea_name"
    # get all saved queries
    # WARNING: now the RTC server cannot correctly list all the saved queries
    #          It seems to be a bug of RTC. Recommend using `runSavedQueryByUrl` to
    #          query all the workitems if the query is saved.
    >>> allsavedqueries = myquery.getAllSavedQueries(projectarea_name=projectarea_name)
    # saved queries created by tester1@email.com
    >>> allsavedqueries = myquery.getAllSavedQueries(projectarea_name=projectarea_name,
                                                     creator="tester1@email.com")
    # my saved queries
    >>> mysavedqueries = myquery.getMySavedQueries(projectarea_name=projectarea_name)
    >>> mysavedquery = mysavedqueries[0]
    >>> returned_prop = "dc:title,dc:identifier,rtc_cm:state,rtc_cm:ownedBy"
    >>> queried_wis = myquery.runSavedQuery(mysavedquery,
                                            returned_properties=returned_prop)


Query Workitems by Saved Query Url
----------------------------------

You can also query all the workitems directly using your saved query's url.

    >>> myquery = myclient.query # query class
    >>> saved_query_url = 'http://test.url:9443/jazz/xxxxxxxx&id=xxxxx'
    >>> returned_prop = "dc:title,dc:identifier,rtc_cm:state,rtc_cm:ownedBy"
    >>> queried_wis = myquery.runSavedQueryByUrl(saved_query_url,
                                                 returned_properties=returned_prop)
