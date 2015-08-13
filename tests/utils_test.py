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