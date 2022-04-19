import logging

import six
import xmltodict

from rtcclient import exception
from rtcclient.base import FieldBase
from rtcclient.models import Role


class ProjectArea(FieldBase):
    """A wrapped class to perform all the operations in a Project Area

    :param url: the project area url
    :param rtc_obj: a reference to the
        :class:`rtcclient.client.RTCClient` object
    :param raw_data: the raw data ( OrderedDict ) of the request response

    """

    log = logging.getLogger("project_area.ProjectArea")

    def __init__(self, url, rtc_obj, raw_data):
        FieldBase.__init__(self, url, rtc_obj, raw_data)
        self.id = self.url.split("/")[-1]

    def __str__(self):
        return self.title

    def _initialize(self):
        """Request to get response"""

        self.log.error("For ProjectArea, raw_data is mandatory")
        raise exception.EmptyAttrib("Please input raw_data")

    def getRoles(self):
        """Get all :class:`rtcclient.models.Role` objects in this project
        area

        If no :class:`Roles` are retrieved, `None` is returned.

        :return: a :class:`list` that contains all
            :class:`rtcclient.models.Role` objects
        :rtype: list
        """

        # no need to retrieve all the entries from _get_paged_resources
        # role raw data is very simple that contains no other links

        self.log.info("Get all the roles in <ProjectArea %s>", self)
        roles_url = "/".join(
            [self.rtc_obj.url,
             "process/project-areas/%s/roles" % self.id])
        resp = self.get(roles_url,
                        verify=False,
                        proxies=self.rtc_obj.proxies,
                        headers=self.rtc_obj.headers)

        roles_list = list()
        raw_data = xmltodict.parse(resp.content)
        roles_raw = raw_data['jp06:roles']['jp06:role']
        if not roles_raw:
            self.log.warning("There are no roles in <ProjectArea %s>", self)
            return None

        for role_raw in roles_raw:
            role = Role(role_raw.get("jp06:url"),
                        self.rtc_obj,
                        raw_data=role_raw)
            roles_list.append(role)
        return roles_list

    def getRole(self, label):
        """Get the :class:`rtcclient.models.Role` object by the label name

        :param label: the label name of the role
        :return: the :class:`rtcclient.models.Role` object
        :rtype: :class:`rtcclient.models.Role`
        """

        if not isinstance(label, six.string_types) or not label:
            excp_msg = "Please specify a valid role label"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        roles = self.getRoles()
        if roles is not None:
            for role in roles:
                if role.label == label:
                    self.log.info("Get <Role %s> in <ProjectArea %s>", role,
                                  self)
                    return role

        excp_msg = "No role's label is %s in <ProjectArea %s>" % (label, self)
        self.log.error(excp_msg)
        raise exception.NotFound(excp_msg)

    def getMembers(self, returned_properties=None):
        """Get all the :class:`rtcclient.models.Member` objects in this
        project area

        If no :class:`Members` are retrieved, `None` is returned.

        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :return: a :class:`list` that contains all
            :class:`rtcclient.models.Member` objects
        :rtype: list
        """

        return self._getMembers(returned_properties=returned_properties)

    def getMember(self, email, returned_properties=None):
        """Get the :class:`rtcclient.models.Member` object by the
        email address

        :param email: the email address (e.g. somebody@gmail.com)
        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :return: the :class:`rtcclient.models.Member` object
        :rtype: rtcclient.models.Member
        """

        if not isinstance(email, six.string_types) or "@" not in email:
            excp_msg = "Please specify a valid email address name"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        self.log.debug("Try to get Member whose email is %s>", email)
        members = self._getMembers(returned_properties=returned_properties,
                                   email=email)
        if members is not None:
            member = members[0]
            self.log.info("Get <Member %s> in <ProjectArea %s>", member, self)
            return member

        excp_msg = "No member's email is %s in <ProjectArea %s>" % (email, self)
        self.log.error(excp_msg)
        raise exception.NotFound(excp_msg)

    def _getMembers(self, returned_properties=None, email=None):
        self.log.warning("If you are not listed, please contact your RTC "
                         "administrators to add you as a team member")
        rp = returned_properties
        filter_rule = None
        if email is not None:
            fmember_rule = ("rtc_cm:userId", None, email)
            filter_rule = self.rtc_obj._add_filter_rule(filter_rule,
                                                        fmember_rule)
        return self.rtc_obj._get_paged_resources("Member",
                                                 projectarea_id=self.id,
                                                 page_size='100',
                                                 returned_properties=rp,
                                                 filter_rule=filter_rule)

    def getItemTypes(self, returned_properties=None):
        """Get all the :class:`rtcclient.models.ItemType` objects
        in this project area

        If no :class:`ItemTypes` are retrieved, `None` is returned.

        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :return: a :class:`list` that contains all
            :class:`rtcclient.models.ItemType` objects
        :rtype: list
        """

        return self._getItemTypes(returned_properties=returned_properties)

    def getItemType(self, title, returned_properties=None):
        """Get the :class:`rtcclient.models.ItemType` object by the title

        :param title: the title (e.g. Story/Epic/..)
        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :return: the :class:`rtcclient.models.ItemType` object
        :rtype: rtcclient.models.ItemType
        """

        if not isinstance(title, six.string_types) or not title:
            excp_msg = "Please specify a valid email address name"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        self.log.debug("Try to get <ItemType %s>", title)
        itemtypes = self._getItemTypes(returned_properties=returned_properties,
                                       title=title)
        if itemtypes is not None:
            itemtype = itemtypes[0]
            self.log.info("Get <ItemType %s> in <ProjectArea %s>", itemtype,
                          self)
            return itemtype

        excp_msg = "No itemtype's name is %s in <ProjectArea %s>" % (title,
                                                                     self)
        self.log.error(excp_msg)
        raise exception.NotFound(excp_msg)

    def _getItemTypes(self, returned_properties=None, title=None):
        rp = returned_properties
        filter_rule = None
        if title is not None:
            fit_rule = ("dc:title", None, title)
            filter_rule = self.rtc_obj._add_filter_rule(filter_rule, fit_rule)
        return self.rtc_obj._get_paged_resources("ItemType",
                                                 projectarea_id=self.id,
                                                 page_size='10',
                                                 returned_properties=rp,
                                                 filter_rule=filter_rule)

    def getAdministrators(self, returned_properties=None):
        """Get all the :class:`rtcclient.models.Administrator` objects in this
        project area

        If no :class:`Administrators` are retrieved,
        `None` is returned.

        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :return: a :class:`list` that contains all
            :class:`rtcclient.models.Administrator` objects
        :rtype: list
        """

        return self._getAdministrators(returned_properties=returned_properties)

    def getAdministrator(self, email, returned_properties=None):
        """Get the :class:`rtcclient.models.Administrator` object
        by the email address

        :param email: the email address (e.g. somebody@gmail.com)
        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :return: the :class:`rtcclient.models.Administrator` object
        :rtype: rtcclient.models.Administrator
        """

        if not isinstance(email, six.string_types) or "@" not in email:
            excp_msg = "Please specify a valid email address name"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        self.log.debug("Try to get Administrator whose email is %s", email)
        rp = returned_properties
        administrators = self._getAdministrators(returned_properties=rp,
                                                 email=email)
        if administrators is not None:
            administrator = administrators[0]
            self.log.info("Get <Administrator %s> in <ProjectArea %s>",
                          administrator, self)
            return administrator

        msg = "No administrator's email is %s in <ProjectArea %s>" % (email,
                                                                      self)
        self.log.error(msg)
        raise exception.NotFound(msg)

    def _getAdministrators(self, returned_properties=None, email=None):
        rp = returned_properties
        filter_rule = None
        if email is not None:
            fadmin_rule = ("rtc_cm:userId", None, email)
            filter_rule = self.rtc_obj._add_filter_rule(filter_rule,
                                                        fadmin_rule)
        return self.rtc_obj._get_paged_resources("Administrator",
                                                 projectarea_id=self.id,
                                                 page_size='10',
                                                 returned_properties=rp,
                                                 filter_rule=filter_rule)
