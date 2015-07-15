import string
import xmltodict
from rtcclient.workitem import Workitem
import re
from rtcclient.base import RTCBase

try:
    import urlparse
    from urllib import quote as urlquote, urlencode
except ImportError:
    # Python3
    import urllib.parse as urlparse
    from urllib.parse import quote as urlquote, urlencode


class Query(RTCBase):
    def __init__(self, baseurl, rtc_obj, query_str):
        """
        :param baseurl: basic url for querying
        :param rtc_obj: a ref to the rtc object
        :param query_str: a valid query string
        :return: Query obj
        """
        self.rtc_obj = rtc_obj
        self.query_str = query_str
        RTCBase.__init__(self, baseurl)

    def __str__(self):
        return self.query_str

    def get_rtc_obj(self):
        return self.rtc_obj

    def queryWorkitems(self, projectarea_id):
        """
        :param projectarea_id: the project area id
        :return: workitems list
        """
        query_str = self.formatQueryStr(self.query_str)
        query_url = "/".join([self.baseurl,
                              projectarea_id,
                              ])
        query_url = "/".join([self.client.baseurl,
                              "oslc/contexts",
                              projectarea_id,
                              "workitems?oslc_cm.query=%s" % query_str])
        resp = self.client.get(query_url,
                               verify=False,
                               headers=self.client.headers)
        workitems_info = xmltodict.parse(resp.content)
        workitems = workitems_info.get("oslc_cm:Collection") \
                                  .get("oslc_cm:ChangeRequest")

        workitems_list = list()
        for workitem in workitems:
            wk = Workitem()
            wk.id = workitem.get("dc:identifier")
            wk.cirats_number = workitem.get("rtc_cm:cirats_number")
            workitems_list.append(wk)

        return workitems_list


