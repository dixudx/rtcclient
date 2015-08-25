.. _workitemattrs:

Workitem Attributes [1]_
========================

Attributes identify the information that you want to capture when users create
and modify work items. Attributes are similar to fields in records. Work item
types include all the built-in attributes that are listed in below Table.
Note, however, that not every ready-to-use work item presentation is configured
to display all of the built-in attributes in the Rational Team Concert™ Eclipse
and web clients. You can customize the attributes that a work item type
contains and the presentations that are used to display these attributes.
For example, you can customize attributes to add behavior. Such behaviors can
include validating an attribute value, or setting an attribute value that is
based on other attribute values.

All the attributes of the :class:`rtcclient.workitem.Workitem` can be accessed
through **dot notation** and **dictionary**.


.. _workitemattrs_table:

Built-in Attributes
-------------------

Table1. Built-in Attributes

+--------------------+-------------+-------------------+----------------------------------------------+
| Name               | Type        | ID                | Description                                  |
+====================+=============+===================+==============================================+
| Archived           | Boolean     | archived          | Specifies whether the work item is archived. |
+--------------------+-------------+-------------------+----------------------------------------------+
| Comments           | Comments    | comments          | Comments about the work item.                |
+--------------------+-------------+-------------------+----------------------------------------------+
| Corrected Estimate | Duration    | correctedEstimate | Correction to the original time estimate     |
|                    |             |                   | (as specified by the Estimate attribute) to  |
|                    |             |                   | resolve the work item.                       |
+--------------------+-------------+-------------------+----------------------------------------------+
| Created By         | Contributor | creator           | User who created the work item.              |
+--------------------+-------------+-------------------+----------------------------------------------+
| Creation Date      | Timestamp   | created           | Date when the work item was created.         |
+--------------------+-------------+-------------------+----------------------------------------------+
| Description        | Large HTML  | description       | Detailed description of the work item.       |
|                    |             |                   | For example, the description for a defect    |
|                    |             |                   | might include a list of steps to follow to   |
|                    |             |                   | reproduce the defect. Any descriptions that  |
|                    |             |                   | are longer than 32 KB are truncated, and the |
|                    |             |                   | entire description is added as an attachment.|
+--------------------+-------------+-------------------+----------------------------------------------+
| Due Date           | Timestamp   | due               | Date by which the resolution of the work     |
|                    |             |                   | item is due.                                 |
+--------------------+-------------+-------------------+----------------------------------------------+
| Estimate           | Duration    | estimate          | Estimated amount of time that it takes to    |
|                    |             |                   | resolve the work item.                       |
+--------------------+-------------+-------------------+----------------------------------------------+
| Filed Against      | Category    | filedAgainst      | Category that identifies the component or    |
|                    |             |                   | functional area that the work item belongs   |
|                    |             |                   | to. For example, your project might have GUI,|
|                    |             |                   | Build, and Documentation categories.         |
|                    |             |                   | Each category is associated with a team area;|
|                    |             |                   | that team is responsible for responding to   |
|                    |             |                   | the work item.                               |
+--------------------+-------------+-------------------+----------------------------------------------+
| Found In           | Deliverable | foundIn           | Release in which the issue described in the  |
|                    |             |                   | work item was identified.                    |
+--------------------+-------------+-------------------+----------------------------------------------+
| Id                 | Integer     | identifier        | Identification number that is associated     |
|                    |             |                   | with the work item.                          |
+--------------------+-------------+-------------------+----------------------------------------------+
| Modified By        | Contributor | modifiedBy        | User who last modified the work item.        |
+--------------------+-------------+-------------------+----------------------------------------------+
| Modified Date      | Timestamp   | modified          | Date when the work item was last modified.   |
+--------------------+-------------+-------------------+----------------------------------------------+
| Owned By           | Contributor | ownedBy           | Owner of the work item.                      |
+--------------------+-------------+-------------------+----------------------------------------------+
| Planned For        | Iteration   | plannedFor        | Iteration for which the work item is planned.|
+--------------------+-------------+-------------------+----------------------------------------------+
| Priority           | Priority    | priority          | Ranked importance of a work item. For        |
|                    |             |                   | example, `Low`, `Medium`, or `High`.         |
+--------------------+-------------+-------------------+----------------------------------------------+
| Project Area       | ProjectArea | projectArea       | Area in the repository where information     |
|                    |             |                   | about the project is stored.                 |
+--------------------+-------------+-------------------+----------------------------------------------+
| Resolution         | Small String| resolution        | How the work item was resolved.              |
+--------------------+-------------+-------------------+----------------------------------------------+
| Resolution Date    | Timestamp   | resolved          | Date when the work item was resolved.        |
+--------------------+-------------+-------------------+----------------------------------------------+
| Resolved By        | Contributor | resolvedBy        | User who resolved the work item.             |
+--------------------+-------------+-------------------+----------------------------------------------+


Table2. Built-in Attributes (cont'd)

+--------------------+-------------+-------------------+----------------------------------------------+
| Name               | Type        | ID                | Description                                  |
+====================+=============+===================+==============================================+
| Restricted Access  | UUID        | contextId         | Scope of access to the work item.            |
+--------------------+-------------+-------------------+----------------------------------------------+
| Severity           | Severity    | severity          | Indication of the impact of the work item.   |
|                    |             |                   | For example, `Minor`, `Normal`, `Major`, or  |
|                    |             |                   | `Critical`.                                  |
+--------------------+-------------+-------------------+----------------------------------------------+
| Start Date         | Timestamp   | startDate         | Date when work began on the work item.       |
+--------------------+-------------+-------------------+----------------------------------------------+
| Status             | Small String| state             | Status of the work item. For example, `New`, |
|                    |             |                   | `In Progress`, or `Resolved`.                |
+--------------------+-------------+-------------------+----------------------------------------------+
| Subscribed By      |Subscriptions| subscribers       | Users who are subscribed to the work item.   |
+--------------------+-------------+-------------------+----------------------------------------------+
| Summary            | Medium HTML | title             | Brief headline that identifies the work item.|
+--------------------+-------------+-------------------+----------------------------------------------+
| Tags               | Tag         | subject           | Tags that are used for organizing and        |
|                    |             |                   | querying on work items.                      |
+--------------------+-------------+-------------------+----------------------------------------------+
| Time Spent         | Duration    | timeSpent         | Length of time that was spent to resolve the |
|                    |             |                   | work item.                                   |
+--------------------+-------------+-------------------+----------------------------------------------+
| Type               | Type        | type              | Type of work item. Commonly available types  |
|                    |             |                   | are `Defect`, `Task`, and `Story`.           |
+--------------------+-------------+-------------------+----------------------------------------------+

.. [1] `Workitem Customization Overview <http://www-01.ibm.com/support/knowledgecenter/api/content/nl/en-us/SSYMRC_5.0.2/com.ibm.team.workitem.doc/topics/c_work_item_customization_overview.html>`_
