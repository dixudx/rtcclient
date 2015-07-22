from rtcclient.base import RTCBase
import xmltodict
from rtcclient import exception
from rtcclient.project_area import ProjectArea
from rtcclient.workitem import Workitem
import logging

try:
    import urlparse
    from urllib import quote as urlquote, urlencode
except ImportError:
    # Python3
    import urllib.parse as urlparse
    from urllib.parse import quote as urlquote, urlencode


class RTCClient(RTCBase):
    log = logging.getLogger("client.RTCClient")

    def __init__(self, url, username, password):
        self.username = username
        self.password = password
        RTCBase.__init__(self, url)
        self.headers = self._get_headers()

    def __str__(self):
        return "RTC Server at %s" % self.url

    def get_rtc_obj(self):
        return self

    def _get_headers(self):
        """
        TODO
        """
        _headers = {'Content-type': RTCBase.CONTENT_XML}
        resp = self.get(self.url + "/authenticated/identity",
                        verify=False,
                        headers=_headers)

        _headers['Content-type'] = RTCBase.CONTENT_URL_ENCODED
        _headers['Cookie'] = resp.headers.get('set-cookie')
        credentials = urlencode({'j_username': self.username,
                                 'j_password': self.password})

        resp = self.post(self.url+'/authenticated/j_security_check',
                         data=credentials,
                         verify=False,
                         headers=_headers)

        resp = self.get(self.url + "/authenticated/identity",
                        verify=False,
                        headers=_headers)

        _headers['Cookie'] = resp.headers.get('set-cookie')
        _headers['Accept'] = RTCBase.CONTENT_XML
        return _headers

    def getProjectAreas(self):
        """Get all <ProjectArea> objects

        :return: A list contains all the <ProjectArea> objects
        :rtype: list
        """

        proj_areas_url = "".join([self.url,
                                  "/process/project-areas"])
        resp = self.get(proj_areas_url,
                        verify=False,
                        headers=self.headers)

        proj_areas_list = list()
        raw_data = xmltodict.parse(resp.content)
        proj_areas_raw = raw_data['jp06:project-areas']['jp06:project-area']
        if not proj_areas_raw:
            self.log.info("No projects found in this RTC:<%s>" % self.url)
            return None

        for proj_area_raw in proj_areas_raw:
            proj_area = ProjectArea(proj_area_raw.get("jp06:url"), self)
            proj_area.initialize(proj_area_raw)
            proj_areas_list.append(proj_area)
        return proj_areas_list

    def getProjectArea(self, projectarea_name):
        """Get <ProjectArea> object by its name

        :param projectarea_name: the project area name
        :return: :class:`ProjectArea <ProjectArea>` object
        :rtype: project_area.ProjectArea
        """

        proj_areas = self.getProjectAreas()
        for proj_area in proj_areas:
            if proj_area.name == projectarea_name:
                self.log.info("Find <ProjectArea %s>" % proj_area)
                return proj_area
        else:
            self.log.error("No Project Area named %s" % projectarea_name)
            return None

    def getProjectAreaID(self, projectarea_name):
        """Get <ProjectArea> id by projectarea name

        :param projectarea_name: the project area name
        :return :class `string` object
        :rtype: string
        """

        proj_area = self.getProjectArea(projectarea_name)
        if proj_area:
            return proj_area.id
        return None

    def getWorkitem(self, workitem_id):
        """Get <Workitem> object by its id/number

        :param workitem_id: the workitem number
        :return: :class:`Workitem <Workitem>` object
        :rtype: workitem.Workitem
        """

        try:
            if int(workitem_id):
                workitem_url = "/".join([self.url,
                                         "oslc/workitems/%s" % workitem_id])
                pass
        except ValueError:
            raise exception.BadValue("Please input valid workitem id.")

    def getWorkitems(self, projectarea_name):
        """Get all <Workitem> objects in some certain projectarea name

        :param projectarea_name: the project area name
        :return: a list contains all the `Workitem <Workitem>` objects
        :rtype: list
        """

        pass

    def get_query_url(self, projectarea_name, query_str=""):
        """Format the query url with the query combination string

        :param projectarea_name: the project area name
        :param query_str: the query combination string
        :return: formatted query url
        :rtype: string
        """

        projectarea_id = self.getProjectAreaID(projectarea_name)
        url = "".join([self.url,
                       "/oslc/contexts/%s" % projectarea_id,
                       "/workitems?oslc_cm.query=%s" % urlquote(query_str)])
        return url
