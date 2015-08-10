import os


_path = os.path.realpath(os.path.dirname(__file__))
_search_path = os.path.join(_path, 'fixtures')


def read_fixture(file_name):
    file_path = os.path.join(_search_path, file_name)
    with open(file_path, mode="r") as fh:
        return fh.read()


pa1 = """
<oslc_cm:Collection>
<rtc_cm:Project rdf:resource="http://test.url:9443/jazz/oslc/projectareas/_0qMJUMfiEd6yW_0tvNlbrw">
<dc:title>ProjectArea1</dc:title>
<dc:description>Demo for test: Project Area One</dc:description>
<rtc_cm:detailedDescription/>
<rtc_cm:initialized>true</rtc_cm:initialized>
<rtc_cm:archived>true</rtc_cm:archived>
</rtc_cm:Project>
</oslc_cm:Collection>
"""


pa2 = """
<oslc_cm:Collection>
<rtc_cm:Project rdf:resource="http://test.url:9443/jazz/oslc/projectareas/_CuZu0HUwEeKicpXBddtqNA">
<dc:title>ProjectArea2</dc:title>
<dc:description>Demo for test: Project Area Two</dc:description>
<rtc_cm:detailedDescription/>
<rtc_cm:initialized>true</rtc_cm:initialized>
<rtc_cm:archived>false</rtc_cm:archived>
</rtc_cm:Project>
</oslc_cm:Collection>
"""
