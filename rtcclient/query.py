import xmltodict
from rtcclient.workitem import Workitem
from rtcclient.base import RTCBase
import logging

try:
    import urlparse
    from urllib import quote as urlquote, urlencode
except ImportError:
    # Python3
    import urllib.parse as urlparse
    from urllib.parse import quote as urlquote, urlencode


class Query(RTCBase):
    log = logging.getLogger("query:Query")

    def __init__(self, baseurl, rtc_obj, query_str):
        """Initialize <Query> object

        :param baseurl: base url for querying
        :param rtc_obj: a ref to the rtc object
        :param query_str: a valid query string
        """

        self.rtc_obj = rtc_obj
        self.query_str = query_str
        RTCBase.__init__(self, baseurl)

    def __str__(self):
        return self.query_str

    def get_rtc_obj(self):
        return self.rtc_obj

    def queryWorkitems(self, projectarea_id):
        """Query workitems with the query string

        :param projectarea_id: the project area id
        :return: a list contains all <Response> objects
        :rtype: list
        """

        query_str = urlquote(self.query_str)
        query_url = "/".join([self.url,
                              "oslc/contexts",
                              projectarea_id,
                              "workitems?oslc_cm.query=%s" % query_str])
        resp = self.get(query_url,
                        verify=False,
                        headers=self.rtc_obj.headers)
        workitems_raw_info = xmltodict.parse(resp.content)

        totalCount = int(workitems_raw_info.get("oslc_cm:Collection")
                                           .get("@oslc_cm:totalCount"))
        if totalCount == 0:
            self.log.warning("No workitems matched query string: %s",
                             self)
            return None

        workitems_raw = workitems_raw_info.get("oslc_cm:Collection") \
                                          .get("oslc_cm:ChangeRequest")

        workitems_list = list()
        for workitem_raw in workitems_raw:
            workitem = Workitem("/".join([self.url,
                                          "oslc/workitem",
                                          workitem_raw.get("dc:identifier")]),
                                self.rtc_obj)
            workitem.initialize(workitem_raw)
            workitems_list.append(workitem)

        return workitems_list
