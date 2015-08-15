from rtcclient.base import FieldBase
import xmltodict
from rtcclient import urlunquote
import logging
from rtcclient import exception


class ProjectArea(FieldBase):
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
        """Get all Role objects in this project area

        If no Roles are retrieved, None is returned.

        :return: a list contains all `Role <Role>` objects
        :rtype: list
        """

        self.log.info("Get all the roles in <ProjectArea %s>",
                      self)
        roles_url = "/".join([self.rtc_obj.url,
                              "process/project-areas/%s/roles" % self.id])
        resp = self.get(roles_url,
                        verify=False,
                        headers=self.rtc_obj.headers)

        roles_list = list()
        raw_data = xmltodict.parse(resp.content)
        roles_raw = raw_data['jp06:roles']['jp06:role']
        if not roles_raw:
            self.log.warning("There are no roles in <ProjectArea %s>",
                             self)
            return None

        for role_raw in roles_raw:
            role = Role(role_raw.get("jp06:url"),
                        self.rtc_obj,
                        raw_data=role_raw)
            roles_list.append(role)
        return roles_list

    def getRole(self, label):
        """Get the Role object by the label name

        :param label: the role label name
        :return: :class:`Role <Role>` object
        :rtype: project_area.Role
        """

        roles = self.getRoles()
        if roles is not None:
            for role in roles:
                if role.label == label:
                    self.log.info("Get <Role %s> in <ProjectArea %s>",
                                  role, self)
                    return role

        excp_msg = "No role's label is %s in <ProjectArea %s>" % (label,
                                                                  self)
        self.log.error(excp_msg)
        raise exception.NotFound(excp_msg)

    def getMembers(self, returned_properties=None):
        """Get all the Member objects in this project area

        If no Members are retrieved, None is returned.

        :param returned_properties: the returned properties that you want
            Refer to class `RTCClient` for more explanations
        :return: a list contains all `Member <Member>` objects
        :rtype: list
        """

        self.log.warning("Currently RTC cannot correctly list all the "
                         "members that belong to the ProjectArea")
        rp = returned_properties
        return self.rtc_obj._get_paged_resources("Member",
                                                 projectarea_id=self.id,
                                                 page_size='100',
                                                 returned_properties=rp)

    def getMember(self, email, returned_properties=None):
        """Get the Member object by the email address

        :param email: the email addr (e.g. somebody@gmail.com)
        :param returned_properties: the returned properties that you want
            Refer to class `RTCClient` for more explanations
        :return: :class:`Member <Member>` object
        :rtype: project_area.Member
        """

        if not isinstance(email, str) or "@" not in email:
            excp_msg = "Please specify a valid email address name"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        members = self.getMembers(returned_properties=returned_properties)
        self.log.warning("Some members that do exist in or belong to"
                         "the ProjectArea may cannot be retrieved")
        self.log.warning("This is an existing bug of RTC")

        self.log.debug("Try to get Member whose email is %s>", email)
        if members is not None:
            for member in members:
                if member.email == email:
                    self.log.info("Get <Member %s> in <ProjectArea %s>",
                                  member, self)
                    return member

        excp_msg = "No member's email is %s in <ProjectArea %s>" % (email,
                                                                    self)
        self.log.error(excp_msg)
        raise exception.NotFound(excp_msg)

    def getItemTypes(self, returned_properties=None):
        """Get all the ItemType objects in this project area

        If no ItemTypes are retrieved, None is returned.

        :param returned_properties: the returned properties that you want
            Refer to class `RTCClient` for more explanations
        :return: a list contains all `ItemType <ItemType>` objects
        :rtype: list
        """

        rp = returned_properties
        return self.rtc_obj._get_paged_resources("ItemType",
                                                 projectarea_id=self.id,
                                                 page_size='10',
                                                 returned_properties=rp)

    def getItemType(self, title, returned_properties=None):
        """Get the ItemType object by the title

        :param title: the title (e.g. Story/Epic/..)
        :param returned_properties: the returned properties that you want
            Refer to class `RTCClient` for more explanations
        :return: :class:`ItemType <ItemType>` object
        :rtype: project_area.ItemType
        """

        if not isinstance(title, str) or not title:
            excp_msg = "Please specify a valid email address name"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        itemtypes = self.getItemTypes(returned_properties=returned_properties)
        self.log.debug("Try to get <ItemType %s>", title)
        if itemtypes is not None:
            for itemtype in itemtypes:
                if itemtype.title == title:
                    self.log.info("Get <ItemType %s> in <ProjectArea %s>",
                                  itemtype, self)
                    return itemtype

        excp_msg = "No itemtype's name is %s in <ProjectArea %s>" % (title,
                                                                     self)
        self.log.error(excp_msg)
        raise exception.NotFound(excp_msg)

    def getAdministrators(self, returned_properties=None):
        """Get all the Administrator objects in this project area

        If no Administrators are retrieved, None is returned.

        :param returned_properties: the returned properties that you want
            Refer to class `RTCClient` for more explanations
        :return: a list contains all `Administrator <Administrator>` objects
        :rtype: list
        """

        rp = returned_properties
        return self.rtc_obj._get_paged_resources("Administrator",
                                                 projectarea_id=self.id,
                                                 page_size='10',
                                                 returned_properties=rp)

    def getAdministrator(self, email, returned_properties=None):
        """Get the <Administrator> object by the email address

        :param email: the email addr (e.g. somebody@gmail.com)
        :param returned_properties: the returned properties that you want
            Refer to class `RTCClient` for more explanations
        :return: :class:`Administrator <Administrator>` object
        :rtype: project_area.Administrator
        """

        if not isinstance(email, str) or "@" not in email:
            excp_msg = "Please specify a valid email address name"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        rp = returned_properties
        administrators = self.getAdministrators(returned_properties=rp)
        self.log.debug("Try to get Administrator whose email is %s",
                       email)
        if administrators is not None:
            for administrator in administrators:
                if administrator.email == email:
                    self.log.info("Get <Administrator %s> in <ProjectArea %s>",
                                  administrator, self)
                    return administrator

        msg = "No administrator's email is %s in <ProjectArea %s>" % (email,
                                                                      self)
        self.log.error(msg)
        raise exception.NotFound(msg)


