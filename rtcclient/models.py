from rtcclient.base import FieldBase
from rtcclient import urlunquote
import logging


class Role(FieldBase):
    log = logging.getLogger("models.Role")

    def __str__(self):
        return self.label


class Member(FieldBase):
    """The :class:`Member` in the :class:`ProjectArea`

    """

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
    log = logging.getLogger("models.Administrator")


class ItemType(FieldBase):
    log = logging.getLogger("models.ItemType")

    def __str__(self):
        return self.title


class TeamArea(FieldBase):
    log = logging.getLogger("models.TeamArea")

    def __str__(self):
        return self.title


class PlannedFor(FieldBase):
    log = logging.getLogger("models.PlannedFor")

    def __str__(self):
        return self.title


class FiledAgainst(FieldBase):
    log = logging.getLogger("models.FiledAgainst")

    def __str__(self):
        return self.title


class FoundIn(FieldBase):
    log = logging.getLogger("models.FoundIn")

    def __str__(self):
        return self.title


class Severity(FieldBase):
    log = logging.getLogger("models.Severity")

    def __str__(self):
        return self.title


class Priority(FieldBase):
    log = logging.getLogger("models.Priority")

    def __str__(self):
        return self.title


class Action(FieldBase):
    log = logging.getLogger("models.Action")

    def __str__(self):
        return self.title


class State(FieldBase):
    log = logging.getLogger("models.State")

    def __str__(self):
        return self.title


class Comment(FieldBase):
    log = logging.getLogger("models.Comment")

    def __init__(self, url, rtc_obj, raw_data=None):
        self.id = url.split("/")[-1]
        FieldBase.__init__(self, url, rtc_obj, raw_data)

    def __str__(self):
        return self.id
