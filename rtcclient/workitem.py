from rtcclient.base import FieldBase
import logging
import xmltodict
import copy
from rtcclient import exception
from requests.exceptions import HTTPError
from rtcclient.models import Comment


class Workitem(FieldBase):
    """A wrapped class for managing all related resources of the workitem

    :param url: the workitem url
    :param rtc_obj: a reference to the
        :class:`rtcclient.client.RTCClient` object
    :param workitem_id (default is `None`): the id of the workitem, which
        will be retrieved if not specified
    :param raw_data: the raw data ( OrderedDict ) of the request response
    """

    log = logging.getLogger("workitem.Workitem")

    OSLC_CR_RDF = "application/rdf+xml"

    def __init__(self, url, rtc_obj, workitem_id=None, raw_data=None):
        self.identifier = workitem_id
        FieldBase.__init__(self, url, rtc_obj, raw_data)

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

        cust_attr = (self.raw_data.get("rtc_cm:state")
                                  .get("@rdf:resource")
                                  .split("/")[-2])
        return self.rtc_obj._get_paged_resources("Action",
                                                 projectarea_id=self.contextId,
                                                 customized_attr=cust_attr,
                                                 page_size="100")

    def getAction(self, action_name):
        """Get the :class:`rtcclient.models.Action` object by its name

        :param action_name: the name/title of the action
        :return: the :class:`rtcclient.models.Action` object
        :rtype: rtcclient.models.Action
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
