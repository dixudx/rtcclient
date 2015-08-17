from rtcclient.base import FieldBase
import logging
import xmltodict
import copy
from rtcclient import exception
from requests.exceptions import HTTPError


class Workitem(FieldBase):
    log = logging.getLogger("workitem.Workitem")

    OSLC_CR_RDF = "application/rdf+xml"

    def __init__(self, url, rtc_obj, workitem_id=None, raw_data=None):
        self.identifier = workitem_id
        FieldBase.__init__(self, url, rtc_obj, raw_data)

    def __str__(self):
        return str(self.identifier)

    def getComments(self):
        """Get all <Comment> objects

        :return: a list contains all the `Comment <Comment>` objects
        :rtype: list
        """

        return self.rtc_obj._get_paged_resources("Comment",
                                                 workitem_id=self.identifier,
                                                 page_size="100")

    def getCommentByID(self, comment_id):
        """Get <Comment> object by its id

        :param comment_id: comment id (integer)
        :return: `Comment <Comment>` object
        :rtype: workitem.Comment
        """

        # check the validity of comment id
        try:
            if isinstance(comment_id, bool):
                raise ValueError()
            if isinstance(comment_id, str):
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

        comments_url = (self.raw_data.get("rtc_cm:comments")
                                     .get("@oslc_cm:collref"))
        headers = copy.deepcopy(self.rtc_obj.headers)
        resp = self.get(comments_url,
                        verify=False,
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
                         data=comment_msg)
        self.log.info("Successfully add comment: [%s] for <Workitem %s>",
                      msg, self)

        raw_data = xmltodict.parse(resp.content)
        return Comment(comment_url,
                       self.rtc_obj,
                       raw_data=raw_data["rdf:RDF"]["rdf:Description"])

    def getSubscribers(self):
        """Get subscribers of this workitem

        :return: a list contains all the `Member <Member>` objects
        :rtype: list
        """

        return self.rtc_obj._get_paged_resources("Subscribers",
                                                 workitem_id=self.identifier,
                                                 page_size="10")

    def getActions(self):
        """Get all the actions of this workitem

        :return: a list contains all the `Action <Action>` objects
        :rtype: list
        """

        cust_attr = (self.raw_data.get("rtc_cm:state")
                                  .get("@rdf:resource")
                                  .split("/")[-2])
        return self.rtc_obj._get_paged_resources("Action",
                                                 projectarea_id=self.contextId,
                                                 customized_attr=cust_attr,
                                                 page_size="100")

    def getAction(self, action_name):
        """Get <Action> object by its name

        TODO: projectarea_id, workitem type
        :return: :class:`Action <Action>` object
        :rtype: workitem.Action
        """

        self.log.debug("Try to get <Action %s>", action_name)
        if not isinstance(action_name, str) or not action_name:
            excp_msg = "Please specify a valid action name"
            self.log.error(excp_msg)
            raise exception.BadValue(excp_msg)

        actions = self.getActions()

        if actions is not None:
            for action in actions:
                if action.title == action_name:
                    self.log.info("Find <Action %s>", action)
                    return action

        self.log.error("No Action named %s", action_name)
        raise exception.NotFound("No Action named %s" % action_name)


class Action(FieldBase):
    log = logging.getLogger("workitem.Action")

    def __str__(self):
        return self.title


class State(FieldBase):
    log = logging.getLogger("workitem.State")

    def __str__(self):
        return self.title


class Comment(FieldBase):
    log = logging.getLogger("workitem.Comment")

    def __init__(self, url, rtc_obj, raw_data=None):
        self.id = url.split("/")[-1]
        FieldBase.__init__(self, url, rtc_obj, raw_data)

    def __str__(self):
        return self.id
