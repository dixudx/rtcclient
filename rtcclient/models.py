import logging
import os
import re

import xmltodict

from rtcclient import urlunquote, OrderedDict
from rtcclient.base import FieldBase


class Role(FieldBase):
    """The role in the project area or team area"""

    log = logging.getLogger("models.Role")

    def __str__(self):
        return self.label


class Member(FieldBase):
    """The member in the project area"""

    log = logging.getLogger("models.Member")

    def __init__(self, url, rtc_obj, raw_data=None):
        FieldBase.__init__(self, url, rtc_obj, raw_data=raw_data)
        # add a new attribute mainly for the un-recorded member use
        self.email = urlunquote(self.url.split("/")[-1])

    def __str__(self):
        if hasattr(self, "title"):
            return self.title
        return self.email

    def _initialize(self):
        pass

    def __initialize(self):
        pass


class Administrator(Member):
    """The administrator of the project area"""

    log = logging.getLogger("models.Administrator")


class ItemType(FieldBase):
    """The workitem type"""

    log = logging.getLogger("models.ItemType")

    def __str__(self):
        return self.title


class TeamArea(FieldBase):
    """The team area"""

    log = logging.getLogger("models.TeamArea")

    def __str__(self):
        return self.title


class PlannedFor(FieldBase):
    """The project plannedfor defines a start and end date along with an
    iteration breakdown
    """

    log = logging.getLogger("models.PlannedFor")

    def __str__(self):
        return self.title


class FiledAgainst(FieldBase):
    """Category that identifies the component or functional area that the
    work item belongs to.
    """

    log = logging.getLogger("models.FiledAgainst")

    def __str__(self):
        return self.title


class FoundIn(FieldBase):
    """Release in which the issue described in the work item was identified.
    """

    log = logging.getLogger("models.FoundIn")

    def __str__(self):
        return self.title


class Severity(FieldBase):
    """Indication of the impact of the work item"""

    log = logging.getLogger("models.Severity")

    def __str__(self):
        return self.title


class Priority(FieldBase):
    """Ranked importance of a work item"""

    log = logging.getLogger("models.Priority")

    def __str__(self):
        return self.title


class Action(FieldBase):
    """The action to change the state of the workitem"""

    log = logging.getLogger("models.Action")

    def __str__(self):
        return self.title


class State(FieldBase):
    """Status of the work item. For example, New, In Progress, or Resolved."""

    log = logging.getLogger("models.State")

    def __str__(self):
        return self.title


class Comment(FieldBase):
    """Comment about the work item"""

    log = logging.getLogger("models.Comment")

    def __init__(self, url, rtc_obj, raw_data=None):
        self.id = url.split("/")[-1]
        FieldBase.__init__(self, url, rtc_obj, raw_data)

    def __str__(self):
        return self.id


class SavedQuery(FieldBase):
    """User saved query"""

    log = logging.getLogger("models.SavedQuery")

    def __init__(self, url, rtc_obj, raw_data=None):
        self.id = url.split("/")[-1]
        FieldBase.__init__(self, url, rtc_obj, raw_data)

    def __str__(self):
        return self.title


class IncludedInBuild(FieldBase):
    """Which build includes the certain workitem"""

    log = logging.getLogger("models.IncludedInBuild")

    def __str__(self):
        return self.label


