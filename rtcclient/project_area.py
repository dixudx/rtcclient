from rtcclient.base import RTCBase, FieldBase
import xmltodict
from rtcclient import urlunquote
import logging


class ProjectArea(RTCBase, FieldBase):
    log = logging.getLogger("project_area: ProjectArea")

    def __init__(self, url, rtc_obj, name=None):
        self.name = name
        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, url)
        FieldBase.__init__()

    def __str__(self):
        return self.name

    def get_rtc_obj(self):
        return self.rtc_obj

    def initialize(self, data):
        self.log.debug("Start initializing data from %s",
                       self.url)
        self._initialize(data)
        self.setattr("id", self.url.split("/")[-1])
        self.log.info("Finish the initialzation for <ProjectArea %s>",
                      self)

    def getRoles(self):
        """Get all Role objects in this project area

        :return: a list contains all `Role <Role>` objects
        :rtype: list
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
            self.log.error("There are no roles in <ProjectArea %s>",
                           self)
            return None
        for role_raw in roles_raw:
            role = Role(role_raw.get("jp06:url"), self.rtc_obj)
            role.initialize(role_raw)
            roles_list.append(role)
        return roles_list

    def getRole(self, label):
        """Get the Role object by the label name

        :param label: the role label name
        :return: :class:`Role <Role>` object
        :rtype: project_area.Role
        """

        roles = self.getRoles()
        for role in roles:
            if role.label == label:
                self.log.info("Get <Role %s> in <ProjectArea %s>",
                              role, self)
                return role
        self.log.error("No role's label is %s in <ProjectArea %s>",
                       label, self)
        return None

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
            self.log.error("There are no members in <ProjectArea %s>",
                           self)
            return None

        members_list = list()
        for member_raw in members_raw:
            member = Member(member_raw.get("jp06:url"), self.rtc_obj)
            member.initialize(member_raw)
            members_list.append(member)
        return members_list

    def getMember(self, email):
        """Get the Member object by the email address

        :param email: the email addr (e.g. somebody@gmail.com)
        :return: :class:`Member <Member>` object
        :rtype: project_area.Member
        """

        members = self.getMembers()
        for member in members:
            if member.email == email:
                self.log.info("Get <Member %s> in <ProjectArea %s>",
                              member, self)
                return member

        self.log.error("No member's email is %s in <ProjectArea %s>",
                       email, self)
        return None

    def getItemTypes(self):
        """Get all the ItemType objects in this project area

        :return: a list contains all `ItemType <ItemType>` objects
        :rtype: list
        """

        self.log.info("Get all the workitem types in <ProjectArea %s>",
                      self)

        types_url = "/".join([self.rtc_obj.url,
                              "oslc/types",
                              self.id])
        resp = self.get(types_url,
                        verify=False,
                        headers=self.rtc_obj.headers)

        itemtypes_list = list()
        raw_data = xmltodict.parse(resp.content)
        itemtypes_raw = raw_data["oslc_cm:Collection"]["rtc_cm:Type"]
        if not itemtypes_raw:
            self.log.warning("There are no workitem types in <ProjectArea %s>",
                             self)
            return None

        for itemtype_raw in itemtypes_raw:
            itemtype = ItemType(itemtype_raw.get("@rdf:resource"),
                                self.rtc_obj)
            itemtype.initialize(itemtype_raw)
            itemtypes_list.append(itemtype)
        return itemtypes_list

    def getItemType(self, title):
        """Get the ItemType object by the title

        :param title: the title (e.g. Story/Epic/..)
        :return: :class:`ItemType <ItemType>` object
        :rtype: project_area.ItemType
        """

        itemtypes = self.getItemTypes()
        for itemtype in itemtypes:
            if itemtype.title == title:
                self.log.info("Get <ItemType %s> in <ProjectArea %s>",
                              itemtype, self)
                return itemtype

        self.log.error("No itemtype's title is %s in <ProjectArea %s>",
                       title, self)
        return None

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
            self.log.error("There are no admins in <ProjectArea %s>",
                           self)
            return None

        admins_list = list()
        for admin_raw in admins_raw:
            admin = Admin(admin_raw.get("jp:url"),
                          self.rtc_obj)
            admin.initialize(admin_raw)
            admins_list.append(admin)

        return admins_list

    def getAdmin(self, email):
        """Get the <Admin> object by the email address

        :param email: the email addr (e.g. somebody@gmail.com)
        :return: :class:`Admin <Admin>` object
        :rtype: project_area.Admin
        """

        admins = self.getAdmins()
        for admin in admins:
            if admin.email == email:
                self.log.info("Get <Admin %s> in <ProjectArea %s>",
                              admin, self)
                return admin

        self.log.error("No admin's title is %s in <ProjectArea %s>",
                       email, self)
        return None


class Role(RTCBase, FieldBase):
    log = logging.getLogger("project_area: Role")

    def __init__(self, url, rtc_obj):
        RTCBase.__init__(self, url)
        FieldBase.__init__()
        self.rtc_obj = rtc_obj

    def __str__(self):
        return self.label

    def get_rtc_obj(self):
        return self.rtc_obj


class Member(RTCBase, FieldBase):
    log = logging.getLogger("project_area: Member")

    def __init__(self, url, rtc_obj):
        RTCBase.__init__(self, url)
        FieldBase.__init__()
        self.rtc_obj = rtc_obj

    def __str__(self):
        return self.email

    def get_rtc_obj(self):
        return self.rtc_obj

    def initialize(self, data):
        self.log.debug("Start initializing data from %s" % self.url)
        self._initialize(data)
        self.setattr("email", urlunquote(self.url.split("/")[-1]))
        self.log.info("Finish the initialization for <%s %s>",
                      self.__class__.__name__,
                      self)


class Admin(Member):
    log = logging.getLogger("project_area: Admin")

    def __init__(self, url, rtc_obj):
        Member.__init__(self, url)


class ProjectAdmin(Member):
    log = logging.getLogger("project_area: ProjectAdmin")

    def __init__(self, url, rtc_obj):
        Member.__init__(self, url)


class ItemType(RTCBase, FieldBase):
    log = logging.getLogger("project_area: ItemType")

    def __init__(self, url, rtc_obj):
        RTCBase.__init__(self, url)
        FieldBase.__init__()
        self.rtc_obj = rtc_obj

    def __str__(self):
        return self.title

    def get_rtc_obj(self):
        return self.rtc_obj

