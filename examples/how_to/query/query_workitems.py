from rtcclient.client import RTCClient
from rtcclient.utils import setup_basic_logging


if __name__ == "__main__":
    # you can remove this if you don't need logging
    # default logging for console output
    setup_basic_logging()

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

    # specify the returned properties: title, id, state, owner
    # This is optional. All properties will be returned if not specified
    returned_prop = "dc:title,dc:identifier,rtc_cm:state,rtc_cm:ownedBy"

    queried_wis = myquery.queryWorkitems(query_str=myquerystr,
                                         projectarea_name=projectarea_name,
                                         returned_properties=returned_prop)
