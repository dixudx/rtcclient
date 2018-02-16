from rtcclient.base import FieldBase
import logging
import xmltodict
import copy
from rtcclient import exception, OrderedDict
from requests.exceptions import HTTPError
from rtcclient.models import Comment, Attachment
import six
import json
import os


class Workitem(FieldBase):
    """A wrapped class for managing all related resources of the workitem

    :param url: the workitem url
    :param rtc_obj: a reference to the
        :class:`rtcclient.client.RTCClient` object
    :param workitem_id: (default is `None`) the id of the workitem, which
        will be retrieved if not specified
    :param raw_data: the raw data ( OrderedDict ) of the request response
    """

    log = logging.getLogger("workitem.Workitem")

    OSLC_CR_RDF = "application/rdf+xml"

    def __init__(self, url, rtc_obj, workitem_id=None, raw_data=None):
        self.identifier = workitem_id
        FieldBase.__init__(self, url, rtc_obj, raw_data)
        if self.identifier is None:
            self.identifier = self.url.split("/")[-1]

    def __str__(self):
        return str(self.identifier)

    def getComments(self):
        """Get all :class:`rtcclient.models.Comment` objects in this workitem

        :return: a :class:`list` contains all the
            :class:`rtcclient.models.Comment` objects
        :rtype: list
        """

        return self.rtc_obj._get_paged_resources("Comment",
                                                 workitem_id=self.identifier,
                                                 page_size="100")

    def getCommentByID(self, comment_id):
        """Get the :class:`rtcclient.models.Comment` object by its id

        Note: the comment id starts from 0

        :param comment_id: the comment id (integer or equivalent string)
        :return: the :class:`rtcclient.models.Comment` object
        :rtype: rtcclient.models.Comment
        """

        # check the validity of comment id
        try:
            if isinstance(comment_id, bool):
                raise ValueError()
            if isinstance(comment_id, six.string_types):
                comment_id = int(comment_id)
            if not isinstance(comment_id, int):
                raise ValueError()
        except (ValueError, TypeError):
            raise exception.BadValue("Please input valid comment id")

        comment_url = "/".join([self.url,
                                "rtc_cm:comments/%s" % comment_id])
        try:
            return Comment(comment_url,
                           self.rtc_obj)
        except HTTPError:
            self.log.error("Comment %s does not exist", comment_id)
            raise exception.BadValue("Comment %s does not exist" % comment_id)

    def addComment(self, msg=None):
        """Add a comment to this workitem

        :param msg: comment message
        :return: the :class:`rtcclient.models.Comment` object
        :rtype: rtcclient.models.Comment
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

        comments_url = "/".join([self.url,
                                 "rtc_cm:comments"])
        headers = copy.deepcopy(self.rtc_obj.headers)
        resp = self.get(comments_url,
                        verify=False,
                        proxies=self.rtc_obj.proxies,
                        headers=headers)

        raw_data = xmltodict.parse(resp.content)

        total_cnt = raw_data["oslc_cm:Collection"]["@oslc_cm:totalCount"]
        comment_url = "/".join([comments_url,
                                total_cnt])

        comment_msg = origin_comment.format(comment_url, msg)

        headers["Content-Type"] = self.OSLC_CR_RDF
        headers["Accept"] = self.OSLC_CR_RDF
        headers["OSLC-Core-Version"] = "2.0"
        headers["If-Match"] = resp.headers.get("etag")
        req_url = "/".join([comments_url,
                            "oslc:comment"])

        resp = self.post(req_url,
                         verify=False,
                         headers=headers,
                         proxies=self.rtc_obj.proxies,
                         data=comment_msg)
        self.log.info("Successfully add comment: [%s] for <Workitem %s>",
                      msg, self)

        raw_data = xmltodict.parse(resp.content)
        return Comment(comment_url,
                       self.rtc_obj,
                       raw_data=raw_data["rdf:RDF"]["rdf:Description"])

    def addSubscriber(self, email):
        """Add a subscriber to this workitem

        If the subscriber has already been added, no more actions will be
        performed.

        :param email: the subscriber's email
        """

        headers, raw_data = self._perform_subscribe()
        existed_flag, raw_data = self._add_subscriber(email, raw_data)
        if existed_flag:
            return

        self._update_subscribe(headers, raw_data)
        self.log.info("Successfully add a subscriber: %s for <Workitem %s>",
                      email, self)

    def addSubscribers(self, emails_list):
        """Add subscribers to this workitem

        If the subscribers have already been added, no more actions will be
        performed.

        :param emails_list: a :class:`list`/:class:`tuple`/:class:`set`
            contains the the subscribers' emails
        """

        if not hasattr(emails_list, "__iter__"):
            error_msg = "Input parameter 'emails_list' is not iterable"
            self.log.error(error_msg)
            raise exception.BadValue(error_msg)

        # overall flag
        existed_flags = False

        headers, raw_data = self._perform_subscribe()
        for email in emails_list:
            existed_flag, raw_data = self._add_subscriber(email, raw_data)
            existed_flags = existed_flags and existed_flag

        if existed_flags:
            return

        self._update_subscribe(headers, raw_data)
        self.log.info("Successfully add subscribers: %s for <Workitem %s>",
                      emails_list, self)

    def removeSubscriber(self, email):
        """Remove a subscriber from this workitem

        If the subscriber has not been added, no more actions will be
        performed.

        :param email: the subscriber's email
        """

        headers, raw_data = self._perform_subscribe()
        missing_flag, raw_data = self._remove_subscriber(email, raw_data)
        if missing_flag:
            return

        self._update_subscribe(headers, raw_data)
        self.log.info("Successfully remove a subscriber: %s for <Workitem %s>",
                      email, self)

    def removeSubscribers(self, emails_list):
        """Remove subscribers from this workitem

        If the subscribers have not been added, no more actions will be
        performed.

        :param emails_list: a :class:`list`/:class:`tuple`/:class:`set`
            contains the the subscribers' emails
        """

        if not hasattr(emails_list, "__iter__"):
            error_msg = "Input parameter 'emails_list' is not iterable"
            self.log.error(error_msg)
            raise exception.BadValue(error_msg)

        # overall flag
        missing_flags = True

        headers, raw_data = self._perform_subscribe()
        for email in emails_list:
            missing_flag, raw_data = self._remove_subscriber(email, raw_data)
            missing_flags = missing_flags and missing_flag

        if missing_flags:
            return

        self._update_subscribe(headers, raw_data)
        self.log.info("Successfully remove subscribers: %s for <Workitem %s>",
                      emails_list, self)

    def _update_subscribe(self, headers, raw_data):
        subscribers_url = "".join([self.url,
                                   "?oslc_cm.properties=rtc_cm:subscribers"])
        self.put(subscribers_url,
                 verify=False,
                 proxies=self.rtc_obj.proxies,
                 headers=headers,
                 data=xmltodict.unparse(raw_data))

    def _perform_subscribe(self):
        subscribers_url = "".join([self.url,
                                   "?oslc_cm.properties=rtc_cm:subscribers"])
        headers = copy.deepcopy(self.rtc_obj.headers)
        headers["Content-Type"] = self.OSLC_CR_RDF
        headers["Accept"] = self.OSLC_CR_RDF
        headers["OSLC-Core-Version"] = "2.0"
        resp = self.get(subscribers_url,
                        verify=False,
                        proxies=self.rtc_obj.proxies,
                        headers=headers)
        headers["If-Match"] = resp.headers.get("etag")
        raw_data = xmltodict.parse(resp.content)
        return headers, raw_data

    def _add_subscriber(self, email, raw_data):
        if not isinstance(email, six.string_types) or "@" not in email:
            excp_msg = "Please specify a valid email address name: %s" % email
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        existed_flag = False
        new_subscriber = self.rtc_obj.getOwnedBy(email)
        new_sub = OrderedDict()
        new_sub["@rdf:resource"] = new_subscriber.url
        description = raw_data.get("rdf:RDF").get("rdf:Description")
        subs = description.get("rtc_cm:subscribers", None)
        if subs is None:
            # no subscribers
            added_url = "http://jazz.net/xmlns/prod/jazz/rtc/cm/1.0/"
            raw_data["rdf:RDF"]["@xmlns:rtc_cm"] = added_url
            description["rtc_cm:subscribers"] = new_sub
        else:
            if isinstance(subs, OrderedDict):
                # only one subscriber exist
                existed_flag = self._check_exist_subscriber(new_subscriber,
                                                            subs)
                if not existed_flag:
                    subs = [subs]
                    subs.append(new_sub)
                    description["rtc_cm:subscribers"] = subs
            else:
                # a list: several subscribers
                # check existing
                for exist_sub in subs:
                    existed_flag = self._check_exist_subscriber(new_subscriber,
                                                                exist_sub)
                    if existed_flag:
                        break
                else:
                    subs.append(new_sub)

        return existed_flag, raw_data

    def _remove_subscriber(self, email, raw_data):
        if not isinstance(email, six.string_types) or "@" not in email:
            excp_msg = "Please specify a valid email address name: %s" % email
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        missing_flag = True
        del_sub = self.rtc_obj.getOwnedBy(email)
        description = raw_data.get("rdf:RDF").get("rdf:Description")
        subs = description.get("rtc_cm:subscribers", None)
        if subs is None:
            # no subscribers
            self.log.error("No subscribers for <Workitem %s>",
                           self)
        else:
            if isinstance(subs, OrderedDict):
                # only one subscriber exist
                missing_flag = self._check_missing_subscriber(del_sub,
                                                              subs)
                if not missing_flag:
                    description.pop("rtc_cm:subscribers")
                else:
                    self.log.error("The subscriber %s has not been "
                                   "added. No need to unsubscribe",
                                   del_sub.email)
            else:
                # a list: several subscribers
                # check existing
                for exist_sub in subs:
                    missing_flag = self._check_missing_subscriber(del_sub,
                                                                  exist_sub)
                    if not missing_flag:
                        subs.remove(exist_sub)

                        if len(subs) == 1:
                            # only one existing
                            description["rtc_cm:subscribers"] = subs[0]

                        break
                else:
                    self.log.error("The subscriber %s has not been "
                                   "added. No need to unsubscribe",
                                   del_sub.email)

        return missing_flag, raw_data

    def _check_exist_subscriber(self, new_subscriber, exist_sub):
        if new_subscriber.url == exist_sub["@rdf:resource"]:
            self.log.error("The subscriber %s has already been "
                           "added. No need to re-add",
                           new_subscriber.email)
            return True
        return False

    def _check_missing_subscriber(self, del_subscriber, exist_sub):
        if del_subscriber.url == exist_sub["@rdf:resource"]:
            return False
        return True

    def getSubscribers(self):
        """Get subscribers of this workitem

        :return: a :class:`list` contains all the
            :class:`rtcclient.models.Member` objects
        :rtype: list
        """

        return self.rtc_obj._get_paged_resources("Subscribers",
                                                 workitem_id=self.identifier,
                                                 page_size="10")

    def getActions(self):
        """Get all :class:`rtcclient.models.Action` objects of this workitem

        :return: a :class:`list` contains all the
            :class:`rtcclient.models.Action` objects
        :rtype: list
        """

        return self._getActions()

    def getAction(self, action_name):
        """Get the :class:`rtcclient.models.Action` object by its name

        :param action_name: the name/title of the action
        :return: the :class:`rtcclient.models.Action` object
        :rtype: rtcclient.models.Action
        """

        self.log.debug("Try to get <Action %s>", action_name)
        if not isinstance(action_name, six.string_types) or not action_name:
            excp_msg = "Please specify a valid action name"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        actions = self._getActions(action_name=action_name)

        if actions is not None:
            action = actions[0]
            self.log.info("Find <Action %s>", action)
            return action

        self.log.error("No Action named %s", action_name)
        raise exception.NotFound("No Action named %s" % action_name)

    def _getActions(self, action_name=None):
        filter_rule = None
        if action_name is not None:
            faction_rule = ("dc:title", None, action_name)
            filter_rule = self.rtc_obj._add_filter_rule(filter_rule,
                                                        faction_rule)

        cust_attr = (self.raw_data.get("rtc_cm:state")
                                  .get("@rdf:resource")
                                  .split("/")[-2])
        return self.rtc_obj._get_paged_resources("Action",
                                                 projectarea_id=self.contextId,
                                                 customized_attr=cust_attr,
                                                 page_size="100",
                                                 filter_rule=filter_rule)

    def getStates(self):
        """Get all :class:`rtcclient.models.State` objects of this workitem

        :return: a :class:`list` contains all the
            :class:`rtcclient.models.State` objects
        :rtype: list
        """

        cust_attr = (self.raw_data.get("rtc_cm:state")
                         .get("@rdf:resource")
                         .split("/")[-2])
        return self.rtc_obj._get_paged_resources("State",
                                                 projectarea_id=self.contextId,
                                                 customized_attr=cust_attr,
                                                 page_size="50")

    def getIncludedInBuilds(self):
        """Get all :class:`rtcclient.models.IncludedInBuild` objects that
        have already included this workitem

        WARNING: If one of the IncludedInBuilds is removed or cannot be
        retrieved/found correctly, then 404 error will be raised.

        :return: a :class:`list` contains all the
            :class:`rtcclient.models.IncludedInBuild` objects
        :rtype: list
        """

        build_tag = ("rtc_cm:com.ibm.team.build.linktype.includedWorkItems."
                     "com.ibm.team.build.common.link.includedInBuilds")
        return self.rtc_obj._get_paged_resources("IncludedInBuild",
                                                 workitem_id=self.identifier,
                                                 customized_attr=build_tag,
                                                 page_size="5")

    def getParent(self, returned_properties=None):
        """Get the parent workitem of this workitem

        If no parent, None will be returned.

        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :return: a :class:`rtcclient.workitem.Workitem` object
        :rtype: rtcclient.workitem.Workitem
        """

        parent_tag = ("rtc_cm:com.ibm.team.workitem.linktype."
                      "parentworkitem.parent")
        rp = returned_properties
        parent = (self.rtc_obj
                      ._get_paged_resources("Parent",
                                            workitem_id=self.identifier,
                                            customized_attr=parent_tag,
                                            page_size="5",
                                            returned_properties=rp))

        # No more than one parent
        if parent:
            # only one element
            return parent[0]
        return None

    def getChildren(self, returned_properties=None):
        """Get all the children workitems of this workitem

        If no children, None will be returned.

        :param returned_properties: the returned properties that you want.
            Refer to :class:`rtcclient.client.RTCClient` for more explanations
        :return: a :class:`rtcclient.workitem.Workitem` object
        :rtype: rtcclient.workitem.Workitem
        """

        children_tag = ("rtc_cm:com.ibm.team.workitem.linktype."
                        "parentworkitem.children")
        rp = returned_properties
        return (self.rtc_obj
                    ._get_paged_resources("Children",
                                          workitem_id=self.identifier,
                                          customized_attr=children_tag,
                                          page_size="10",
                                          returned_properties=rp))

    def getChangeSets(self):
        """Get all the ChangeSets of this workitem

        :return: a :class:`list` contains all the
            :class:`rtcclient.models.ChangeSet` objects
        :rtype: list
        """

        changeset_tag = ("rtc_cm:com.ibm.team.filesystem.workitems."
                         "change_set.com.ibm.team.scm.ChangeSet")
        return (self.rtc_obj
                    ._get_paged_resources("ChangeSet",
                                          workitem_id=self.identifier,
                                          customized_attr=changeset_tag,
                                          page_size="10"))

    def addParent(self, parent_id):
        """Add a parent to current workitem

        Notice: for a certain workitem, no more than one parent workitem
        can be added and specified

        :param parent_id: the parent workitem id/number
            (integer or equivalent string)
        """

        if isinstance(parent_id, bool):
            raise exception.BadValue("Please input a valid workitem id")
        if isinstance(parent_id, six.string_types):
            parent_id = int(parent_id)
        if not isinstance(parent_id, int):
            raise exception.BadValue("Please input a valid workitem id")

        self.log.debug("Try to add a parent <Workitem %s> to current "
                       "<Workitem %s>",
                       parent_id,
                       self)

        headers = copy.deepcopy(self.rtc_obj.headers)
        headers["Content-Type"] = self.OSLC_CR_JSON
        req_url = "".join([self.url,
                           "?oslc_cm.properties=com.ibm.team.workitem.",
                           "linktype.parentworkitem.parent"])

        parent_tag = ("rtc_cm:com.ibm.team.workitem.linktype."
                      "parentworkitem.parent")
        parent_url = ("{0}/resource/itemName/com.ibm.team."
                      "workitem.WorkItem/{1}".format(self.rtc_obj.url,
                                                     parent_id))
        parent_original = {parent_tag: [{"rdf:resource": parent_url}]}

        self.put(req_url,
                 verify=False,
                 proxies=self.rtc_obj.proxies,
                 headers=headers,
                 data=json.dumps(parent_original))
        self.log.info("Successfully add a parent <Workitem %s> to current "
                      "<Workitem %s>",
                      parent_id,
                      self)

    def addChild(self, child_id):
        """Add a child to current workitem

        :param child_id: the child workitem id/number
            (integer or equivalent string)
        """

        self.log.debug("Try to add a child <Workitem %s> to current "
                       "<Workitem %s>",
                       child_id,
                       self)
        self._addChildren([child_id])
        self.log.info("Successfully add a child <Workitem %s> to current "
                      "<Workitem %s>",
                      child_id,
                      self)

    def addChildren(self, child_ids):
        """Add children to current workitem

        :param child_ids: a :class:`list` contains the children
            workitem id/number (integer or equivalent string)
        """

        if not hasattr(child_ids, "__iter__"):
            error_msg = "Input parameter 'child_ids' is not iterable"
            self.log.error(error_msg)
            raise exception.BadValue(error_msg)

        self.log.debug("Try to add children <Workitem %s> to current "
                       "<Workitem %s>",
                       child_ids,
                       self)
        self._addChildren(child_ids)
        self.log.info("Successfully add children <Workitem %s> to current "
                      "<Workitem %s>",
                      child_ids,
                      self)

    def _addChildren(self, child_ids):
        child_tag = ("rtc_cm:com.ibm.team.workitem.linktype."
                     "parentworkitem.children")

        children_original = dict()
        children_original[child_tag] = list()

        # retrieve current children
        cur_children = self.getChildren(returned_properties="dc:identifier")
        cur_child_ids = [cur_child.identifier for cur_child
                         in (cur_children or []) if cur_child is not None]

        # add current children to list
        for child_id in cur_child_ids:
            self._addChild(child_id, children_original)

        # add new children to list
        for child_id in child_ids:
            self._addChild(child_id, children_original)

        # update children workitems
        headers = copy.deepcopy(self.rtc_obj.headers)
        headers["Content-Type"] = self.OSLC_CR_JSON
        req_url = "".join([self.url,
                           "?oslc_cm.properties=com.ibm.team.workitem.",
                           "linktype.parentworkitem.children"])
        self.put(req_url,
                 verify=False,
                 headers=headers,
                 proxies=self.rtc_obj.proxies,
                 data=json.dumps(children_original))

    def _addChild(self, child_id, children_original):
        child_tag = ("rtc_cm:com.ibm.team.workitem.linktype."
                     "parentworkitem.children")

        # check data type
        if isinstance(child_id, bool):
            raise exception.BadValue("Invalid workitem id: %s",
                                     child_id)
        if isinstance(child_id, six.string_types):
            child_id = int(child_id)
        if not isinstance(child_id, int):
            raise exception.BadValue("Invalid workitem id: %s",
                                     child_id)

        # add child url
        child_url = ("{0}/resource/itemName/com.ibm.team."
                     "workitem.WorkItem/{1}".format(self.rtc_obj.url,
                                                    child_id))
        new_child = {"rdf:resource": child_url}
        if new_child not in children_original[child_tag]:
            children_original[child_tag].append(new_child)
        else:
            self.log.debug("Child <Workitem %s> has already been added to "
                           "current <Workitem %s>. Ignore it.",
                           child_id,
                           self)

    def removeParent(self):
        """Remove the parent workitem from current workitem

        Notice: for a certain workitem, no more than one parent workitem
        can be added and specified

        """

        self.log.debug("Try to remove the parent workitem from current "
                       "<Workitem %s>",
                       self)

        headers = copy.deepcopy(self.rtc_obj.headers)
        headers["Content-Type"] = self.OSLC_CR_JSON
        req_url = "".join([self.url,
                           "?oslc_cm.properties=com.ibm.team.workitem.",
                           "linktype.parentworkitem.parent"])

        parent_tag = ("rtc_cm:com.ibm.team.workitem.linktype."
                      "parentworkitem.parent")
        parent_original = {parent_tag: []}

        self.put(req_url,
                 verify=False,
                 proxies=self.rtc_obj.proxies,
                 headers=headers,
                 data=json.dumps(parent_original))
        self.log.info("Successfully remove the parent workitem of current "
                      "<Workitem %s>",
                      self)

    def removeChild(self, child_id):
        """Remove a child from current workitem

        :param child_id: the child workitem id/number
            (integer or equivalent string)
        """

        self.log.debug("Try to remove a child <Workitem %s> from current "
                       "<Workitem %s>",
                       child_id,
                       self)
        self._removeChildren([child_id])
        self.log.info("Successfully remove a child <Workitem %s> from "
                      "current <Workitem %s>",
                      child_id,
                      self)

    def removeChildren(self, child_ids):
        """Remove children from current workitem

        :param child_ids: a :class:`list` contains the children
            workitem id/number (integer or equivalent string)
        """

        if not hasattr(child_ids, "__iter__"):
            error_msg = "Input parameter 'child_ids' is not iterable"
            self.log.error(error_msg)
            raise exception.BadValue(error_msg)

        self.log.debug("Try to remove children <Workitem %s> from current "
                       "<Workitem %s>",
                       child_ids,
                       self)
        self._removeChildren(child_ids)
        self.log.info("Successfully remove children <Workitem %s> from "
                      "current <Workitem %s>",
                      child_ids,
                      self)

    def _removeChildren(self, child_ids):
        child_tag = ("rtc_cm:com.ibm.team.workitem.linktype."
                     "parentworkitem.children")

        children_original = dict()
        children_original[child_tag] = list()

        # retrieve current children
        cur_children = self.getChildren(returned_properties="dc:identifier")
        cur_child_ids = [cur_child.identifier for cur_child in cur_children]

        # add current children to list
        # remove to-be-deleted children
        for child_id in cur_child_ids:
            if (int(child_id) not in child_ids and
                    str(child_id) not in child_ids):
                self._addChild(child_id, children_original)

        # update children workitems
        headers = copy.deepcopy(self.rtc_obj.headers)
        headers["Content-Type"] = self.OSLC_CR_JSON
        req_url = "".join([self.url,
                           "?oslc_cm.properties=com.ibm.team.workitem.",
                           "linktype.parentworkitem.children"])
        self.put(req_url,
                 verify=False,
                 headers=headers,
                 proxies=self.rtc_obj.proxies,
                 data=json.dumps(children_original))

    def addAttachment(self, filepath):
        """Upload attachment to a workitem

        :param filepath: the attachment file path
        :return: the :class:`rtcclient.models.Attachment` object
        :rtype: rtcclient.models.Attachment
        """

        proj_id = self.contextId

        fa = self.rtc_obj.getFiledAgainst(self.filedAgainst,
                                          projectarea_id=proj_id)
        fa_id = fa.url.split("/")[-1]

        headers = copy.deepcopy(self.rtc_obj.headers)
        if headers.__contains__("Content-Type"):
            headers.__delitem__("Content-Type")

        filename = os.path.basename(filepath)
        fileh = open(filepath, "rb")
        files = {"attach": (filename, fileh, "application/octet-stream")}

        params = {"projectId": proj_id,
                  "multiple": "true",
                  "category": fa_id}
        req_url = "".join([self.rtc_obj.url,
                           "/service/com.ibm.team.workitem.service.",
                           "internal.rest.IAttachmentRestService/"])
        resp = self.post(req_url,
                         verify=False,
                         headers=headers,
                         proxies=self.rtc_obj.proxies,
                         params=params,
                         files=files)
        raw_data = xmltodict.parse(resp.content)
        json_body = json.loads(raw_data["html"]["body"]["textarea"])
        attachment_info = json_body["files"][0]
        return self._add_attachment_link(attachment_info)

    def _add_attachment_link(self, attachment_info):
        payload = {"rdf:resource": attachment_info["url"],
                   "dcterms:title": ": ".join([str(attachment_info["id"]),
                                               attachment_info["name"]])}
        attachment_tag = ("/rtc_cm:com.ibm.team.workitem.linktype."
                          "attachment.attachment")
        attachment_collection_url = self.url + attachment_tag

        resp = self.post(attachment_collection_url,
                         payload,
                         verify=False,
                         headers=self.rtc_obj.headers,
                         proxies=self.rtc_obj.proxies)
        raw_data = xmltodict.parse(resp.content)

        return Attachment(attachment_info["url"],
                          self.rtc_obj,
                          raw_data=raw_data["rtc_cm:Attachment"])

    def getAttachments(self):
        """Get all :class:`rtcclient.models.Attachment` objects of
        this workitem

        :return: a :class:`list` contains all the
            :class:`rtcclient.models.Attachment` objects
        :rtype: list
        """

        attachment_tag = ("rtc_cm:com.ibm.team.workitem.linktype."
                          "attachment.attachment")
        return (self.rtc_obj
                    ._get_paged_resources("Attachment",
                                          workitem_id=self.identifier,
                                          customized_attr=attachment_tag,
                                          page_size="10"))