class ChangeSet(FieldBase):
    """ChangeSet"""

    log = logging.getLogger("models.ChangeSet")

    def __str__(self):
        return self.label

    def getChanges(self):
        """Get all :class:`rtcclient.models.Change` objects in this changeset

        :return: a :class:`list` contains all the
            :class:`rtcclient.models.Change` objects
        :rtype: list
        """

        identifier = self.url.split("/")[-1]
        resource_url = "/".join([
            "%s" % self.rtc_obj.url, "resource/itemOid",
            "com.ibm.team.scm.ChangeSet",
            "%s?_mediaType=text/xml" % identifier
        ])
        resp = self.get(resource_url,
                        verify=False,
                        proxies=self.rtc_obj.proxies,
                        headers=self.rtc_obj.headers)
        raw_data = xmltodict.parse(resp.content).get("scm:ChangeSet")
        common_changes = dict()
        changes = raw_data.get("changes")
        for (key, value) in raw_data.items():
            if key.startswith("@"):
                continue
            if "changes" != key:
                common_changes[key] = value
        return self._handle_changes(changes, common_changes)

    def _handle_changes(self, changes, common_changes):
        change_objs = list()

        if isinstance(changes, OrderedDict):
            # only one single change
            changes.update(common_changes)
            change_objs.append(Change(None, self.rtc_obj, raw_data=changes))

        elif isinstance(changes, list):
            # multiple changes
            for change in changes:
                change.update(common_changes)
                change_objs.append(Change(None, self.rtc_obj, raw_data=change))

        return change_objs


class Change(FieldBase):
    """Change"""

    log = logging.getLogger("models.Change")

    def __init__(self, url, rtc_obj, raw_data=None):
        FieldBase.__init__(self, url, rtc_obj, raw_data)

    def __str__(self):
        return self.internalId

    def fetchBeforeStateFile(self, file_folder):
        """Fetch the initial file (before the change) to a folder

        If the file is newly added, then `None` will be returned.

        :param file_folder: the folder to store the file
        :return: the :class:`string` object
        :rtype: string
        """

        if u"true" == self.before:
            self.log.info("This file is newly added. No previous file")
        else:
            self.log.info("Fetching initial file of this Change<%s>:" % self)
            return self._fetchFile(self.before, file_folder, override=False)

    def fetchAfterStateFile(self, file_folder):
        """Fetch the final file (after the change) to a folder

        If the file has been deleted, then `None` will be returned.

        :param file_folder: the folder to store the file
        :return: the :class:`string` object
        :rtype: string
        """

        if u"true" == self.after:
            self.log.info("This file has been deleted successfully.")
        else:
            self.log.info("Fetching final file of this Change<%s>:" % self)
            return self._fetchFile(self.after, file_folder)

    def fetchCurrentFile(self, file_folder):
        """Fetch the current/final file (after the change) to a folder

        If the file has been deleted, then `None` will be returned.

        :param file_folder: the folder to store the file
        :return: the :class:`string` object
        :rtype: string
        """

        return self.fetchAfterStateFile(file_folder)

    def _fetchFile(self, state_id, file_folder, override=True):
        if self.raw_data['item']['@xsi:type'] == 'scm:FolderHandle':
            return

        file_url = "/".join([
            "{0}/service",
            ("com.ibm.team.filesystem.service.internal."
             "rest.IFilesystemContentService"), "-",
            ("{1}?itemId={2}&stateId={3}"
             "&platformLineDelimiter=CRLF")
        ])

        file_url = file_url.format(self.rtc_obj.url, self.component, self.item,
                                   state_id)

        self.log.debug("Start fetching file from %s ..." % file_url)

        resp = self.get(file_url, verify=False, headers=self.rtc_obj.headers)
        file_name = re.findall(r".+filename\*=UTF-8''(.+)",
                               resp.headers["content-disposition"])[0]
        file_path = os.path.join(file_folder, file_name)

        if not override and os.path.exists(file_path):
            return

        with open(file_path, "wb") as file_content:
            file_content.write(resp.content)

        self.log.info("Successfully Fetching '%s' to '%s'" %
                      (file_name, file_path))
        return file_path


class Attachment(FieldBase):
    """Attachment of the work item"""

    log = logging.getLogger("models.Attachment")

    def __init__(self, url, rtc_obj, raw_data=None):
        FieldBase.__init__(self, url, rtc_obj, raw_data)

    def __str__(self):
        return self.identifier + ": " + self.title
