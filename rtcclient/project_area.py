from rtcclient.base import RTCBase


class ProjectArea(RTCBase):
    def __init__(self, baseurl, rtc_obj, name=None):
        self.name = name
        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, baseurl)

    def __str__(self):
        return self.name

    def get_rtc_obj(self):
        return self.rtc_obj
