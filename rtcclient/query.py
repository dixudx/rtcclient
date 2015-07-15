import string
import xmltodict
from rtcclient.base import Workitem
import re


class Query(object):
    def __init__(self, client):
        self.client = client

    def queryWorkitems(self, projectarea_id, query_str):
        """
        @param projectarea_id: the project area id
        @param query_str: vaild query string
        @return: workitems list
        """
        query_str = self.formatQueryStr(query_str)
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

    def formatQueryStr(self, query_str):
        """
        @param query_str: vaild query string
        @return: format string
        """
        query_str = query_str.strip()
        punctuation = string.punctuation + " "
        # remove % from punctuation
        punctuation = punctuation.replace("%", "")

        trans_table = dict((char, hex(ord(char)).replace("0x", "%").upper())
                           for char in punctuation)
        regex = re.compile("(%s)" % "|".join(map(re.escape,
                                                 trans_table.keys())))
        qs = regex.sub(lambda m: trans_table[m.string[m.start():m.end()]],
                       query_str)
        return qs

