import xmltodict
from rtcclient.workitem import Workitem
from rtcclient.base import RTCBase
import logging
from rtcclient import urlquote
from rtcclient import OrderedDict


class Query(RTCBase):
    log = logging.getLogger("query:Query")

    def __init__(self, rtc_obj):
        """Initialize <Query> object

        :param baseurl: base url for querying
        :param rtc_obj: a ref to the rtc object

        """

        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, self.rtc_obj.url)

    def __str__(self):
        return "Query @ %s" % self.rtc_obj

    def get_rtc_obj(self):
        return self.rtc_obj

    def queryWorkitems(self, query_str, projectarea_id=None,
                       projectarea_name=None):
        """Query workitems with the query string in a certain ProjectArea

        At least either of `projectarea_id` and `projectarea_name` is given

        :param query_str: a valid query string
        :param projectarea_id: the project area id
        :param projectarea_name: the project area name
        :return: a list contains the queried <Workitem> objects
        :rtype: list
        """

        pa_id = (self.rtc_obj
                     ._pre_get_resource(projectarea_id=projectarea_id,
                                        projectarea_name=projectarea_name))

        self.log.info("Start to query workitems with query string: %s",
                      query_str)

        query_str = urlquote(query_str)
        query_url = "/".join([self.rtc_obj.url,
                              "oslc/contexts/%s" % pa_id,
                              "workitems?oslc_cm.query=%s" % query_str])

        resp = self.get(query_url,
                        verify=False,
                        headers=self.rtc_obj.headers)

        try:
            workitems_raw_info = xmltodict.parse(resp.content)
        except Exception, excp_msg:
            self.log.error(excp_msg)
            query_new_url = resp.history[-1].url
            self.log.debug("Switch to request the redirect url %s",
                           query_new_url)
            resp = self.get(query_new_url,
                            verify=False,
                            headers=self.rtc_obj.headers)
            workitems_raw_info = xmltodict.parse(resp.content)

        total_count = int(workitems_raw_info.get("oslc_cm:Collection")
                                            .get("@oslc_cm:totalCount"))

        if total_count == 0:
            self.log.warning("No workitems match the query string: %s",
                             self.query_str)
            return None

        workitems_list = list()

        # TODO: self.rtc_obj._get_paged_resources
        # for queries with workitems in several pages
        while True:
            workitems = (workitems_raw_info.get("oslc_cm:Collection")
                                           .get("oslc_cm:ChangeRequest"))

            # the single one on the last page
            if isinstance(workitems, OrderedDict):
                wk = Workitem(workitems.get("@rdf:about"),
                              self.rtc_obj,
                              raw_data=workitems)
                workitems_list.append(wk)
                break

            for workitem in workitems:
                wk = Workitem(workitem.get("@rdf:about"),
                              self.rtc_obj,
                              raw_data=workitem)
                workitems_list.append(wk)

            url_next = (workitems_raw_info.get('oslc_cm:Collection')
                                          .get('@oslc_cm:next'))

            if url_next:
                self.log.debug("Query request on the next page: %s",
                               url_next)
                resp = self.get(url_next,
                                verify=False,
                                headers=self.rtc_obj.headers)
                workitems_raw_info = xmltodict.parse(resp.content)
            else:
                break

        self.log.info("Fetch all the workitems match the query string: %s",
                      self.query_str)
        return workitems_list
