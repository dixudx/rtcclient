from rtcclient.base import RTCBase


class Workitem(RTCBase):
    def __init__(self, url, rtc_obj, workitem_id=None):
        self.id = workitem_id
        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, url)

    def __str__(self):
        return self.id

    def get_rtc_obj(self):
        return self.rtc_obj

    def getState(self):
        """
        Get the workitem state
        """
        pass

    def updateWorkitem(self):
        pass

    def updateField(self, field):
        pass

    def getFields(self):
        pass
