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

    # change workitem id here
    workitem_id = 123456
    wk = myclient.getWorkitem(workitem_id)
    wk.addComment("changeme: add comments here")
