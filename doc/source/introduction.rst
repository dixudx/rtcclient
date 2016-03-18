.. _introduction:

Introduction
============

In this section, some common terminologies are introduced. For more information,
please visit `Rational Collaborative Lifecycle Management Solution <http://www-01.ibm.com/support/knowledgecenter/SSYMRC_5.0.2/com.ibm.rational.clm.doc/helpindex_clm.html>`_


Project Area
------------

Project Area is, quite simply, an area in the repository where information
about the project is stored.

In each of the Collaborative Lifecycle Management (CLM) applications,
teams perform their work within the context of a project area.
A project area is an area in the repository where information about one
or more software projects is stored. **A project area defines the project
deliverables, team structure, process, and schedule**. You access all project
artifacts, such as iteration plans, work items, requirements, test cases,
and files under source control within the context of a project area.
Each project area has a process, which governs how members work.

For example, the project area process defines:

* User roles
* Permissions assigned to roles
* Timelines and iterations
* Operation behavior (preconditions and follow-up actions) for Change and Configuration Management and Quality Management
* Work item types and their state transition models (for Change and Configuration Management and Quality Management)

A project area is stored as a top-level or root item in a repository.
A project area references project artifacts and stores the relationships
between these artifacts. Access to a project area and its artifacts is
controlled by access control settings and permissions. A project area
cannot be deleted from the repository; however, it can be archived,
which places it in an inactive state.


Team Area
---------

You can create a team area to assign users in particular roles for work on a
timeline or a particular set of deliverables. You can create a team area
within an existing project area or another team area to establish a team
hierarchy.


Component [3]_
--------------

A configuration or set of configurations may be divided into components
representing some user-defined set of object versions and/or
sub-configurations; for example, components might be used to represent
physical components or software modules. A provider is not required to
implement components; they are used only as a way of limiting the scope of
the closure over links. Components might or might not be resources; they
might be dynamic sets of object versions chosen by other criteria such as
property values. A provider can also treat each configuration and
sub-configuration in a hierarchy as being separate components.


Change set [3]_
---------------

A set of changes to be made to one or more configurations, where each
change is described in terms of members (direct or indirect) that should
be added to, replaced in, or removed from some configurations.


Role
----

Each project area and each team area can define a set of roles.
The defined roles are visible in the area where they're declared and in all
child areas. Roles defined in the project area can be assigned to users for the
whole project area or they can be assigned in any team area. Roles defined in
a team area can similarly be assigned in that team or in any child team.
The ordering of roles in this section determines how they will be ordered in
other sections of the editor, but it does not affect the process runtime.


Administrator
-------------

If you require permissions, contact an administrator.
Project administrators can modify and save this project area and its team areas.


PlannedFor
----------

In modern software development, a release is divided into a series of
fixed-length development periods, typically ranging from two to six weeks,
called iterations. Planning an iteration involves scheduling the work to be
done during an iteration and assigning individual work items to members of the
team.

Iteration planning takes place in the context of a project area.
Each project area has a development line that is divided into development
phases or iterations. For each iteration, you can create an iteration plan.

The project `plannedfor` defines a start and end date along with an iteration
breakdown.


Workitem
--------

You can use work items to manage and track not only your work, but also
the work of your team.


Workitem Type
-------------


A workitem type is a classification of work items that has a specific set of
attributes. Each predefined process template includes the work item types that
allow users to work in that process. For example, the Scrum process includes
work item types such as `Epic`, `Story`, `Adoption Item`, `Task`, and
`Retrospective`, which support an agile development model. The Formal Project
Management process, which supports a more traditional development model,
includes workitem types such as `Project Change Request`, `Business Need`, and
`Risk`. Some work item types, such as `Defect` and `Task`, are used by
multiple processes.


Workitem Type Category
----------------------

Each work item type belongs to a work item category. Multiple work item types
can belong to the same work item category. The work item types of a work item
type category share workflow and custom attributes.
When you create a work item type, you must associate it with a category.
If you intend to define a unique workflow for the new work item type,
create a new category and associate it with the work item type.
Otherwise, you can associate the work item type with an existing category.

.. [3] `SCM Data Model <http://open-services.net/bin/view/Main/CmQuerySyntaxV1>`_
