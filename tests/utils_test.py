import os
import xmltodict

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
