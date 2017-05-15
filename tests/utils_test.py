import os
import xmltodict
from rtcclient import OrderedDict


_path = os.path.realpath(os.path.dirname(__file__))
_search_path = os.path.join(_path, 'fixtures')


def read_fixture(file_name):
    file_path = os.path.join(_search_path, file_name)
    with open(file_path, mode="r") as fh:
        return fh.read()


pa1 = (xmltodict.parse(read_fixture("projectareas.xml"))
                .get("oslc_cm:Collection")
                .get("rtc_cm:Project")[0])


pa2 = (xmltodict.parse(read_fixture("projectareas.xml"))
                .get("oslc_cm:Collection")
                .get("rtc_cm:Project")[1])


ta1 = (xmltodict.parse(read_fixture("teamareas.xml"))
                .get("oslc_cm:Collection")
                .get("rtc_cm:Team")[0])

ta2 = (xmltodict.parse(read_fixture("teamareas.xml"))
                .get("oslc_cm:Collection")
                .get("rtc_cm:Team")[1])

plannedfor1 = (xmltodict.parse(read_fixture("plannedfors.xml"))
                        .get("oslc_cm:Collection")
                        .get("rtc_cm:Iteration")[0])

plannedfor2 = (xmltodict.parse(read_fixture("plannedfors.xml"))
                        .get("oslc_cm:Collection")
                        .get("rtc_cm:Iteration")[1])

severity1 = (xmltodict.parse(read_fixture("severities.xml"))
                      .get("oslc_cm:Collection")
                      .get("rtc_cm:Literal")[0])

severity2 = (xmltodict.parse(read_fixture("severities.xml"))
                      .get("oslc_cm:Collection")
                      .get("rtc_cm:Literal")[1])

priority1 = (xmltodict.parse(read_fixture("priorities.xml"))
                      .get("oslc_cm:Collection")
                      .get("rtc_cm:Literal")[0])

priority2 = (xmltodict.parse(read_fixture("priorities.xml"))
                      .get("oslc_cm:Collection")
                      .get("rtc_cm:Literal")[1])

foundin1 = (xmltodict.parse(read_fixture("foundins.xml"))
                     .get("oslc_cm:Collection")
                     .get("rtc_cm:Deliverable")[0])

foundin2 = (xmltodict.parse(read_fixture("foundins.xml"))
                     .get("oslc_cm:Collection")
                     .get("rtc_cm:Deliverable")[1])

filedagainst1 = (xmltodict.parse(read_fixture("filedagainsts.xml"))
                          .get("oslc_cm:Collection")
                          .get("rtc_cm:Category")[0])

filedagainst2 = (xmltodict.parse(read_fixture("filedagainsts.xml"))
                          .get("oslc_cm:Collection")
                          .get("rtc_cm:Category")[1])

workitem1 = (xmltodict.parse(read_fixture("workitems.xml"))
                      .get("oslc_cm:Collection")
                      .get("oslc_cm:ChangeRequest")[0])

workitem1_origin = OrderedDict()
workitem1_origin["oslc_cm:ChangeRequest"] = workitem1
workitem1_raw = xmltodict.unparse(workitem1_origin)

workitem2 = (xmltodict.parse(read_fixture("workitems.xml"))
                      .get("oslc_cm:Collection")
                      .get("oslc_cm:ChangeRequest")[1])
workitem2_origin = OrderedDict()
workitem2_origin["oslc_cm:ChangeRequest"] = workitem2
workitem2_raw = xmltodict.unparse(workitem2_origin)

template_name = "issue_example.template"
template_raw = read_fixture(template_name)
template_ordereddict = xmltodict.parse(template_raw)

member1 = (xmltodict.parse(read_fixture("members.xml"))
                    .get("oslc_cm:Collection")
                    .get("rtc_cm:User")[0])

member2 = (xmltodict.parse(read_fixture("members.xml"))
                    .get("oslc_cm:Collection")
                    .get("rtc_cm:User")[1])

member3 = (xmltodict.parse(read_fixture("members.xml"))
                    .get("oslc_cm:Collection")
                    .get("rtc_cm:User")[2])

