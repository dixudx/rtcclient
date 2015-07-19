from rtcclient.base import RTCBase
import logging


class ProjectArea(RTCBase):
    log = logging.getLogger("project_area: ProjectArea")

    def __init__(self, baseurl, rtc_obj, name=None):
        self.name = name
        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, baseurl)

    def __str__(self):
        return self.name

    def get_rtc_obj(self):
        return self.rtc_obj

    def initialize(self, data):
        self.log.debug("Start initializing data from %s" % self.baseurl)
        for (key, value) in data.iteritems():
            attr = key.split(":")[-1].replace("-", "_")
            self.setattr(attr, value)
        self.setattr("id", self.url.split("/")[-1])
        self.log.info("Finish")

    def getRoles(self):
        pass

    def getMembers(self):
        pass


class Role(RTCBase):
    pass


class Member(RTCBase):
    pass
