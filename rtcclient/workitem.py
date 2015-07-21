from rtcclient.base import RTCBase
import logging
import requests
import xmltodict


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

    def getActions(self, projectarea_id, type):
        """
        todo type
        :param projectarea_id: project area id
        :param type: workitem type
        """
        self.log.info("Get all the actions")
        actions_url = "/".join([self.baseurl,
                                "oslc/workflows",
                                projectarea_id,
                                "actions/%s" % type])
        resp = requests.get(actions_url,
                            verify=False,
                            headers=self.headers)
        collects = xmltodict.parse(resp.content).get("oslc_cm:Collection")
        totalCount = int(collects.get("@oslc_cm:totalCount"))
        if totalCount == 0:
            self.log.warning("No actions found")
            return None
        actions_raw = collects.get("rtc_cm:Action")
        actions_list = list()
        for action_raw in actions_raw:
            action = Action()
            action.initialize(action_raw)
            actions_list.append(action)
        return actions_list

    def getAction(self, projectarea_id, action_name):
        """
        @param projectarea_id: project area id
        """
        actions = self.getActions(projectarea_id)
        self.log.info("Get action whose name is %s" % action_name)
        if actions:
            for action in actions:
                if action.title == action_name:
                    return action
            else:
                self.log.warning("No action's name is %s" % action_name)
                return None


class Action(RTCBase):
    log = logging.getLogger("workitem:Action")

    def __init__(self, url, rtc_obj):
        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, url)

    def __str__(self):
        return self.title

    def get_rtc_obj(self):
        return self.rtc_obj

    def initialize(self, data):
        self.log.debug("Start initializing data from %s" % self.url)
        self._initialize(data)
        self.log.info("Finish the initialization for <Action %s>", self)
