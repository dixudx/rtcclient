from rtcclient.base import RTCBase, FieldBase
import logging
import xmltodict
from rtcclient import urlunquote
import copy


class Workitem(RTCBase, FieldBase):
    log = logging.getLogger("workitem: Workitem")

    def __init__(self, url, rtc_obj, workitem_id=None, raw_data=None):
        self.identifier = workitem_id
        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, url)
        FieldBase.__init__(self, data=raw_data)

    def __str__(self):
        return self.identifier

    def get_rtc_obj(self):
        return self.rtc_obj

    def getState(self):
        """Get the workitem state
        """

        pass

    def create(self, new_workitem):
        # TODO
        pass

    def update(self, new_workitem, state=None):

        # TODO

#         if state:
#             action = self.getAction(self.contextId, action_name)
#             update_url = "".join([self.url,
#                                   "?_action=%s" % action.title])
#         else:
#             update_url = self.url

        pass

    def getComments(self):
        pass

    def addComment(self, msg=None):
        """Add comment for this workitem

        :param msg: comment message
        :return: :class:`Comment <Comment>` object
        :rtype: workitem.Comment
        """

        origin_comment = '''
<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:rtc_ext="http://jazz.net/xmlns/prod/jazz/rtc/ext/1.0/"
    xmlns:rtc_cm="http://jazz.net/xmlns/prod/jazz/rtc/cm/1.0/"
    xmlns:oslc_cm="http://open-services.net/ns/cm#"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:oslc_cmx="http://open-services.net/ns/cm-x#"
    xmlns:oslc="http://open-services.net/ns/core#">
  <rdf:Description rdf:about="{0}">
    <rdf:type rdf:resource="http://open-services.net/ns/core#Comment"/>
    <dcterms:description rdf:parseType="Literal">{1}</dcterms:description>
  </rdf:Description>
</rdf:RDF>
'''

        headers = copy.deepcopy(self.rtc_obj.headers)
        resp = self.get(self.comments,
                        verify=False,
                        headers=headers)

        raw_data = xmltodict.parse(resp.content)

        total_cnt = raw_data["oslc_cm:Collection"]["@oslc_cm:totalCount"]
        comment_url = "/".join([self.comments,
                                total_cnt])

        comment_msg = origin_comment.format(comment_url, msg)

        headers['Content-type'] = 'application/rdf+xml'
        headers['Accept'] = 'application/rdf+xml'
        headers["OSLC-Core-Version"] = "2.0"
        headers['If-Match'] = resp.headers.get('etag')
        req_url = "/".join([self.comments,
                            "oslc:comment"])

        resp = self.post(req_url,
                         verify=False,
                         headers=headers,
                         data=comment_msg)
        self.log.info("Successfully add comment: %s for <Workitem %s>",
                      msg, self)

        # TODO: resp.content
        return Comment(comment_url,
                       self.rtc_obj,
                       raw_data=resp.content)

    def getComment(self, url):
        headers = copy.deepcopy(self.rtc_obj.headers)
#         headers['Content-type'] = 'application/rdf+xml'
#         headers['Accept'] = 'application/rdf+xml'
        resp = self.get(url, verify=False,
                        headers=headers)
        print resp.content
        print str(resp.content)
        return resp.content
#         raw_data = xmltodict.parse(resp.content).get("oslc_cm:Collection")
#         return Comment()
#         url, rtc_obj, raw_data=None

    def addSubscribers(self, subscribers):
        """Add subscribers for this workitem

        :param subscribers: subscribers list
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

        if actions is not None:
            for action in actions:
                if action.title == action_name:
                    self.log.info("Get an action whose name is %s",
                                  action_name)
                    return action
            self.log.error("No action's name is %s",
                           action_name)
            return None


class Action(RTCBase, FieldBase):
    log = logging.getLogger("workitem: Action")

    def __init__(self, url, rtc_obj, raw_data=None):
        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, url)
        FieldBase.__init__(self, data=raw_data)

    def __str__(self):
        return self.title

    def get_rtc_obj(self):
        return self.rtc_obj


class State(RTCBase, FieldBase):
    log = logging.getLogger("workitem: State")

    def __init__(self, url, rtc_obj, raw_data=None):
        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, url)
        FieldBase.__init__(self, data=raw_data)

    def __str__(self):
        return self.title

    def get_rtc_obj(self):
        return self.rtc_obj


class ItemScheme(RTCBase):
    log = logging.getLogger("workitem: ItemScheme")

    def __init__(self, url, rtc_obj, raw_data=None):
        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, url)
        FieldBase.__init__(self, data=raw_data)

    def __str__(self):
        return self.title

    def get_rtc_obj(self):
        return self.rtc_obj

    def getScheme(self):
        """TODO

        :return:
        """
        pass


class Comment(RTCBase, FieldBase):
    log = logging.getLogger("workitem: Comment")

    def __init__(self, url, rtc_obj, raw_data=None):
        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, url)
        FieldBase.__init__(self, data=raw_data)

    def __str__(self):
        # TODO
        return "comment"

    def get_rtc_obj(self):
        return self.rtc_obj
