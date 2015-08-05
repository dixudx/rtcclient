from rtcclient.client import RTCClient
from rtcclient.utils import setup_logging


if __name__ == "__main__":
    setup_logging()

    url = "https://your_domain:9443/jazz"
    username = "your_username"
    password = "your_password"
    projectarea_name = "your_projectarea_name"
    myclient = RTCClient(url, username, password)

    # query starts here
    myquery = myclient.query

    # customize your query string
    # below query string means: query all the workitems whose title
    # is "use case 1"
    myquerystr = 'dc:title="use case 1"'
    queried_wis = myquery.queryWorkitems(query_str=myquerystr,
                                         projectarea_name=projectarea_name)
    print queried_wis
