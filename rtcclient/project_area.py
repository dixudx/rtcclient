from rtcclient.base import FieldBase
import xmltodict
from rtcclient import urlunquote
import logging
from rtcclient import exception


class ProjectArea(FieldBase):
    log = logging.getLogger("project_area.ProjectArea")

    def __init__(self, url, rtc_obj, raw_data=None, name=None):
        FieldBase.__init__(self, url, rtc_obj, raw_data)
        self.name = name
        # TODO: for new projectarea obj, self.url may be None
        self.id = self.url.split("/")[-1]

    def __str__(self):
        return self.name

    def get_rtc_obj(self):
        return self.rtc_obj

    def __initialize(self):
        """Request to get response

        """

        self.log.error("For ProjectArea, raw_data is mandatory")
        raise exception.EmptyAttrib("Please input raw_data")

    def getRoles(self):
        """Get all Role objects in this project area

        :return: a list contains all `Role <Role>` objects
        :rtype: list
        pass
        """

        self.log.info("Get all the roles in <ProjectArea %s>",
                      self)
        resp = self.get(self.roles_url,
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
        pass
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

    def getMembers(self):
        """Get all the Member objects in this project area

        :return: a list contains all `Member <Member>` objects
        :rtype: list
        """

        self.log.info("Get all the members in <ProjectArea %s>",
                      self)
        resp = self.get(self.members_url,
                        verify=False,
                        headers=self.rtc_obj.headers)

        raw_data = xmltodict.parse(resp.content)
        members_raw = raw_data['jp06:members']['jp06:member']
        if not members_raw:
            self.log.warning("There are no members in <ProjectArea %s>",
                             self)
            return None

        members_list = list()
        for member_raw in members_raw:
            member = Member(member_raw.get("jp06:url"),
                            self.rtc_obj,
                            raw_data=member_raw)
            members_list.append(member)
        return members_list

    def getMember(self, email):
        """Get the Member object by the email address

        :param email: the email addr (e.g. somebody@gmail.com)
        :return: :class:`Member <Member>` object
        :rtype: project_area.Member
        """

        members = self.getMembers()
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

    def getItemTypes(self):
        """Get all the ItemType objects in this project area

        :return: a list contains all `ItemType <ItemType>` objects
        :rtype: list
        pass
        """

        self.log.info("Get all the workitem types in <ProjectArea %s>",
                      self)

        types_url = "/".join([self.rtc_obj.url,
                              "oslc/types",
                              self.id])
        resp = self.get(types_url,
                        verify=False,
                        headers=self.rtc_obj.headers)

        itemtypes_dict = dict()
        raw_data = xmltodict.parse(resp.content)
        itemtypes_raw = raw_data["oslc_cm:Collection"]["rtc_cm:Type"]
        if not itemtypes_raw:
            self.log.warning("There are no workitem types in <ProjectArea %s>",
                             self)
            return None

        for itemtype_raw in itemtypes_raw:
            itemtype = ItemType(itemtype_raw.get("@rdf:resource"),
                                self.rtc_obj,
                                raw_data=itemtype_raw)
            itemtypes_dict[itemtype.title] = itemtype
        return itemtypes_dict

    def getItemType(self, title):
        """Get the ItemType object by the title

        :param title: the title (e.g. Story/Epic/..)
        :return: :class:`ItemType <ItemType>` object
        :rtype: project_area.ItemType
        """

        itemtypes = self.getItemTypes()
        if itemtypes is not None:
            if title in itemtypes:
                itemtype = itemtypes[title]
                self.log.info("Get <ItemType %s> in <ProjectArea %s>",
                              itemtype, self)
                return itemtype

        excp_msg = "No itemtype's title is %s in <ProjectArea %s>" % (title,
                                                                      self)
        self.log.error(excp_msg)
        raise exception.NotFound(excp_msg)

    def getAdmins(self):
        """Get all the Admin objects in this project area

        :return: a list contains all `Admin <Admin>` objects
        :rtype: list
        """

        self.log.info("Get all the admins in <ProjectArea %s>",
                      self)

        resp = self.get(self.admins_url,
                        verify=False,
                        headers=self.rtc_obj.headers)

        raw_data = xmltodict.parse(resp.content)
        admins_raw = raw_data["jp:admins"]["jp:admin"]

        if not admins_raw:
            self.log.warning("There are no admins in <ProjectArea %s>",
                             self)
            return None

        admins_list = list()
        for admin_raw in admins_raw:
            admin = Admin(admin_raw.get("jp:url"),
                          self.rtc_obj,
                          raw_data=admin_raw)
            admins_list.append(admin)

        return admins_list

    def getAdmin(self, email):
        """Get the <Admin> object by the email address

        :param email: the email addr (e.g. somebody@gmail.com)
        :return: :class:`Admin <Admin>` object
        :rtype: project_area.Admin
        """

        admins = self.getAdmins()
        if admins is not None:
            for admin in admins:
                if admin.email == email:
                    self.log.info("Get <Admin %s> in <ProjectArea %s>",
                                  admin, self)
                    return admin

        excp_msg = "No admin's title is %s in <ProjectArea %s>" % (email,
                                                                   self)
        self.log.error(excp_msg)
        raise exception.NotFound(excp_msg)


class Role(FieldBase):
    log = logging.getLogger("project_area.Role")

    def __str__(self):
        return self.label

    def get_rtc_obj(self):
        return self.rtc_obj

    def __initialize(self):
        """Request to get response

        """
        # TODO
        pass


class Member(FieldBase):
    log = logging.getLogger("project_area.Member")

    def __init__(self, url, rtc_obj, raw_data=None):
        FieldBase.__init__(self, url, rtc_obj, raw_data=raw_data)
        self.email = urlunquote(self.url.split("/")[-1])

    def __str__(self):
        return self.email

    def get_rtc_obj(self):
        return self.rtc_obj

    def __initialize(self):
        """Request to get response

        """
        # TODO
        pass


class Admin(Member):
    log = logging.getLogger("project_area.Admin")


class ProjectAdmin(Member):
    log = logging.getLogger("project_area.ProjectAdmin")


class ItemType(FieldBase):
    log = logging.getLogger("project_area.ItemType")

    def __str__(self):
        return self.title

    def get_rtc_obj(self):
        return self.rtc_obj

    def __initialize(self):
        """Request to get response

        """
        # TODO
        pass
