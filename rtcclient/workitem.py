from rtcclient.base import RTCBase
import logging


class Workitem(RTCBase):
    log = logging.getLogger("workitem:Workitem")

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

    def initialize(self, data):
        self.log.debug("Start initializing data from %s" % self.url)
        self._initialize(data)
        self.log.info("Finish the initialization for <Workitem %s>", self)
