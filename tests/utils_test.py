import os


_path = os.path.realpath(os.path.dirname(__file__))
_search_path = os.path.join(_path, 'fixtures')


def read_fixture(file_name):
    file_path = os.path.join(_search_path, file_name)
    with open(file_path, mode="r") as fh:
        return fh.read()


pa1 = """
<rtc_cm:Project rdf:resource="http://test.url:9443/jazz/oslc/projectareas/_0qMJUMfiEd6yW_0tvNlbrw">
<dc:title>ProjectArea1</dc:title>
<dc:description>Demo for test: Project Area One</dc:description>
<rtc_cm:detailedDescription/>
<rtc_cm:initialized>true</rtc_cm:initialized>
<rtc_cm:archived>true</rtc_cm:archived>
</rtc_cm:Project>
"""


pa2 = """
<rtc_cm:Project rdf:resource="http://test.url:9443/jazz/oslc/projectareas/_CuZu0HUwEeKicpXBddtqNA">
<dc:title>ProjectArea2</dc:title>
<dc:description>Demo for test: Project Area Two</dc:description>
<rtc_cm:detailedDescription/>
<rtc_cm:initialized>true</rtc_cm:initialized>
<rtc_cm:archived>false</rtc_cm:archived>
</rtc_cm:Project>
"""


ta1 = """
<rtc_cm:Team rdf:resource="http://test.url:9443/jazz/oslc/teamareas/_ECYfMHUwEeKicpXBddtqNA">
<dc:title>Team1</dc:title>
<dc:description/>
<rtc_cm:archived>false</rtc_cm:archived>
<rtc_cm:projectArea rdf:resource="http://test.url:9443/jazz/oslc/projectareas/_CuZu0HUwEeKicpXBddtqNA"/>
<rtc_cm:members oslc_cm:collref="http://test.url:9443/jazz/oslc/teamareas/_ECYfMHUwEeKicpXBddtqNA/rtc_cm:members"/>
<rtc_cm:administrators oslc_cm:collref="http://test.url:9443/jazz/oslc/teamareas/_ECYfMHUwEeKicpXBddtqNA/rtc_cm:administrators"/>
</rtc_cm:Team>
"""

ta2 = """
<rtc_cm:Team rdf:resource="http://test.url:9443/jazz/oslc/teamareas/_XazXEPbZEeGWkpg5MjeYZQ">
<dc:title>Team2</dc:title>
<dc:description/>
<rtc_cm:archived>false</rtc_cm:archived>
<rtc_cm:projectArea rdf:resource="http://test.url:9443/jazz/oslc/projectareas/_CuZu0HUwEeKicpXBddtqNA"/>
<rtc_cm:members oslc_cm:collref="http://test.url:9443/jazz/oslc/teamareas/_XazXEPbZEeGWkpg5MjeYZQ/rtc_cm:members"/>
<rtc_cm:administrators oslc_cm:collref="http://test.url:9443/jazz/oslc/teamareas/_XazXEPbZEeGWkpg5MjeYZQ/rtc_cm:administrators"/>
</rtc_cm:Team>
"""

plannedfor1 = """
<rtc_cm:Iteration rdf:resource="http://test.url:9443/jazz/oslc/iterations/_00J9ocfiEd6yW_0tvNlbrw">
<dc:identifier>1.0</dc:identifier>
<dc:title>Release 1.0</dc:title>
<dc:description/>
<rtc_cm:startDate>2009-11-02T06:00:00.000Z</rtc_cm:startDate>
<rtc_cm:endDate>2009-12-12T06:00:00.000Z</rtc_cm:endDate>
<rtc_cm:parent/>
<rtc_cm:hasDeliverable>true</rtc_cm:hasDeliverable>
<rtc_cm:archived>true</rtc_cm:archived>
<rtc_cm:timeline rdf:resource="http://test.url:9443/jazz/oslc/timelines/_00J9oMfiEd6yW_0tvNlbrw"/>
<rtc_cm:projectArea rdf:resource="http://test.url:9443/jazz/oslc/projectareas/_0qMJUMfiEd6yW_0tvNlbrw"/>
</rtc_cm:Iteration>
"""

plannedfor2 = """
<rtc_cm:Iteration rdf:resource="http://test.url:9443/jazz/oslc/iterations/_DbGcwHUwEeKicpXBddtqNA">
<dc:identifier>1.0 S1</dc:identifier>
<dc:title>Sprint 1 (1.0)</dc:title>
<dc:description/>
<rtc_cm:startDate>2013-02-12T06:00:00.000Z</rtc_cm:startDate>
<rtc_cm:endDate>2013-03-04T06:00:00.000Z</rtc_cm:endDate>
<rtc_cm:parent rdf:resource="http://test.url:9443/jazz/oslc/iterations/_DbF1sXUwEeKicpXBddtqNA"/>
<rtc_cm:hasDeliverable>true</rtc_cm:hasDeliverable>
<rtc_cm:archived>false</rtc_cm:archived>
<rtc_cm:timeline rdf:resource="http://test.url:9443/jazz/oslc/timelines/_DbF1sHUwEeKicpXBddtqNA"/>
<rtc_cm:projectArea rdf:resource="http://test.url:9443/jazz/oslc/projectareas/_CuZu0HUwEeKicpXBddtqNA"/>
</rtc_cm:Iteration>
"""

