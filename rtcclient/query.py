from rtcclient.base import RTCBase
import logging
from rtcclient import urlquote


class Query(RTCBase):
    """A wrapped class to perform all query-related actions

    :param rtc_obj: a reference to the
        :class:`rtcclient.client.RTCClient` object
    """

    log = logging.getLogger("query:Query")

    def __init__(self, rtc_obj):
        """Initialize <Query> object"""

        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, self.rtc_obj.url)

    def __str__(self):
        return "Query @ %s" % self.rtc_obj

    def get_rtc_obj(self):
        return self.rtc_obj

    def queryWorkitems(self, query_str, projectarea_id=None,
                       projectarea_name=None, returned_properties=None,
                       archived=False):
        """Query workitems with the query string in a certain
        :class:`rtcclient.project_area.ProjectArea`

        At least either of `projectarea_id` and `projectarea_name` is given

        :param query_str: a valid query string
        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the
            :class:`rtcclient.project_area.ProjectArea` name
        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :param archived (default is False): whether the
            :class:`rtcclient.workitem.Workitem` is archived
        :return: a :class:`list` that contains the queried
            :class:`rtcclient.workitem.Workitem` objects
        :rtype: list
        """

        pa_id = (self.rtc_obj
                     ._pre_get_resource(projectarea_id=projectarea_id,
                                        projectarea_name=projectarea_name))

        self.log.info("Start to query workitems with query string: %s",
                      query_str)
        query_str = urlquote(query_str)
        rp = returned_properties

        return (self.rtc_obj
                    ._get_paged_resources("Query",
                                          projectarea_id=pa_id,
                                          customized_attr=query_str,
                                          page_size="100",
                                          returned_properties=rp,
                                          archived=archived))
