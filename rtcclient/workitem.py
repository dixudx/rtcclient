from rtcclient.base import RTCBase, FieldBase
import logging
import xmltodict
from rtcclient import urlunquote


class Workitem(RTCBase, FieldBase):
    log = logging.getLogger("workitem: Workitem")

    def __init__(self, url, rtc_obj, workitem_id=None):
        self.id = workitem_id
        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, url)
        FieldBase.__init__()

    def __str__(self):
        return self.id

    def get_rtc_obj(self):
        return self.rtc_obj

    def getState(self):
        """Get the workitem state
        """

        pass

    def initialize(self, data):
        self.log.debug("Start initializing data from %s" % self.url)
        self._initialize(data)
        self.setattr("id", self.identifier)
        self.log.info("Finish the initialization for <Workitem %s>",
                      self)

    def create(self, new_workitem):
        # TODO
        pass

    def update(self, new_workitem, state=None):

        # TODO

        if state:
            action = self.getAction(projectarea_id, action_name)
            update_url = "".join([self.url,
                                  "?_action=%s" % action.title])
        else:
            update_url = self.url

        pass

    def addComment(self, msg):
        """Add comment for this workitem

        :param msg: comment message
        :return: True or False
        :rtype: bool
        """

        pass

    def updateField(self, field):
        pass

    def getFields(self):
        pass

    def getActions(self, type, projectarea_id=None,
                   projectarea_name=None):
        """Get all the actions of this workitem

        TODO: type
        :param type: workitem type
        :param projectarea_id: project area id
        :param projectarea_name: project area name
        :return: a list contains all the `Action <Action>` objects
        :rtype: list
        """

        if not projectarea_id:
            projectarea_id = self.rtc_obj.getProjectAreaID(projectarea_name)

        self.log.info("Get all the actions")
        baseurl = self.rtc_obj.url
        actions_url = "/".join([baseurl,
                                "oslc/workflows",
                                projectarea_id,
                                "actions/%s" % type])
        resp = self.get(actions_url,
                        verify=False,
                        headers=self.rtc_obj.headers)
        collects = xmltodict.parse(resp.content).get("oslc_cm:Collection")
        total_cnt = int(collects.get("@oslc_cm:totalCount", 0))
        if total_cnt == 0:
            self.log.warning("No actions are found")
            return None
        actions_raw = collects.get("rtc_cm:Action")
        actions_list = list()
        for action_raw in actions_raw:
            action = Action(action_raw.get("@rdf:about"), self.rtc_obj)
            action.initialize(action_raw)
            actions_list.append(action)
        return actions_list

    def getAction(self, projectarea_id, action_name):
        """Get <Action> object by its name

        TODO: projectarea_id, workitem type
        :param projectarea_id, project area id
        :return: :class:`Action <Action>` object
        :rtype: workitem.Action
        """

        actions = self.getActions(projectarea_id)
        self.log.info("Get an action whose name is %s",
                      action_name)
        if actions:
            for action in actions:
                if action.title == action_name:
                    return action
            self.log.warning("No action's name is %s",
                             action_name)
            return None


class Action(RTCBase, FieldBase):
    log = logging.getLogger("workitem: Action")

    def __init__(self, url, rtc_obj):
        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, url)
        FieldBase.__init__()

    def __str__(self):
        return self.title

    def get_rtc_obj(self):
        return self.rtc_obj


class State(RTCBase, FieldBase):
    log = logging.getLogger("workitem: State")

    def __init__(self, url, rtc_obj):
        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, url)
        FieldBase.__init__()

    def __str__(self):
        return self.title

    def get_rtc_obj(self):
        return self.rtc_obj


class ItemScheme(RTCBase):
    log = logging.getLogger("workitem: ItemScheme")

    def __init__(self, url, rtc_obj):
        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, url)
        FieldBase.__init__()

    def __str__(self):
        return self.title

    def get_rtc_obj(self):
        return self.rtc_obj

    def getScheme(self):
        """TODO

        :return:
        """
        pass
