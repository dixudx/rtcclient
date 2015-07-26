from rtcclient.base import RTCBase
import xmltodict
from rtcclient import exception
from rtcclient.project_area import ProjectArea
from rtcclient.workitem import Workitem
import logging
from rtcclient import urlquote, urlencode


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

        self.log.info("Get all the project areas")

        proj_areas_url = "".join([self.url,
                                  "/process/project-areas"])
        resp = self.get(proj_areas_url,
                        verify=False,
                        headers=self.headers)

        proj_areas_list = list()
        raw_data = xmltodict.parse(resp.content)
        proj_areas_raw = raw_data['jp06:project-areas']['jp06:project-area']
        if not proj_areas_raw:
            self.log.error("No project areas found in <%s>", self)
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

        self.log.debug("Try to get <ProjectArea %s>", projectarea_name)
        if not projectarea_name:
            excp_msg = "Please specify a valid project area name"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        proj_areas = self.getProjectAreas()
        for proj_area in proj_areas:
            if proj_area.name == projectarea_name:
                self.log.info("Find <ProjectArea %s>", proj_area)
                return proj_area

        self.log.error("No Project Area named %s", projectarea_name)
        raise exception.NotFound("No Project Area named %s" % projectarea_name)

    def getProjectAreaID(self, projectarea_name):
        """Get <ProjectArea> id by projectarea name

        :param projectarea_name: the project area name
        :return :class `string` object
        :rtype: string
        """

        self.log.debug("Get the project area id by its name: %s",
                       projectarea_name)
        proj_area = self.getProjectArea(projectarea_name)
        if proj_area:
            return proj_area.id
        return None

    def checkProjectAreaID(self, projectarea_id):
        """Check the validity of <ProjectArea> ID

        :param projectarea_id: the project area id
        :return True or False
        :rtype: bool
        """

        self.log.debug("Check the validity of the project area id: %s",
                       projectarea_id)

        proj_areas = self.getProjectAreas()
        for proj_area in proj_areas:
            if proj_area.id == projectarea_id:
                self.log.info("Find <ProjectArea %s> whose id is: %s",
                              proj_area,
                              projectarea_id)
                return True

        self.log.error("No Project Area whose id is: %s",
                       projectarea_id)
        return False

    def getWorkitem(self, workitem_id):
        """Get <Workitem> object by its id/number

        :param workitem_id: the workitem number (integer)
        :return: :class:`Workitem <Workitem>` object
        :rtype: workitem.Workitem
        """

        try:
            if int(workitem_id):
                workitem_url = "/".join([self.url,
                                         "oslc/workitems/%s" % workitem_id])
                resp = self.get(workitem_url,
                                verify=False,
                                headers=self.headers)
                raw_data = xmltodict.parse(resp.content)
                # TODO
                workitem_raw = raw_data

                workitem = Workitem(workitem_url,
                                    self,
                                    workitem_id)
                workitem.initialize(workitem_raw)
        except ValueError:
            excp_msg = "Please input a valid workitem id"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

    def getWorkitems(self, projectarea_id=None, projectarea_name=None):
        """Get all <Workitem> objects in some certain projectarea name

        :param projectarea_id: the project area id
        :param projectarea_name: the project area name
        :return: a list contains all the `Workitem <Workitem>` objects
        :rtype: list
        """
        # TODO: multi-thread

        if not projectarea_id:
            projectarea_id = self.getProjectAreaID(projectarea_name)

        workitems_url = "/".join([self.url,
                                  "oslc/workitems"])
        resp = self.get(workitems_url,
                        verify=False,
                        headers=self.headers)
        raw_data = xmltodict.parse(resp.content)

        #TODO: raw data
        workitems_raw = raw_data

        if not workitems_raw:
            self.log.warning("There are no workitems in ProjectArea:<%s>",
                             self.name)
            return None

        workitems_list = list()
        for workitem_raw in workitems_raw:
            # TODO: url, id
            workitem = Workitem(workitem_raw.get("jp:url"),
                                self,
                                workitem_id=None)
            workitem.initialize(workitem_raw)
            workitems_list.append(workitem)

        return workitems_list

    def createWorkitem(self, item_type, projectarea_id=None,
                       projectarea_name=None, **kwargs):
        """Create a workitem

        :param item_type: the type of the workitem (e.g. task/defect/issue)
        :param projectarea_id: the project area id
        :param projectarea_name: the project area name
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Workitem <Workitem>` object
        :rtype: workitem.Workitem
        """

        # TODO

        if not projectarea_id:
            projectarea_id = self.getProjectAreaID(projectarea_name)

        if not self.checkType(item_type):
            self.log.error("<%s> is not a supported workitem type in %s",
                           item_type.capitalize(), self)
            return None

        pass
        self.log.info("Start to create a %s",
                      item_type)

    def checkType(self, item_type):
        """Check the validity of workitem type

        :param item_type: the type of the workitem (e.g. task/defect/issue)
        :return: True or False
        :rtype: bool
        """

        # TODO
        self.log.debug("Checking the validity of workitem type: %s",
                       item_type)
        pass

    def getScheme(self, item_type):
        """Get the scheme for the certain workitem type, including some
        optional and mandatory fields/parameters

        TODO
        :param item_type: the type of the workitem (e.g. task/defect/issue)
        :return: :class:`ItemScheme <ItemScheme>` object
        :rtype: workitem.ItemScheme
        """

        # TODO
        self.log.debug("Get the scheme for workitem %s",
                       item_type)
        pass

    def get_query_url(self, projectarea_id=None, projectarea_name=None,
                      query_str=""):
        """Format the query url with the query combination string

        :param projectarea_id: the project area id
        :param projectarea_name: the project area name
        :param query_str: the query combination string
        :return: formatted query url
        :rtype: string
        """

        if not projectarea_id:
            projectarea_id = self.getProjectAreaID(projectarea_name)

        url = "/".join([self.url,
                        "oslc/contexts/%s" % projectarea_id,
                        "workitems?oslc_cm.query=%s" % urlquote(query_str)])
        return url
