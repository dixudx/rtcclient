from rtcclient.base import RTCBase


class Workitem(RTCBase):
    def __init__(self, baseurl, rtc_obj, workitem_id=None):
        self.id = workitem_id
        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, baseurl)

    def __str__(self):
        return self.id

    def get_rtc_obj(self):
        return self.rtc_obj
