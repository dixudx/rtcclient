from rtcclient.base import RTCBase
import xmltodict
import requests
try:
    from urllib import unquote as urlunquote
except ImportError:
    # Python3
    from urllib.parse import unquote as urlunquote

import logging


class ProjectArea(RTCBase):
    log = logging.getLogger("project_area: ProjectArea")

    def __init__(self, url, rtc_obj, name=None):
        self.name = name
        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, url)

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
        resp = requests.get(self.roles_url,
                            verify=False,
                            headers=self.rtc_obj.headers)

        roles_list = list()
        raw_data = xmltodict.parse(resp.content)
        roles_raw = raw_data['jp06:roles']['jp06:role']
        if not roles_raw:
            self.log.warning("No roles found in this ProjectArea:<%s>",
                             self.name)
            return None
        for role_raw in roles_raw:
            role = Role(role_raw.get("jp06:url"), self.rtc_obj)
            role.initialize(role_raw)
            roles_list.append(role)
        return roles_list

    def getMembers(self):
        resp = requests.get(self.members_url,
                            verify=False,
                            headers=self.rtc_obj.headers)

        members_list = list()
        raw_data = xmltodict.parse(resp.content)
        members_raw = raw_data['jp06:members']['jp06:member']
        if not members_raw:
            self.log.warning("No member found in this ProjectArea:<%s>",
                             self.name)
            return None
        for member_raw in members_raw:
            member = Member(member_raw.get("jp06:url"), self.rtc_obj)
            member.initialize(member_raw)
            members_list.append(member)
        return members_list


class Role(RTCBase):
    log = logging.getLogger("project_area: Role")

    def __init__(self, url, rtc_obj):
        RTCBase.__init__(self, url)
        self.rtc_obj = rtc_obj

    def __str__(self):
        return self.label

    def get_rtc_obj(self):
        return self.rtc_obj

    def initialize(self, data):
        self.log.debug("Start initializing data from %s" % self.url)
        self._initialize(data)
        self.log.info("Finish the initialization for <Role %s>", self)


class Member(RTCBase):
    log = logging.getLogger("project_area: Member")

    def __init__(self, url, rtc_obj):
        RTCBase.__init__(self, url)
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
