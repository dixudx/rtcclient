from rtcclient.base import RTCBase, FieldBase
import xmltodict
try:
    from urllib import unquote as urlunquote
except ImportError:
    # Python3
    from urllib.parse import unquote as urlunquote

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
        """Get all roles in this project area

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
            self.log.warning("There are no roles in this <ProjectArea %s>",
                             self)
            return None
        for role_raw in roles_raw:
            role = Role(role_raw.get("jp06:url"), self.rtc_obj)
            role.initialize(role_raw)
            roles_list.append(role)
        return roles_list

    def getRole(self, label):
        """Get the role object by the label name

        :param label: the role label name
        :return: :class:`Role <Role>` object
        :rtype: project_area.Role
        """

        roles = self.getRoles()
        for role in roles:
            if role.label == label:
                self.log.info("Get <Role %s> in this <ProjectArea %s>",
                              role, self)
                return role
        self.log.error("No role's label is %s in this <ProjectArea %s>",
                       label, self)
        return None

    def getMembers(self):
        """Get all the members in this project area

        :return: a list contains all `Member <Member>` objects
        :rtype: list
        """

        self.log.info("Get all the members in <ProjectArea %s>",
                      self)
        resp = self.get(self.members_url,
                        verify=False,
                        headers=self.rtc_obj.headers)

        members_list = list()
        raw_data = xmltodict.parse(resp.content)
        members_raw = raw_data['jp06:members']['jp06:member']
        if not members_raw:
            self.log.warning("There are no members in this ProjectArea:<%s>",
                             self.name)
            return None
        for member_raw in members_raw:
            member = Member(member_raw.get("jp06:url"), self.rtc_obj)
            member.initialize(member_raw)
            members_list.append(member)
        return members_list

    def getMember(self, email):
        """Get the member object by the email address

        :param email: the email addr (e.g. somebody@gmail.com)
        :return: :class:`Member <Member>` object
        :rtype: project_area.Member
        """

        members = self.getMembers()
        for member in members:
            if member.email == email:
                self.log.info("Get <Member %s> in this <ProjectArea %s>",
                              member, self)
                return member
        self.log.error("No member's email is %s in this <ProjectArea %s>",
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
        self.log.info("Finish the initialization for <Member %s>", self)
