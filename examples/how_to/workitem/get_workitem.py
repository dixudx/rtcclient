from rtcclient.client import RTCClient
from rtcclient.utils import setup_basic_logging

if __name__ == "__main__":
    # you can remove this if you don't need logging
    # default logging for console output
    setup_basic_logging()

    url = "https://your_domain:9443/jazz"
    username = "your_username"
    password = "your_password"
    myclient = RTCClient(url, username, password)

    # get all workitems
    # If both projectarea_id and projectarea_name are None, all the workitems
    # in all ProjectAreas will be returned
    workitems_list = myclient.getWorkitems(projectarea_id=None,
                                           projectarea_name=None)

    # get a workitem with its id
    workitem_id = 123456
    wk = myclient.getWorkitem(workitem_id)
