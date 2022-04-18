from rtcclient.base import RTCBase
import xmltodict
from rtcclient import exception
from rtcclient.project_area import ProjectArea
from rtcclient.workitem import Workitem
from rtcclient.models import TeamArea, Member, Administrator, PlannedFor
from rtcclient.models import Severity, Priority, ItemType, SavedQuery
from rtcclient.models import FiledAgainst, FoundIn, Comment, Action, State
from rtcclient.models import IncludedInBuild, ChangeSet, Attachment
import logging
from rtcclient import urlparse, urlquote, urlencode, OrderedDict
import copy
from rtcclient.template import Templater
from rtcclient import _search_path
from rtcclient.query import Query
import six
from rtcclient.utils import capitalize


class RTCClient(RTCBase):
    """A wrapped class for :class:`RTC Client` to perform all related
    operations

    :param url: the rtc url (e.g. https://your_domain:9443/jazz)
    :param username: the rtc username
    :param password: the rtc password
    :param proxies: (optional) Dictionary mapping protocol to the URL of
            the proxy.
    :param searchpath: (optional) the folder to store your templates.
        If `None`, the default search path
        (/your/site-packages/rtcclient/templates) will be loaded.
    :param ends_with_jazz: (optional but important) Set to `True` (default) if
        the url ends with 'jazz', otherwise to `False` if with 'ccm'
        (Refer to issue #68 for details)
    :type ends_with_jazz: bool

    Tips: You can also customize your preferred properties to be returned
    by specified `returned_properties` when the called methods have
    this optional parameter, which can also GREATLY IMPROVE the performance
    of this client especially when getting or querying lots of workitems.

    Important Note: `returned_properties` is an advanced parameter, the
    returned properties can be found in `ClassInstance.field_alias.values()`,
    e.g. `myworkitem1.field_alias.values()`. If you don't care the performance,
    just leave it alone with `None`.
    """

    log = logging.getLogger("client.RTCClient")

    def __init__(self, url, username, password, proxies=None, searchpath=None,
                 ends_with_jazz=True):
        """Initialization

        See params above
        """

        self.username = username
        self.password = password
        self.proxies = proxies
        RTCBase.__init__(self, url)

        if not isinstance(ends_with_jazz, bool):
            raise exception.BadValue("ends_with_jazz is not boolean")

        self.jazz = ends_with_jazz
        self.headers = self._get_headers()
        if searchpath is None:
            self.searchpath = _search_path
        else:
            self.searchpath = searchpath
        self.templater = Templater(self, searchpath=self.searchpath)
        self.query = Query(self)

    def __str__(self):
        return "RTC Server at %s" % self.url

    def get_rtc_obj(self):
        return self

    def _get_headers(self):
        if self.jazz is True:
            _allow_redirects = True
        else:
            _allow_redirects = False

        _headers = {"Content-Type": self.CONTENT_XML}
        resp = self.get(self.url + "/authenticated/identity",
                        auth=(self.username, self.password),
                        verify=False,
                        headers=_headers,
                        proxies=self.proxies,
                        allow_redirects=_allow_redirects)

        # authfailed
        authfailed = resp.headers.get("x-com-ibm-team-repository-web-auth-msg")
        if authfailed == "authfailed":
            raise exception.RTCException("Authentication Failed: "
                                         "Invalid username or password")

        # header changes in 6.0.3, issue #92
        authfailedloc = resp.headers.get("Location")
        if authfailedloc is not None and authfailedloc.endswith("authfailed"):
            raise exception.RTCException("Authentication Failed: "
                                         "Invalid username or password")

        # fix issue #68
        if not _allow_redirects:
            if resp.headers.get("set-cookie") is not None:
                _headers["Cookie"] = resp.headers.get("set-cookie")

        resp = self.get(self.url + "/authenticated/identity",
                        auth=(self.username, self.password),
                        verify=False,
                        headers=_headers,
                        proxies=self.proxies,
                        allow_redirects=_allow_redirects)

        # fix issue #68
        if not _allow_redirects:
            _headers["Cookie"] += "; " + resp.headers.get("set-cookie")
        else:
            _headers["Cookie"] = resp.headers.get("set-cookie")

        _headers["Accept"] = self.CONTENT_XML
        return _headers

    def relogin(self):
        """Relogin the RTC Server/Jazz when the token expires

        """

        self.log.info("Cookie expires. Relogin to get a new cookie.")
        self.headers = None
        self.headers = self._get_headers()
        self.log.debug("Successfully relogin.")

    def getProjectAreas(self, archived=False, returned_properties=None):
        """Get all :class:`rtcclient.project_area.ProjectArea` objects

        If no :class:`rtcclient.project_area.ProjectArea` objects are
        retrieved, `None` is returned.

        :param archived: (default is False) whether the project area
            is archived
        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :return: A :class:`list` that contains all the
            :class:`rtcclient.project_area.ProjectArea` objects
        :rtype: list
        """

        return self._getProjectAreas(archived=archived,
                                     returned_properties=returned_properties)

    def getProjectArea(self, projectarea_name, archived=False,
                       returned_properties=None):
        """Get :class:`rtcclient.project_area.ProjectArea` object by its name

        :param projectarea_name: the project area name
        :param archived: (default is False) whether the project area
            is archived
        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :return: the :class:`rtcclient.project_area.ProjectArea` object
        :rtype: rtcclient.project_area.ProjectArea
        """

        if not isinstance(projectarea_name,
                          six.string_types) or not projectarea_name:
            excp_msg = "Please specify a valid ProjectArea name"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        self.log.debug("Try to get <ProjectArea %s>", projectarea_name)
        rp = returned_properties
        proj_areas = self._getProjectAreas(archived=archived,
                                           returned_properties=rp,
                                           projectarea_name=projectarea_name)

        if proj_areas is not None:
            proj_area = proj_areas[0]
            self.log.info("Find <ProjectArea %s>", proj_area)
            return proj_area

        self.log.error("No ProjectArea named %s", projectarea_name)
        raise exception.NotFound("No ProjectArea named %s" % projectarea_name)

    def _getProjectAreas(self, archived=False, returned_properties=None,
                         projectarea_name=None, projectarea_id=None):
        rp = returned_properties

        filter_rule = None
        if projectarea_name is not None:
            fpaname_rule = ("dc:title", None, projectarea_name)
            filter_rule = self._add_filter_rule(filter_rule, fpaname_rule)

        if projectarea_id is not None:
            paid_url = "/".join([self.url, "oslc/projectareas",
                                 projectarea_id])
            fpaid_rule = ("@rdf:resource", None, paid_url)
            filter_rule = self._add_filter_rule(filter_rule, fpaid_rule)

        return self._get_paged_resources("ProjectArea",
                                         page_size="10",
                                         archived=archived,
                                         returned_properties=rp,
                                         filter_rule=filter_rule)

    def _add_filter_rule(self, filter_rule, added_rule):
        if filter_rule is None:
            filter_rule = [added_rule]
        else:
            filter_rule.append(added_rule)
        return filter_rule

    def getProjectAreaByID(self, projectarea_id, archived=False,
                           returned_properties=None):
        """Get :class:`rtcclient.project_area.ProjectArea` object by its id

        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param archived: (default is False) whether the project area
            is archived
        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :return: the :class:`rtcclient.project_area.ProjectArea` object
        :rtype: rtcclient.project_area.ProjectArea
        """

        if not isinstance(projectarea_id,
                          six.string_types) or not projectarea_id:
            excp_msg = "Please specify a valid ProjectArea ID"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        self.log.debug("Try to get <ProjectArea> by its id: %s",
                       projectarea_id)
        rp = returned_properties
        proj_areas = self._getProjectAreas(archived=archived,
                                           returned_properties=rp,
                                           projectarea_id=projectarea_id)
        if proj_areas is not None:
            proj_area = proj_areas[0]
            self.log.info("Find <ProjectArea %s>", proj_area)
            return proj_area

        self.log.error("No ProjectArea's ID is %s", projectarea_id)
        raise exception.NotFound("No ProjectArea's ID is %s" % projectarea_id)

    def getProjectAreaID(self, projectarea_name, archived=False):
        """Get :class:`rtcclient.project_area.ProjectArea` id by its name

        :param projectarea_name: the project area name
        :param archived: (default is False) whether the project area
            is archived
        :return: the :class:`string` object
        :rtype: string
        """

        self.log.debug("Get the ProjectArea id by its name: %s",
                       projectarea_name)
        proj_area = self.getProjectArea(projectarea_name,
                                        archived=archived)
        if proj_area:
            return proj_area.id
        raise exception.NotFound("No ProjectArea named %s" % projectarea_name)

    def getProjectAreaIDs(self, projectarea_name=None, archived=False):
        """Get all :class:`rtcclient.project_area.ProjectArea` id(s)
        by project area name

        If `projectarea_name` is `None`, all the
        :class:`rtcclient.project_area.ProjectArea` id(s) will be returned.

        :param projectarea_name: the project area name
        :param archived: (default is False) whether the project area
            is archived
        :return: a :class:`list` that contains all the :class:`ProjectArea` ids
        :rtype: list
        """

        projectarea_ids = list()
        if projectarea_name and isinstance(projectarea_name,
                                           six.string_types):
            projectarea_id = self.getProjectAreaID(projectarea_name,
                                                   archived=archived)
            projectarea_ids.append(projectarea_id)
        elif projectarea_name is None:
            projectareas = self.getProjectAreas(archived=archived)
            if projectareas is None:
                return None
            projectarea_ids = [proj_area.id for proj_area in projectareas]
        else:
            error_msg = "Invalid ProjectArea name: [%s]" % projectarea_name
            self.log.error(error_msg)
            raise exception.BadValue(error_msg)

        return projectarea_ids

    def checkProjectAreaID(self, projectarea_id, archived=False):
        """Check the validity of :class:`rtcclient.project_area.ProjectArea` id

        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param archived: (default is False) whether the project area is
            archived
        :return: `True` or `False`
        :rtype: bool
        """

        self.log.debug("Check the validity of the ProjectArea id: %s",
                       projectarea_id)

        proj_areas = self._getProjectAreas(archived=archived,
                                           projectarea_id=projectarea_id)
        if proj_areas is not None:
            proj_area = proj_areas[0]
            self.log.info("Find <ProjectArea %s> whose id is: %s",
                          proj_area,
                          projectarea_id)
            return True

        self.log.error("No ProjectArea whose id is: %s",
                       projectarea_id)
        return False

    def getTeamArea(self, teamarea_name, projectarea_id=None,
                    projectarea_name=None, archived=False,
                    returned_properties=None):
        """Get :class:`rtcclient.models.TeamArea` object by its name

        If `projectarea_id` or `projectarea_name` is
        specified, then the matched :class:`rtcclient.models.TeamArea`
        in that project area will be returned.
        Otherwise, only return the first found
        :class:`rtcclient.models.TeamArea` with that name.

        :param teamarea_name: the team area name
        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the project area name
        :param archived: (default is False) whether the team area
            is archived
        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :return: the :class:`rtcclient.models.TeamArea` object
        :rtype: rtcclient.models.TeamArea
        """

        if not isinstance(teamarea_name,
                          six.string_types) or not teamarea_name:
            excp_msg = "Please specify a valid TeamArea name"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        self.log.debug("Try to get <TeamArea %s>", teamarea_name)
        teamareas = self._getTeamAreas(projectarea_id=projectarea_id,
                                       projectarea_name=projectarea_name,
                                       archived=archived,
                                       returned_properties=returned_properties,
                                       teamarea_name=teamarea_name)

        if teamareas is not None:
            teamarea = teamareas[0]
            self.log.info("Find <TeamArea %s>", teamarea)
            return teamarea

        self.log.error("No TeamArea named %s", teamarea_name)
        raise exception.NotFound("No TeamArea named %s" % teamarea_name)

    def getTeamAreas(self, projectarea_id=None, projectarea_name=None,
                     archived=False, returned_properties=None):
        """Get all :class:`rtcclient.models.TeamArea` objects by
        project area id or name

        If both `projectarea_id` and `projectarea_name` are `None`,
        all team areas in all project areas will be returned.

        If no :class:`rtcclient.models.TeamArea` objects are retrieved,
        `None` is returned.

        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the project area name
        :param archived: (default is False) whether the team areas
            are archived
        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :return: a :class:`list` that contains all the
            :class:`rtcclient.models.TeamArea` objects
        :rtype: list
        """

        return self._getTeamAreas(projectarea_id=projectarea_id,
                                  projectarea_name=projectarea_name,
                                  archived=archived,
                                  returned_properties=returned_properties)

    def _getTeamAreas(self, projectarea_id=None, projectarea_name=None,
                      archived=False, returned_properties=None,
                      teamarea_name=None):

        projarea_id = self._pre_get_resource(projectarea_id=projectarea_id,
                                             projectarea_name=projectarea_name)
        rp = returned_properties

        filter_rule = None
        if teamarea_name is not None:
            ftaname_rule = ("dc:title", None, teamarea_name)
            filter_rule = self._add_filter_rule(filter_rule, ftaname_rule)

        return self._get_paged_resources("TeamArea",
                                         projectarea_id=projarea_id,
                                         page_size="100",
                                         archived=archived,
                                         returned_properties=rp,
                                         filter_rule=filter_rule)

    def getOwnedBy(self, email, projectarea_id=None,
                   projectarea_name=None):

        if not isinstance(email, six.string_types) or "@" not in email:
            excp_msg = "Please specify a valid email address name"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        parse_result = urlparse.urlparse(self.url)
        new_path = "/".join(["/jts/users",
                             urlquote(email)])
        new_parse_result = urlparse.ParseResult(scheme=parse_result.scheme,
                                                netloc=parse_result.netloc,
                                                path=new_path,
                                                params=parse_result.params,
                                                query=parse_result.query,
                                                fragment=parse_result.fragment)
        return Member(urlparse.urlunparse(new_parse_result),
                      self)

    def getPlannedFor(self, plannedfor_name, projectarea_id=None,
                      projectarea_name=None, archived=False,
                      returned_properties=None):
        """Get :class:`rtcclient.models.PlannedFor` object by its name

        :param plannedfor_name: the plannedfor name
        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the project area name
        :param archived: (default is False) whether the plannedfor
            is archived
        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :return: the :class:`rtcclient.models.PlannedFor` object
        :rtype: rtcclient.models.PlannedFor
        """

        if not isinstance(plannedfor_name,
                          six.string_types) or not plannedfor_name:
            excp_msg = "Please specify a valid PlannedFor name"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        self.log.debug("Try to get <PlannedFor %s>", plannedfor_name)
        rp = returned_properties
        plannedfors = self._getPlannedFors(projectarea_id=projectarea_id,
                                           projectarea_name=projectarea_name,
                                           archived=archived,
                                           returned_properties=rp,
                                           plannedfor_name=plannedfor_name)

        if plannedfors is not None:
            plannedfor = plannedfors[0]
            self.log.info("Find <PlannedFor %s>", plannedfor)
            return plannedfor

        self.log.error("No PlannedFor named %s", plannedfor_name)
        raise exception.NotFound("No PlannedFor named %s" % plannedfor_name)

    def getPlannedFors(self, projectarea_id=None, projectarea_name=None,
                       archived=False, returned_properties=None):
        """Get all :class:`rtcclient.models.PlannedFor` objects by
        project area id or name

        If both `projectarea_id` and `projectarea_name` are None,
        all the plannedfors in all project areas will be returned.

        If no :class:`rtcclient.models.PlannedFor` objecs are retrieved,
        `None` is returned.

        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the project area name
        :param archived: (default is False) whether the plannedfors
            are archived
        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :return: a :class:`list` that contains all the
            :class:`rtcclient.models.PlannedFor` objects
        :rtype: list
        """

        return self._getPlannedFors(projectarea_id=projectarea_id,
                                    projectarea_name=projectarea_name,
                                    archived=archived,
                                    returned_properties=returned_properties)

    def _getPlannedFors(self, projectarea_id=None, projectarea_name=None,
                        archived=False, returned_properties=None,
                        plannedfor_name=None):

        projarea_id = self._pre_get_resource(projectarea_id=projectarea_id,
                                             projectarea_name=projectarea_name)

        filter_rule = None
        if plannedfor_name is not None:
            fpfname_rule = ("dc:title", None, plannedfor_name)
            filter_rule = self._add_filter_rule(filter_rule, fpfname_rule)

        rp = returned_properties
        return self._get_paged_resources("PlannedFor",
                                         projectarea_id=projarea_id,
                                         page_size="100",
                                         archived=archived,
                                         returned_properties=rp,
                                         filter_rule=filter_rule)

    def getSeverity(self, severity_name, projectarea_id=None,
                    projectarea_name=None):
        """Get :class:`rtcclient.models.Severity` object by its name

        At least either of `projectarea_id` and `projectarea_name` is given

        :param severity_name: the severity name
        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the project area name
        :return: the :class:`rtcclient.models.Severity` object
        :rtype: rtcclient.models.Severity
        """

        self.log.debug("Try to get <Severity %s>", severity_name)
        if not isinstance(severity_name,
                          six.string_types) or not severity_name:
            excp_msg = "Please specify a valid Severity name"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        severities = self._getSeverities(projectarea_id=projectarea_id,
                                         projectarea_name=projectarea_name,
                                         severity_name=severity_name)

        if severities is not None:
            severity = severities[0]
            self.log.info("Find <Severity %s>", severity)
            return severity

        self.log.error("No Severity named %s", severity_name)
        raise exception.NotFound("No Severity named %s" % severity_name)

    def getSeverities(self, projectarea_id=None, projectarea_name=None):
        """Get all :class:`rtcclient.models.Severity` objects by
        project area id or name

        At least either of `projectarea_id` and `projectarea_name` is given

        If no :class:`rtcclient.models.Severity` is retrieved,
        `None` is returned.

        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the project area name
        :return: a :class:`list` that contains all the
            :class:`rtcclient.models.Severity` objects
        :rtype: list
        """

        return self._getSeverities(projectarea_id=projectarea_id,
                                   projectarea_name=projectarea_name)

    def _getSeverities(self, projectarea_id=None, projectarea_name=None,
                       severity_name=None):
        projarea_id = self._pre_get_resource(projectarea_id=projectarea_id,
                                             projectarea_name=projectarea_name)
        if projarea_id is None:
            self.log.error("Please input either-or between "
                           "projectarea_id and projectarea_name")
            raise exception.EmptyAttrib("At least input either-or between "
                                        "projectarea_id and projectarea_name")

        filter_rule = None
        if severity_name is not None:
            fsname_rule = ("dc:title", None, severity_name)
            filter_rule = self._add_filter_rule(filter_rule, fsname_rule)

        return self._get_paged_resources("Severity",
                                         projectarea_id=projarea_id,
                                         page_size="10",
                                         filter_rule=filter_rule)

    def getPriority(self, priority_name, projectarea_id=None,
                    projectarea_name=None):
        """Get :class:`rtcclient.models.Priority` object by its name

        At least either of `projectarea_id` and `projectarea_name` is given

        :param priority_name: the priority name
        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the project area name
        :return: the :class:`rtcclient.models.Priority` object
        :rtype: rtcclient.models.Priority
        """

        self.log.debug("Try to get <Priority %s>", priority_name)
        if not isinstance(priority_name,
                          six.string_types) or not priority_name:
            excp_msg = "Please specify a valid Priority name"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        priorities = self._getPriorities(projectarea_id=projectarea_id,
                                         projectarea_name=projectarea_name,
                                         priority_name=priority_name)

        if priorities is not None:
            priority = priorities[0]
            self.log.info("Find <Priority %s>", priority)
            return priority

        self.log.error("No Priority named %s", priority_name)
        raise exception.NotFound("No Priority named %s" % priority_name)

    def getPriorities(self, projectarea_id=None, projectarea_name=None):
        """Get all :class:`rtcclient.models.Priority` objects by
        project area id or name

        At least either of `projectarea_id` and `projectarea_name` is given.

        If no :class:`rtcclient.models.Priority` is retrieved,
        `None` is returned.

        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the project area name
        :return: a :class:`list` contains all the
            :class:`rtcclient.models.Priority` objects
        :rtype: list
        """

        return self._getPriorities(projectarea_id=projectarea_id,
                                   projectarea_name=projectarea_name)

    def _getPriorities(self, projectarea_id=None, projectarea_name=None,
                       priority_name=None):
        projarea_id = self._pre_get_resource(projectarea_id=projectarea_id,
                                             projectarea_name=projectarea_name)
        if projarea_id is None:
            self.log.error("Please input either-or between "
                           "projectarea_id and projectarea_name")
            raise exception.EmptyAttrib("At least input either-or between "
                                        "projectarea_id and projectarea_name")

        filter_rule = None
        if priority_name is not None:
            fpname_rule = ("dc:title", None, priority_name)
            filter_rule = self._add_filter_rule(filter_rule, fpname_rule)

        return self._get_paged_resources("Priority",
                                         projectarea_id=projarea_id,
                                         page_size="10",
                                         filter_rule=filter_rule)

    def getFoundIn(self, foundin_name, projectarea_id=None,
                   projectarea_name=None, archived=False):
        """Get :class:`rtcclient.models.FoundIn` object by its name

        :param foundin_name: the foundin name
        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the project area name
        :param archived: (default is False) whether the foundin is archived
        :return: the :class:`rtcclient.models.FoundIn` object
        :rtype: rtcclient.models.FoundIn
        """

        self.log.debug("Try to get <FoundIn %s>", foundin_name)
        if not isinstance(foundin_name,
                          six.string_types) or not foundin_name:
            excp_msg = "Please specify a valid PlannedFor name"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        foundins = self._getFoundIns(projectarea_id=projectarea_id,
                                     projectarea_name=projectarea_name,
                                     archived=archived,
                                     foundin_name=foundin_name)

        if foundins is not None:
            foundin = foundins[0]
            self.log.info("Find <FoundIn %s>", foundin)
            return foundin

        self.log.error("No FoundIn named %s", foundin_name)
        raise exception.NotFound("No FoundIn named %s" % foundin_name)

    def getFoundIns(self, projectarea_id=None, projectarea_name=None,
                    archived=False):
        """Get all :class:`rtcclient.models.FoundIn` objects by
        project area id or name

        If both `projectarea_id` and `projectarea_name` are `None`,
        all the foundins in all project areas will be returned.

        If no :class:`rtcclient.models.FoundIn` objects are retrieved,
        `None` is returned.

        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the project area name
        :param archived: (default is False) whether the foundins are archived
        :return: a :class:`list` that contains all the
            :class:`rtcclient.models.FoundIn` objects
        :rtype: list
        """

        return self._getFoundIns(projectarea_id=projectarea_id,
                                 projectarea_name=projectarea_name,
                                 archived=archived)

    def _getFoundIns(self, projectarea_id=None, projectarea_name=None,
                     archived=False, foundin_name=None):
        projarea_id = self._pre_get_resource(projectarea_id=projectarea_id,
                                             projectarea_name=projectarea_name)

        filter_rule = None
        if foundin_name is not None:
            ffname_rule = ("dc:title", None, foundin_name)
            filter_rule = self._add_filter_rule(filter_rule, ffname_rule)
        return self._get_paged_resources("FoundIn",
                                         projectarea_id=projarea_id,
                                         page_size="100",
                                         archived=archived,
                                         filter_rule=filter_rule)

    def getFiledAgainst(self, filedagainst_name, projectarea_id=None,
                        projectarea_name=None, archived=False):
        """Get :class:`rtcclient.models.FiledAgainst` object by its name

        :param filedagainst_name: the filedagainst name
        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the project area name
        :param archived: (default is False) whether the filedagainst is
            archived
        :return: the :class:`rtcclient.models.FiledAgainst` object
        :rtype: rtcclient.models.FiledAgainst
        """

        self.log.debug("Try to get <FiledAgainst %s>", filedagainst_name)
        if not isinstance(filedagainst_name,
                          six.string_types) or not filedagainst_name:
            excp_msg = "Please specify a valid FiledAgainst name"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        fas = self._getFiledAgainsts(projectarea_id=projectarea_id,
                                     projectarea_name=projectarea_name,
                                     archived=archived,
                                     filedagainst_name=filedagainst_name)

        if fas is not None:
            filedagainst = fas[0]
            self.log.info("Find <FiledAgainst %s>", filedagainst)
            return filedagainst

        error_msg = "No FiledAgainst named %s" % filedagainst_name
        self.log.error(error_msg)
        raise exception.NotFound(error_msg)

    def getFiledAgainsts(self, projectarea_id=None, projectarea_name=None,
                         archived=False):
        """Get all :class:`rtcclient.models.FiledAgainst` objects by
        project area id or name

        If both `projectarea_id` and `projectarea_name` are `None`,
        all the filedagainsts in all project areas will be returned.

        If no :class:`rtcclient.models.FiledAgainst` objects are retrieved,
        `None` is returned.

        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the project area name
        :param archived: (default is False) whether the filedagainsts are
            archived
        :return: a :class:`list` that contains all the
            :class:`rtcclient.models.FiledAgainst` objects
        :rtype: list
        """

        return self._getFiledAgainsts(projectarea_id=projectarea_id,
                                      projectarea_name=projectarea_name,
                                      archived=archived)

    def _getFiledAgainsts(self, projectarea_id=None, projectarea_name=None,
                          archived=False, filedagainst_name=None):
        projarea_id = self._pre_get_resource(projectarea_id=projectarea_id,
                                             projectarea_name=projectarea_name)

        filter_rule = None
        if filedagainst_name is not None:
            ffaname_rule = ("dc:title", None, filedagainst_name)
            filter_rule = self._add_filter_rule(filter_rule, ffaname_rule)
        return self._get_paged_resources("FiledAgainst",
                                         projectarea_id=projarea_id,
                                         page_size="100",
                                         archived=archived,
                                         filter_rule=filter_rule)

    def getTemplate(self, copied_from, template_name=None,
                    template_folder=None, keep=False, encoding="UTF-8"):
        """Get template from some to-be-copied workitems

        More details, please refer to
        :class:`rtcclient.template.Templater.getTemplate`
        """

        return self.templater.getTemplate(copied_from,
                                          template_name=template_name,
                                          template_folder=template_folder,
                                          keep=keep,
                                          encoding=encoding)

    def getTemplates(self, workitems, template_folder=None,
                     template_names=None, keep=False, encoding="UTF-8"):
        """Get templates from a group of to-be-copied workitems
        and write them to files named after the names in `template_names`
        respectively.

        More details, please refer to
        :class:`rtcclient.template.Templater.getTemplates`
        """

        self.templater.getTemplates(workitems,
                                    template_folder=template_folder,
                                    template_names=template_names,
                                    keep=keep,
                                    encoding=encoding)

    def listFields(self, template):
        """List all the attributes to be rendered from the template file

        :param template: The template to render.
            The template is actually a file, which is usually generated
            by :class:`rtcclient.template.Templater.getTemplate` and can also
            be modified by user accordingly.
        :return: a :class:`set` that contains all the needed attributes
        :rtype: set

        More details, please refer to
        :class:`rtcclient.template.Templater.listFieldsFromWorkitem`
        """

        return self.templater.listFields(template)

    def listFieldsFromWorkitem(self, copied_from, keep=False):
        """List all the attributes to be rendered directly from some
        to-be-copied workitems

        More details, please refer to
        :class:`rtcclient.template.Templater.listFieldsFromWorkitem`
        """

        return self.templater.listFieldsFromWorkitem(copied_from,
                                                     keep=keep)

    def getWorkitem(self, workitem_id, returned_properties=None):
        """Get :class:`rtcclient.workitem.Workitem` object by its id/number

        :param workitem_id: the workitem id/number
            (integer or equivalent string)
        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :return: the :class:`rtcclient.workitem.Workitem` object
        :rtype: rtcclient.workitem.Workitem
        """

        try:
            if isinstance(workitem_id, bool):
                raise ValueError("Invalid Workitem id")
            if isinstance(workitem_id, six.string_types):
                workitem_id = int(workitem_id)
            if not isinstance(workitem_id, int):
                raise ValueError("Invalid Workitem id")

            workitem_url = "/".join([self.url,
                                     "oslc/workitems/%s" % workitem_id])

            rp = self._validate_returned_properties(returned_properties)
            if rp is not None:
                req_url = "".join([workitem_url,
                                   "?oslc_cm.properties=",
                                   urlquote(rp)])
            else:
                req_url = workitem_url
            resp = self.get(req_url,
                            verify=False,
                            proxies=self.proxies,
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
        except Exception as excp:
            self.log.error(excp)
            raise exception.NotFound("Not found <Workitem %s>" % workitem_id)

    def getWorkitems(self, projectarea_id=None, projectarea_name=None,
                     returned_properties=None, archived=False):
        """Get all :class:`rtcclient.workitem.Workitem` objects by
        project area id or name

        If both `projectarea_id` and `projectarea_name` are `None`,
        all the workitems in all project areas will be returned.

        If no :class:`rtcclient.workitem.Workitem` objects are retrieved,
        `None` is returned.

        You can also customize your preferred properties to be returned
        by specified `returned_properties`

        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the project area name
        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :param archived: (default is False) whether the workitems are archived
        :return: a :class:`list` that contains all the
            :class:`rtcclient.workitem.Workitem` objects
        :rtype: list
        """

        workitems_list = list()
        projectarea_ids = list()
        if not isinstance(projectarea_id,
                          six.string_types) or not projectarea_id:
            pa_ids = self.getProjectAreaIDs(projectarea_name)
            if pa_ids is None:
                self.log.warning("Stop getting workitems because of "
                                 "no ProjectAreas")
                return None
            projectarea_ids.extend(pa_ids)
        else:
            if self.checkProjectAreaID(projectarea_id):
                projectarea_ids.append(projectarea_id)
            else:
                raise exception.BadValue("Invalid ProjectAred ID: "
                                         "%s" % projectarea_id)

        self.log.warning("For a single ProjectArea, only latest 1000 "
                         "workitems can be fetched. "
                         "This may be a bug of Rational Team Concert")

        rp = self._validate_returned_properties(returned_properties)
        for projarea_id in projectarea_ids:
            workitems = self._get_paged_resources("Workitem",
                                                  projectarea_id=projarea_id,
                                                  page_size="100",
                                                  returned_properties=rp,
                                                  archived=archived)
            if workitems is not None:
                workitems_list.extend(workitems)

        if not workitems_list:
            self.log.warning("Cannot find a workitem in the ProjectAreas "
                             "with ids: %s" % projectarea_ids)
            return None
        return workitems_list

    def _validate_returned_properties(self, returned_properties=None):
        if returned_properties is not None:
            # retrieve project area info and state
            # indispensable for some methods in class Workitem
            mandatory_strs = ["rtc_cm:state", "rtc_cm:contextId"]
            for mandatory_str in mandatory_strs:
                if mandatory_str not in returned_properties:
                    returned_properties += ",%s" % mandatory_str
        return returned_properties

    def createWorkitem(self, item_type, title, description=None,
                       projectarea_id=None, projectarea_name=None,
                       template=None, copied_from=None, keep=False,
                       **kwargs):
        """Create a workitem

        :param item_type: the type of the workitem
            (e.g. task/defect/issue)
        :param title: the title of the new created workitem
        :param description: the description of the new created workitem
        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the project area name
        :param template: The template to render.
            The template is actually a file, which is usually generated
            by :class:`rtcclient.template.Templater.getTemplate` and can also
            be modified by user accordingly.
        :param copied_from: the to-be-copied workitem id
        :param keep: refer to `keep` in
            :class:`rtcclient.template.Templater.getTemplate`. Only works when
            `template` is not specified
        :param kwargs: Optional/mandatory arguments when creating a new
            workitem. More details, please refer to `kwargs` in
            :class:`rtcclient.template.Templater.render`
        :return: the :class:`rtcclient.workitem.Workitem` object
        :rtype: rtcclient.workitem.Workitem
        """

        if not isinstance(projectarea_id,
                          six.string_types) or not projectarea_id:
            projectarea = self.getProjectArea(projectarea_name)
            projectarea_id = projectarea.id
        else:
            projectarea = self.getProjectAreaByID(projectarea_id)

        itemtype = projectarea.getItemType(item_type)

        if not template:
            if not copied_from:
                self.log.error("Please choose either-or between "
                               "template and copied_from")
                raise exception.EmptyAttrib("At least choose either-or "
                                            "between template and copied_from")

            self._checkMissingParamsFromWorkitem(copied_from, keep=keep,
                                                 **kwargs)
            kwargs = self._retrieveValidInfo(projectarea_id,
                                             **kwargs)
            wi_raw = self.templater.renderFromWorkitem(copied_from,
                                                       keep=keep,
                                                       encoding="UTF-8",
                                                       title=title,
                                                       description=description,
                                                       **kwargs)

        else:
            self._checkMissingParams(template, **kwargs)
            kwargs = self._retrieveValidInfo(projectarea_id,
                                             **kwargs)
            wi_raw = self.templater.render(template,
                                           title=title,
                                           description=description,
                                           **kwargs)

        self.log.info("Start to create a new <%s> with raw data: %s",
                      item_type, wi_raw)

        wi_url_post = "/".join([self.url,
                                "oslc/contexts",
                                projectarea_id,
                                "workitems/%s" % itemtype.identifier])
        return self._createWorkitem(wi_url_post, wi_raw)

    def copyWorkitem(self, copied_from, title=None, description=None,
                     prefix=None):
        """Create a workitem by copying from an existing one

        :param copied_from: the to-be-copied workitem id
        :param title: the new workitem title/summary.
            If `None`, will copy that from a to-be-copied workitem
        :param description: the new workitem description.
            If `None`, will copy that from a to-be-copied workitem
        :param prefix: used to add a prefix to the copied title and
            description
        :return: the :class:`rtcclient.workitem.Workitem` object
        :rtype: rtcclient.workitem.Workitem
        """

        copied_wi = self.getWorkitem(copied_from)
        if title is None:
            title = copied_wi.title
            if prefix is not None:
                title = prefix + title

        if description is None:
            description = copied_wi.description
            if prefix is not None:
                description = prefix + description

        self.log.info("Start to create a new <Workitem>, copied from "
                      "<Workitem %s>", copied_from)

        projectarea = self.getProjectAreaByID(copied_wi.contextId)
        itemtype = projectarea.getItemType(copied_wi.type)

        wi_url_post = "/".join([self.url,
                                "oslc/contexts/%s" % copied_wi.contextId,
                                "workitems",
                                "%s" % itemtype.identifier])
        wi_raw = self.templater.renderFromWorkitem(copied_from,
                                                   keep=True,
                                                   encoding="UTF-8",
                                                   title=title,
                                                   description=description)
        return self._createWorkitem(wi_url_post, wi_raw)

    def _createWorkitem(self, url_post, workitem_raw):
        headers = copy.deepcopy(self.headers)
        headers['Content-Type'] = self.OSLC_CR_XML

        resp = self.post(url_post, verify=False,
                         headers=headers, proxies=self.proxies,
                         data=workitem_raw)

        raw_data = xmltodict.parse(resp.content)
        workitem_raw = raw_data["oslc_cm:ChangeRequest"]
        workitem_id = workitem_raw["dc:identifier"]
        workitem_url = "/".join([self.url,
                                 "oslc/workitems/%s" % workitem_id])
        new_wi = Workitem(workitem_url,
                          self,
                          workitem_id=workitem_id,
                          raw_data=raw_data["oslc_cm:ChangeRequest"])

        self.log.info("Successfully create <Workitem %s>" % new_wi)
        return new_wi

    def _checkMissingParams(self, template, **kwargs):
        """Check the missing parameters for rendering from the template file
        """

        parameters = self.listFields(template)
        self._findMissingParams(parameters, **kwargs)

    def _checkMissingParamsFromWorkitem(self, copied_from, keep=False,
                                        **kwargs):
        """Check the missing parameters for rendering directly from the
        copied workitem
        """

        parameters = self.listFieldsFromWorkitem(copied_from,
                                                 keep=keep)
        self._findMissingParams(parameters, **kwargs)

    def _retrieveValidInfo(self, projectarea_id, **kwargs):
        # get rdf:resource by keywords
        for keyword in kwargs.keys():
            try:
                keyword_cls = eval("self.get" + capitalize(keyword))
                keyword_obj = keyword_cls(kwargs[keyword],
                                          projectarea_id=projectarea_id)
                kwargs[keyword] = keyword_obj.url
            except Exception as excp:
                self.log.error(excp)
        return kwargs

    def _findMissingParams(self, parameters, **kwargs):
        known_parameters = ["title", "description"]
        for known_parameter in known_parameters:
            try:
                parameters.remove(known_parameter)
            except KeyError:
                continue

        input_attributes = set(kwargs.keys())
        missing_attributes = parameters.difference(input_attributes)
        if bool(missing_attributes):
            error_msg = "Missing Parameters: %s" % list(missing_attributes)
            self.log.error(error_msg)
            raise exception.EmptyAttrib(error_msg)
        else:
            self.log.debug("No missing parameters")

    def checkType(self, item_type, projectarea_id):
        """Check the validity of :class:`rtcclient.workitem.Workitem` type

        :param item_type: the type of the workitem
            (e.g. Story/Defect/Epic)
        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :return: `True` or `False`
        :rtype: bool
        """

        self.log.debug("Checking the validity of workitem type: %s",
                       item_type)
        try:
            project_area = self.getProjectAreaByID(projectarea_id)
            if project_area.getItemType(item_type):
                return True
            else:
                return False
        except (exception.NotFound, exception.BadValue):
            self.log.error("Invalid ProjectArea name")
            return False

    def _pre_get_resource(self, projectarea_id=None, projectarea_name=None):
        if projectarea_id is None:
            if projectarea_name is not None:
                return self.getProjectAreaID(projectarea_name)
            return None
        else:
            if not self.checkProjectAreaID(projectarea_id):
                raise exception.BadValue("Invalid ProjectArea id")
            return projectarea_id

    def _get_paged_resources(self, resource_name, projectarea_id=None,
                             workitem_id=None, customized_attr=None,
                             page_size="100", archived=False,
                             returned_properties=None, filter_rule=None):
        # TODO: multi-thread

        self.log.debug("Start to fetch all %ss with [ProjectArea ID: %s] "
                       "and [archived=%s]",
                       resource_name,
                       projectarea_id if projectarea_id else "not specified",
                       archived)

        projectarea_required = ["Workitem",
                                "Severity",
                                "Priority",
                                "Member",
                                "Administrator",
                                "ItemType",
                                "Action",
                                "Query",
                                "State"]
        workitem_required = ["Comment",
                             "Subscriber",
                             "IncludedInBuild",
                             "Parent",
                             "Children",
                             "ChangeSet",
                             "Attachment"]
        customized_required = ["Action",
                               "Query",
                               "State",
                               "RunQuery",
                               "IncludedInBuild",
                               "Parent",
                               "Children",
                               "ChangeSet",
                               "Attachment"]

        if resource_name in projectarea_required and not projectarea_id:
            self.log.error("No ProjectArea ID is specified")
            raise exception.EmptyAttrib("No ProjectArea ID")

        if resource_name in workitem_required and not workitem_id:
            self.log.error("No Workitem ID is specified")
            raise exception.EmptyAttrib("No Workitem ID")

        if resource_name in customized_required and not customized_attr:
            self.log.error("No customized value is specified")
            raise exception.EmptyAttrib("No customized value")

        res_map = {"TeamArea": "teamareas",
                   "ProjectArea": "projectareas",
                   "FiledAgainst": "categories",
                   "FoundIn": "deliverables",
                   "PlannedFor": "iterations",
                   "ItemType": "types/%s" % projectarea_id,
                   "Member": "projectareas/%s/rtc_cm:members" % projectarea_id,
                   "Administrator": "/".join(["projectareas",
                                              "%s" % projectarea_id,
                                              "rtc_cm:administrators"]),
                   "Workitem": "contexts/%s/workitems" % projectarea_id,
                   "Severity": "enumerations/%s/severity" % projectarea_id,
                   "Priority": "enumerations/%s/priority" % projectarea_id,
                   "Comment": "workitems/%s/rtc_cm:comments" % workitem_id,
                   "Subscriber": "/".join(["workitems",
                                           "%s" % workitem_id,
                                           "rtc_cm:subscribers"]),
                   "Action": "workflows/%s/actions/%s" % (projectarea_id,
                                                          customized_attr),
                   "Query": "".join(["contexts/%s/workitems" % projectarea_id,
                                     "?oslc_cm.query=%s" % customized_attr]),
                   "State": "workflows/%s/states/%s" % (projectarea_id,
                                                        customized_attr),
                   "SavedQuery": "queries",
                   "RunQuery": "queries/%s/rtc_cm:results" % customized_attr,
                   "IncludedInBuild": "workitems/%s/%s" % (workitem_id,
                                                           customized_attr),
                   "Parent": "workitems/%s/%s" % (workitem_id,
                                                  customized_attr),
                   "Children": "workitems/%s/%s" % (workitem_id,
                                                    customized_attr),
                   "ChangeSet": "workitems/%s/%s" % (workitem_id,
                                                     customized_attr),
                   "Attachment": "workitems/%s/%s" % (workitem_id,
                                                      customized_attr),
                   }

        entry_map = {"TeamArea": "rtc_cm:Team",
                     "ProjectArea": "rtc_cm:Project",
                     "FiledAgainst": "rtc_cm:Category",
                     "FoundIn": "rtc_cm:Deliverable",
                     "PlannedFor": "rtc_cm:Iteration",
                     "ItemType": "rtc_cm:Type",
                     "Member": "rtc_cm:User",
                     "Administrator": "rtc_cm:User",
                     "Workitem": "oslc_cm:ChangeRequest",
                     "Severity": "rtc_cm:Literal",
                     "Priority": "rtc_cm:Literal",
                     "Comment": "rtc_cm:Comment",
                     "Subscriber": "rtc_cm:User",
                     "Action": "rtc_cm:Action",
                     "Query": "oslc_cm:ChangeRequest",
                     "State": "rtc_cm:Status",
                     "SavedQuery": "rtc_cm:Query",
                     "RunQuery": "oslc_cm:ChangeRequest",
                     "IncludedInBuild": "oslc_auto:AutomationResult",
                     "Parent": "oslc_cm:ChangeRequest",
                     "Children": "oslc_cm:ChangeRequest",
                     "ChangeSet": "rtc_cm:Reference",
                     "Attachment": "rtc_cm:Attachment"
                     }

        if resource_name not in res_map:
            self.log.error("Unsupported resource name")
            raise exception.BadValue("Unsupported resource name")

        resource_url = "".join([self.url,
                                "/oslc/{0}",
                                "?" if resource_name != "Query"
                                else "&",
                                "oslc_cm.pageSize={1}&_startIndex=0"])

        resource_url = resource_url.format(res_map[resource_name],
                                           page_size)

        if returned_properties is not None:
            if not isinstance(returned_properties, six.string_types):
                raise exception.BadValue("returned_properties is not a"
                                         "valid string")
            resource_url = "".join([resource_url,
                                    "&oslc_cm.properties=",
                                    urlquote(returned_properties)])

        pa_url = ("/".join([self.url,
                            "oslc/projectareas",
                            projectarea_id])
                  if projectarea_id else None)

        resp = self.get(resource_url,
                        verify=False,
                        proxies=self.proxies,
                        headers=self.headers)
        raw_data = xmltodict.parse(resp.content)

        try:
            total_count = int(raw_data.get("oslc_cm:Collection")
                                      .get("@oslc_cm:totalCount"))
            if total_count == 0:
                self.log.warning("No %ss are found", resource_name)
                return None
        except:
            pass

        resources_list = []

        while True:
            entries = (raw_data.get("oslc_cm:Collection")
                               .get(entry_map[resource_name]))

            if entries is None:
                break

            # for the last single entry
            if isinstance(entries, OrderedDict):
                resource = self._handle_resource_entry(resource_name,
                                                       entries,
                                                       projectarea_url=pa_url,
                                                       archived=archived,
                                                       filter_rule=filter_rule)
                if resource is not None:
                    resources_list.append(resource)
                break

            # iterate all the entries
            for entry in entries:
                resource = self._handle_resource_entry(resource_name,
                                                       entry,
                                                       projectarea_url=pa_url,
                                                       archived=archived,
                                                       filter_rule=filter_rule)
                if resource is not None:
                    resources_list.append(resource)

            # find the next page
            url_next = raw_data.get('oslc_cm:Collection').get('@oslc_cm:next')
            if url_next:
                resp = self.get(url_next,
                                verify=False,
                                proxies=self.proxies,
                                headers=self.headers)
                raw_data = xmltodict.parse(resp.content)
            else:
                break

        if not resources_list:
            self.log.warning("No %ss are found with [ProjectArea ID: %s] "
                             "and [archived=%s]",
                             resource_name,
                             projectarea_id if projectarea_id
                             else "not specified",
                             archived)
            return None

        self.log.debug("Successfully fetching all the paged resources")
        return resources_list

    def _handle_resource_entry(self, resource_name, entry,
                               projectarea_url=None, archived=False,
                               filter_rule=None):
        """
        :param filter_rule: a list of filter rules
            e.g. filter_rule = [("dc:creator", "@rdf:resource",
                                 "https://test.url:9443/jts/users/me%40mail"),
                                ("dc:modified", None,
                                 "2013-08-28T02:06:26.516Z")
                                ]
            only the entry matches all the rules will be kept
        """

        if projectarea_url is not None:
            try:
                if (entry.get("rtc_cm:projectArea")
                         .get("@rdf:resource")) != projectarea_url:
                    return None
            except AttributeError:
                pass

        if filter_rule is not None:
            # match all the filter rules
            for frule in filter_rule:
                fattr, rdf_resource, fvalue = frule
                try:
                    if rdf_resource is not None:
                        frule_value = entry.get(fattr).get(rdf_resource)
                    else:
                        frule_value = entry.get(fattr)

                    if frule_value != fvalue:
                        return None
                except AttributeError:
                    pass

        entry_archived = entry.get("rtc_cm:archived")
        if (entry_archived is not None and
                eval(entry_archived.capitalize()) != archived):
            return None

        if resource_name == "Subscriber":
            resource_cls = Member
        elif resource_name in ["Query", "RunQuery", "Parent", "Children"]:
            resource_cls = Workitem
        else:
            resource_cls = eval(resource_name)

        if resource_name in ["Workitem",
                             "Query",
                             "RunQuery",
                             "Parent",
                             "Children"]:
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

    def queryWorkitems(self, query_str, projectarea_id=None,
                       projectarea_name=None, returned_properties=None,
                       archived=False):
        """Query workitems with the query string in a certain project area

        At least either of `projectarea_id` and `projectarea_name` is given

        :param query_str: a valid query string
        :param projectarea_id: the :class:`rtcclient.project_area.ProjectArea`
            id
        :param projectarea_name: the project area name
        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :param archived: (default is False) whether the workitems are archived
        :return: a :class:`list` that contains the queried
            :class:`rtcclient.workitem.Workitem` objects
        :rtype: list
        """

        rp = returned_properties
        return self.query.queryWorkitems(query_str=query_str,
                                         projectarea_id=projectarea_id,
                                         projectarea_name=projectarea_name,
                                         returned_properties=rp,
                                         archived=archived)