itemtype1 = (xmltodict.parse(read_fixture("itemtypes.xml"))
                      .get("oslc_cm:Collection")
                      .get("rtc_cm:Type")[0])

itemtype2 = (xmltodict.parse(read_fixture("itemtypes.xml"))
                      .get("oslc_cm:Collection")
                      .get("rtc_cm:Type")[1])

admin = (xmltodict.parse(read_fixture("administrators.xml"))
                  .get("oslc_cm:Collection")
                  .get("rtc_cm:User"))

comment1 = (xmltodict.parse(read_fixture("comments.xml"))
                     .get("oslc_cm:Collection")
                     .get("rtc_cm:Comment")[0])

comment2 = (xmltodict.parse(read_fixture("comments.xml"))
                     .get("oslc_cm:Collection")
                     .get("rtc_cm:Comment")[1])

action1 = (xmltodict.parse(read_fixture("actions.xml"))
                    .get("oslc_cm:Collection")
                    .get("rtc_cm:Action")[0])

action2 = (xmltodict.parse(read_fixture("actions.xml"))
                    .get("oslc_cm:Collection")
                    .get("rtc_cm:Action")[1])

role1 = (xmltodict.parse(read_fixture("roles.xml"))
                  .get("jp06:roles")
                  .get("jp06:role")[0])

role2 = (xmltodict.parse(read_fixture("roles.xml"))
                  .get("jp06:roles")
                  .get("jp06:role")[1])

role3 = (xmltodict.parse(read_fixture("roles.xml"))
                  .get("jp06:roles")
                  .get("jp06:role")[2])

state1 = (xmltodict.parse(read_fixture("states.xml"))
                   .get("oslc_cm:Collection")
                   .get("rtc_cm:Status")[0])

state2 = (xmltodict.parse(read_fixture("states.xml"))
                   .get("oslc_cm:Collection")
                   .get("rtc_cm:Status")[1])

savedquery1 = (xmltodict.parse(read_fixture("savedqueries.xml"))
                        .get("oslc_cm:Collection")
                        .get("rtc_cm:Query")[0])

savedquery2 = (xmltodict.parse(read_fixture("savedqueries.xml"))
                        .get("oslc_cm:Collection")
                        .get("rtc_cm:Query")[1])

savedquery3 = (xmltodict.parse(read_fixture("savedqueries.xml"))
                        .get("oslc_cm:Collection")
                        .get("rtc_cm:Query")[2])

includedinbuild1 = (xmltodict.parse(read_fixture("includedinbuilds.xml"))
                             .get("oslc_cm:Collection")
                             .get("oslc_auto:AutomationResult")[0])

includedinbuild2 = (xmltodict.parse(read_fixture("includedinbuilds.xml"))
                             .get("oslc_cm:Collection")
                             .get("oslc_auto:AutomationResult")[1])

children1 = (xmltodict.parse(read_fixture("children.xml"))
                      .get("oslc_cm:Collection")
                      .get("oslc_cm:ChangeRequest")[0])

children2 = (xmltodict.parse(read_fixture("children.xml"))
                      .get("oslc_cm:Collection")
                      .get("oslc_cm:ChangeRequest")[1])

parent = (xmltodict.parse(read_fixture("parent.xml"))
                   .get("oslc_cm:Collection")
                   .get("oslc_cm:ChangeRequest"))

changeset1 = (xmltodict.parse(read_fixture("changesets.xml"))
                       .get("oslc_cm:Collection")
                       .get("rtc_cm:Reference")[0])

changeset2 = (xmltodict.parse(read_fixture("changesets.xml"))
                       .get("oslc_cm:Collection")
                       .get("rtc_cm:Reference")[1])

changeset3 = (xmltodict.parse(read_fixture("changesets.xml"))
                       .get("oslc_cm:Collection")
                       .get("rtc_cm:Reference")[2])

attachment1 = (xmltodict.parse(read_fixture("attachment.xml"))
                        .get("oslc_cm:Collection")
                        .get("rtc_cm:Attachment")[0])
attachment2 = (xmltodict.parse(read_fixture("attachment.xml"))
                        .get("oslc_cm:Collection")
                        .get("rtc_cm:Attachment")[1])
