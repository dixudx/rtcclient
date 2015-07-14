import abc


class RTCBase(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, baseurl, username, password):
        self.baseurl = baseurl
        self.username = username
        self.password = password

    @abc.abstractproperty
    def workitems(self):
        pass
