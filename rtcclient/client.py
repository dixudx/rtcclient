from rtcclient.base import RTCBase
import xmltodict
from rtcclient import exception
from rtcclient.project_area import ProjectArea
from rtcclient.workitem import Workitem
import logging
from rtcclient import urlquote, urlencode
from collections import OrderedDict
import copy

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
        TODO: for invalid username or password,
            rtc cannot return the right code
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
        pass
        """

        self.log.info("Get all the ProjectAreas")

        proj_areas_url = "/".join([self.url,
                                   "process/project-areas"])
        resp = self.get(proj_areas_url,
                        verify=False,
                        headers=self.headers)

        proj_areas_list = list()
        raw_data = xmltodict.parse(resp.content)
        proj_areas_raw = raw_data['jp06:project-areas']['jp06:project-area']
        if not proj_areas_raw:
            self.log.warning("No ProjectAreas are found in <%s>", self)
            return None

        for proj_area_raw in proj_areas_raw:
            proj_area = ProjectArea(url=proj_area_raw.get("jp06:url"),
                                    rtc_obj=self,
                                    raw_data=proj_area_raw,
                                    name=proj_area_raw.get("@jp06:name"))
            proj_areas_list.append(proj_area)
        return proj_areas_list

    def getProjectArea(self, projectarea_name):
        """Get <ProjectArea> object by its name

        :param projectarea_name: the project area name
        :return: :class:`ProjectArea <ProjectArea>` object
        :rtype: project_area.ProjectArea
        pass
        """

        self.log.debug("Try to get <ProjectArea %s>", projectarea_name)
        if not projectarea_name:
            excp_msg = "Please specify a valid ProjectArea name"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        proj_areas = self.getProjectAreas()
        if proj_areas is not None:
            for proj_area in proj_areas:
                if proj_area.name == projectarea_name:
                    self.log.info("Find <ProjectArea %s>", proj_area)
                    return proj_area

        self.log.error("No ProjectArea named %s", projectarea_name)
        raise exception.NotFound("No ProjectArea named %s" % projectarea_name)

    def getProjectAreaById(self, projectarea_id):
        """Get <ProjectArea> object by its id

        :param projectarea_id: the project area id
        :return: :class:`ProjectArea <ProjectArea>` object
        :rtype: project_area.ProjectArea
        pass
        """

        self.log.debug("Try to get <ProjectArea> by its id: %s",
                       projectarea_id)
        if not projectarea_id:
            excp_msg = "Please specify a valid ProjectArea ID"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        proj_areas = self.getProjectAreas()
        if proj_areas is not None:
            for proj_area in proj_areas:
                if proj_area.id == projectarea_id:
                    self.log.info("Find <ProjectArea %s>", proj_area)
                    return proj_area

        self.log.error("No ProjectArea's ID is %s", projectarea_id)
        raise exception.NotFound("No ProjectArea's ID is %s" % projectarea_id)

    def getProjectAreaID(self, projectarea_name):
        """Get <ProjectArea> id by projectarea name

        :param projectarea_name: the project area name
        :return :class `string` object
        :rtype: string
        pass
        """

        self.log.debug("Get the ProjectArea id by its name: %s",
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

        self.log.debug("Check the validity of the ProjectArea id: %s",
                       projectarea_id)

        proj_areas = self.getProjectAreas()
        if proj_areas is not None:
            for proj_area in proj_areas:
                if proj_area.id == projectarea_id:
                    self.log.info("Find <ProjectArea %s> whose id is: %s",
                                  proj_area,
                                  projectarea_id)
                    return True

        self.log.error("No ProjectArea whose id is: %s",
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
                workitem_raw = raw_data["oslc_cm:ChangeRequest"]

                return Workitem(workitem_url,
                                self,
                                workitem_id=workitem_id,
                                raw_data=workitem_raw)

        except ValueError:
            excp_msg = "Please input a valid workitem id"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)
        except Exception, excp:
            # TODO: invalid token for all get resp
            self.log.error(excp)

    def getWorkitems(self, projectarea_id=None, projectarea_name=None):
        """Get all <Workitem> objects in some certain projectarea name

        If both projectarea_id and projectarea_name are None, all the workitems
        in all ProjectAreas will be returned.

        :param projectarea_id: the project area id
        :param projectarea_name: the project area name
        :return: a list contains all the `Workitem <Workitem>` objects
        :rtype: list
        pass
        """

        workitems_list = list()
        projectarea_ids = list()
        if not projectarea_id:
            try:
                projectarea_id = self.getProjectAreaID(projectarea_name)
                projectarea_ids.append(projectarea_id)
            except (exception.NotFound, exception.BadValue):
                self.log.error("Invalid ProjectArea name")
                self.log.warning("Fetch all workitems in all ProjectAreas")
                projectareas = self.getProjectAreas()
                projectarea_ids = [proj_area.id for proj_area in projectareas]
        else:
            projectarea_ids.append(projectarea_id)

        self.log.warning("For a single ProjectArea, only latest 1000 "
                         "workitems can be fetched. "
                         "This may be a bug of Rational Team Concert")

        for projarea_id in projectarea_ids:
            workitems_list.extend(self._get_resource_collections("Workitem",
                                                                 projarea_id))

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
            # TODO
            return None
        
        

        pass
        self.log.info("Start to create a %s",
                      item_type)

    def checkType(self, item_type, projectarea_id):
        """Check the validity of workitem type

        :param item_type: the type of the workitem (e.g. task/defect/issue)
        :param projectarea_id: the project area id
        :return: True or False
        :rtype: bool
        """

        self.log.debug("Checking the validity of workitem type: %s",
                       item_type)
        try:
            project_area = self.getProjectAreaById(projectarea_id)
            itemtype = project_area.getItemType(item_type)
            return True
        except (exception.NotFound, exception.BadValue):
            self.log.error("Invalid ProjectArea name")
            return False

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

    def _get_resource_collections(self, resource_name, projectarea_id,
                                  page_size='100'):

        # TODO: multi-thread

        if not projectarea_id:
            self.log.error("No ProjectArea ID is specified")
            raise exception.EmptyAttrib("No ProjectArea ID")

        # TODO: for category/deliverable/iteration object
        resource_map = {"Category": "categories",
                        "Deliverable": "deliverables",
                        "Iteration": "iterations",
                        "Workitem": "contexts/%s/workitems" % projectarea_id}

        if resource_name not in resource_map:
            self.log.error("Unsupported resource name")
            return None

        resource_url = "".join([self.url,
                                "/oslc/{0}?oslc_cm.pageSize={1}",
                                "&_startIndex=0"])
        resource_url = resource_url.format(resource_map[resource_name],
                                           page_size)

        resp = self.get(resource_url,
                        verify=False,
                        headers=self.headers)
        raw_data = xmltodict.parse(resp.content)

        resources_list = []

        while True:
            if resource_name == "Workitem":
                entries = (raw_data.get("oslc_cm:Collection")
                                   .get("oslc_cm:ChangeRequest"))
            else:
                entries = (raw_data.get("oslc_cm:Collection")
                                   .get("rtc_cm:%s" % resource_name))

            # for the last single entry
            if isinstance(entries, OrderedDict):
                resource = self._handle_resource_entry(resource_name, entries)
                resources_list.append(resource)
                break

            for entry in entries:
                resource = self._handle_resource_entry(resource_name, entry)
                resources_list.append(resource)

            url_next = raw_data.get('oslc_cm:Collection').get('@oslc_cm:next')

            if url_next:
                resp = self.get(url_next,
                                verify=False,
                                headers=self.headers)
                raw_data = xmltodict.parse(resp.content)
            else:
                break

        return resources_list

    def _handle_resource_entry(self, resource_name, entry):
        resource_cls = eval(resource_name)
        if resource_name == "Workitem":
            resource_url = entry.get("@rdf:resource")
            resource_url = "/".join([self.url,
                                     "oslc/workitems",
                                     resource_url.split("/")[-1]])
        else:
            resource_url = entry.get("@rdf:resource")

        resource = resource_cls(resource_url,
                                self,
                                raw_data=entry)
        return resource