severity1 = """
<rtc_cm:Literal rdf:resource="http://test.url:9443/jazz/oslc/enumerations/_CuZu0HUwEeKicpXBddtqNA/severity/severity.literal.l1">
<dc:identifier>severity.literal.l1</dc:identifier>
<dc:title>Unclassified</dc:title>
<rtc_cm:iconUrl>
http://test.url:9443/jazz/service/com.ibm.team.workitem.common.internal.model.IImageContentService/processattachment/_CuZu0HUwEeKicpXBddtqNA/enumeration/unassigned2.gif
</rtc_cm:iconUrl>
</rtc_cm:Literal>
"""

severity2 = """
<rtc_cm:Literal rdf:resource="http://test.url:9443/jazz/oslc/enumerations/_CuZu0HUwEeKicpXBddtqNA/severity/severity.literal.l2">
<dc:identifier>severity.literal.l2</dc:identifier>
<dc:title>Normal</dc:title>
<rtc_cm:iconUrl>
http://test.url:9443/jazz/service/com.ibm.team.workitem.common.internal.model.IImageContentService/processattachment/_CuZu0HUwEeKicpXBddtqNA/enumeration/normal.gif
</rtc_cm:iconUrl>
</rtc_cm:Literal>
"""

priority1 = """
<rtc_cm:Literal rdf:resource="http://test.url:9443/jazz/oslc/enumerations/_CuZu0HUwEeKicpXBddtqNA/priority/priority.literal.l01">
<dc:identifier>priority.literal.l01</dc:identifier>
<dc:title>Unassigned</dc:title>
<rtc_cm:iconUrl>
http://test.url:9443/jazz/service/com.ibm.team.workitem.common.internal.model.IImageContentService/processattachment/_CuZu0HUwEeKicpXBddtqNA/enumeration/unassigned.gif
</rtc_cm:iconUrl>
</rtc_cm:Literal>
"""

priority2 = """
<rtc_cm:Literal rdf:resource="http://test.url:9443/jazz/oslc/enumerations/_CuZu0HUwEeKicpXBddtqNA/priority/priority.literal.l11">
<dc:identifier>priority.literal.l11</dc:identifier>
<dc:title>High</dc:title>
<rtc_cm:iconUrl>
http://test.url:9443/jazz/service/com.ibm.team.workitem.common.internal.model.IImageContentService/processattachment/_CuZu0HUwEeKicpXBddtqNA/enumeration/high.gif
</rtc_cm:iconUrl>
</rtc_cm:Literal>
"""

foundin1 = """
<rtc_cm:Deliverable rdf:resource="http://test.url:9443/jazz/resource/itemOid/com.ibm.team.workitem.Deliverable/_Hx5_wKOlEeKPvqjjtP1sGw">
<dc:title>Sprint1</dc:title>
<rtc_cm:projectArea rdf:resource="http://test.url:9443/jazz/oslc/projectareas/_0qMJUMfiEd6yW_0tvNlbrw"/>
<dc:description/>
<rtc_cm:archived>true</rtc_cm:archived>
<rtc_cm:filtered>true</rtc_cm:filtered>
<rtc_cm:artifact/>
<dc:created/>
<dc:modified>2009-11-05T11:36:00.596Z</dc:modified>
<rtc_cm:modifiedBy rdf:resource="http://test.url:9443/jts/users/tester1%40email.com"/>
</rtc_cm:Deliverable>
"""

foundin2 = """
<rtc_cm:Deliverable rdf:resource="http://test.url:9443/jazz/resource/itemOid/com.ibm.team.workitem.Deliverable/_vztkUOW3Ed6ThJa-QCz7dg">
<dc:title>Sprint2</dc:title>
<rtc_cm:projectArea rdf:resource="http://test.url:9443/jazz/oslc/projectareas/_CuZu0HUwEeKicpXBddtqNA"/>
<dc:description/>
<rtc_cm:archived>false</rtc_cm:archived>
<rtc_cm:filtered>false</rtc_cm:filtered>
<rtc_cm:artifact/>
<dc:created/>
<dc:modified>2015-07-21T01:46:12.096Z</dc:modified>
<rtc_cm:modifiedBy rdf:resource="http://test.url:9443/jts/users/tester2%40email.com"/>
</rtc_cm:Deliverable>
"""
