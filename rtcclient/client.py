from rtcclient.base import RTCBase
import xmltodict
import requests
from rtcclient import exception
from rtcclient.project_area import ProjectArea
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

    def __init__(self, baseurl, username, password):
        self.username = username
        self.password = password
        RTCBase.__init__(self, baseurl)
        self.headers = self._get_headers()

    def __str__(self):
        return "RTC Server at %s" % self.baseurl

    def get_rtc_obj(self):
        return self

    def _get_headers(self):
        """
        TODO
        """
        _headers = {'Content-type': RTCBase.CONTENT_XML}
        resp = requests.get(self.baseurl + "/authenticated/identity",
                            verify=False,
                            headers=_headers,
                            timeout=60)

        _headers['Content-type'] = RTCBase.CONTENT_URL_ENCODED
        _headers['Cookie'] = resp.headers.get('set-cookie')
        credentials = urlencode({'j_username': self.username,
                                 'j_password': self.password})

        resp = requests.post(self.baseurl+'/authenticated/j_security_check',
                             data=credentials,
                             verify=False,
                             headers=_headers)

        resp = requests.get(self.baseurl + "/authenticated/identity",
                            verify=False,
                            headers=_headers,
                            timeout=60)

        _headers['Cookie'] = resp.headers.get('set-cookie')
        _headers['Accept'] = RTCBase.CONTENT_XML
        return _headers

    def getProjectAreas(self):
        """
        :return: Get all the project areas
        """
        proj_areas_url = "".join([self.baseurl,
                                  "/process/project-areas"])
        resp = requests.get(proj_areas_url,
                            verify=False,
                            headers=self.headers)

        proj_areas_list = list()
        raw_data = xmltodict.parse(resp.content)
        proj_areas_raw = raw_data['jp06:project-areas']['jp06:project-area']
        if not proj_areas_raw:
            self.log.info("No projects found in this RTC:<%s>" % self.baseurl)
            return None
        for proj_area_raw in proj_areas_raw:
            proj_area = ProjectArea(proj_area_raw.get("jp06:url"), self)
            proj_area.initialize(proj_area_raw)
            proj_areas_list.append(proj_area)
        return proj_areas_list

    def getProjectArea(self, projectarea_name):
        """
        :param projectarea_name: the project area name
        :return: The project area object
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
        """
        :param projectarea_name: the project area name
        """
        proj_area = self.getProjectArea(projectarea_name)
        if proj_area:
            return proj_area.id
        return None

    def getWorkitem(self, workitem_id):
        """
        :param workitem_id: the workitem number
        :return: the workitem object
        """
        try:
            if int(workitem_id):
                pass
        except ValueError:
            raise exception.BadValue("Please input valid workitem id.")

    def get_query_url(self, projectarea_name, query_str=""):
        """
        :param projectarea_name: the project area name
        :param query_str: the query string
        :return: the url for query
        """
        projectarea_id = self.getProjectAreaID(projectarea_name)
        url = "".join([self.baseurl,
                       "/oslc/contexts/%s" % projectarea_id,
                       "/workitems?oslc_cm.query=%s" % urlquote(query_str)])
        return url
