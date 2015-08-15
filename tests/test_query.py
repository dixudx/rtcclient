import requests
import pytest
import utils_test
from rtcclient.exception import BadValue, EmptyAttrib
from rtcclient.query import Query
from rtcclient.workitem import Workitem


class TestQuery:
    @pytest.fixture(autouse=True)
    def myrtcclient(self, rtcclient):
        myclient = rtcclient
        return myclient

    def test_init_query(self, myrtcclient):
        myqeury = Query(myrtcclient)
        assert myqeury.rtc_obj == myrtcclient
        assert str(myqeury) == "Query @ RTC Server at http://test.url:9443/jazz"
        assert myqeury.get_rtc_obj() == myrtcclient

    @pytest.fixture
    def mock_query(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.read_fixture("workitems.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_query_workitems(self, myrtcclient, mocker, mock_query):
        myquery = Query(myrtcclient)

        # projectarea is not specified
        with pytest.raises(EmptyAttrib):
            myquery.queryWorkitems(query_str="fake_test",
                                   projectarea_id=None,
                                   projectarea_name=None,
                                   returned_properties=None)

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myquery.queryWorkitems(query_str="fake_test",
                                   projectarea_id="fake_id")

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"

        # Workitem1
        workitem1 = Workitem("http://test.url:9443/jazz/oslc/workitems/161",
                             myrtcclient,
                             workitem_id=161,
                             raw_data=utils_test.workitem1)

        # Workitem2
        workitem2 = Workitem("http://test.url:9443/jazz/oslc/workitems/6329",
                             myrtcclient,
                             workitem_id=6329,
                             raw_data=utils_test.workitem2)

        queried_wis = myquery.queryWorkitems(query_str="valid_query_str",
                                             projectarea_id=pa_id)
        assert queried_wis == [workitem1]

        queried_wis = myquery.queryWorkitems(query_str="valid_query_str",
                                             projectarea_id=pa_id,
                                             archived=True)
        assert queried_wis == [workitem2]

        # test for other valid id
        queried_wis = myquery.queryWorkitems(query_str="valid_query_str",
                                             projectarea_id="valid_id",
                                             archived=True)
        assert queried_wis is None

        queried_wis = myquery.queryWorkitems(query_str="valid_query_str",
                                             projectarea_id="valid_id",
                                             archived=False)
        assert queried_wis is None
