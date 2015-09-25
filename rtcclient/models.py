from rtcclient.base import FieldBase
from rtcclient import urlunquote
import logging


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