class Role(FieldBase):
    log = logging.getLogger("project_area.Role")

    def __str__(self):
        return self.label


class Member(FieldBase):
    log = logging.getLogger("project_area.Member")

    def __init__(self, url, rtc_obj, raw_data=None):
        FieldBase.__init__(self, url, rtc_obj, raw_data=raw_data)
        # add a new attribute mainly for the un-recorded member use
        self.email = urlunquote(self.url.split("/")[-1])

    def __str__(self):
        if hasattr(self, "title"):
            return self.title
        return self.email

    def _initialize(self):
        pass

    def __initialize(self):
        pass


class Administrator(Member):
    log = logging.getLogger("project_area.Administrator")


class ProjectAdmin(Member):
    log = logging.getLogger("project_area.ProjectAdmin")


class ItemType(FieldBase):
    log = logging.getLogger("project_area.ItemType")

    def __str__(self):
        return self.title


class TeamArea(FieldBase):
    log = logging.getLogger("project_area.TeamArea")

    def __str__(self):
        return self.title


class PlannedFor(FieldBase):
    log = logging.getLogger("project_area.PlannedFor")

    def __str__(self):
        return self.title


class FiledAgainst(FieldBase):
    log = logging.getLogger("project_area.FiledAgainst")

    def __str__(self):
        return self.title


class FoundIn(FieldBase):
    log = logging.getLogger("project_area.FoundIn")

    def __str__(self):
        return self.title


class Severity(FieldBase):
    log = logging.getLogger("project_area.Severity")

    def __str__(self):
        return self.title


class Priority(FieldBase):
    log = logging.getLogger("project_area.Priority")

    def __str__(self):
        return self.title
