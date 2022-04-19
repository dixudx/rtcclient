import requests
import pytest
import utils_test
from rtcclient.exception import BadValue, EmptyAttrib
from rtcclient.query import Query
from rtcclient.workitem import Workitem
from rtcclient.models import SavedQuery
from rtcclient import exception


class TestQuery:

    @pytest.fixture(autouse=True)
    def myrtcclient(self, rtcclient):
        myclient = rtcclient
        return myclient

    def test_init_query(self, myrtcclient):
        myqeury = Query(myrtcclient)
        assert myqeury.rtc_obj == myrtcclient
        assert str(myqeury) == ("Query @ RTC Server at "
                                "http://test.url:9443/jazz")
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
        myquery = myrtcclient.query

        # projectarea is not specified
        query_fake_strs = ["fake_test", u"fake_test"]
        for query_str in query_fake_strs:
            with pytest.raises(EmptyAttrib):
                myquery.queryWorkitems(query_str=query_str,
                                       projectarea_id=None,
                                       projectarea_name=None,
                                       returned_properties=None)

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        projectarea_fake_ids = ["fake_id", u"fake_id"]
        for query_str in query_fake_strs:
            for pa_id in projectarea_fake_ids:
                with pytest.raises(BadValue):
                    myquery.queryWorkitems(query_str=query_str,
                                           projectarea_id=pa_id)

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

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        query_valid_strs = ["valid_query_str", u"valid_query_str"]
        projectarea_ids = [
            "_CuZu0HUwEeKicpXBddtqNA", u"_CuZu0HUwEeKicpXBddtqNA"
        ]
        for query_str in query_valid_strs:
            for pa_id in projectarea_ids:
                queried_wis = myquery.queryWorkitems(query_str=query_str,
                                                     projectarea_id=pa_id)
                assert queried_wis == [workitem1]

        queried_wis = myquery.queryWorkitems(query_str="valid_query_str",
                                             projectarea_id=pa_id,
                                             archived=True)
        assert queried_wis == [workitem2]

        # test for other valid id
        projectarea_other_ids = ["valid_id", u"valid_id"]
        for query_str in query_valid_strs:
            for pa_id in projectarea_other_ids:
                # archived
                queried_wis = myquery.queryWorkitems(query_str=query_str,
                                                     projectarea_id=pa_id,
                                                     archived=True)
                assert queried_wis is None

                # unarchived
                queried_wis = myquery.queryWorkitems(query_str=query_str,
                                                     projectarea_id=pa_id,
                                                     archived=False)
                assert queried_wis is None

    @pytest.fixture
    def mock_getsavedqueries(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.read_fixture("savedqueries.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_get_saved_queries(self, myrtcclient, mock_getsavedqueries, mocker):
        # SavedQuery1
        saved_query1_url = ("http://test.url:9443/jazz/resource/"
                            "itemOid/com.ibm.team.workitem.query."
                            "QueryDescriptor/_1CR5MMfiEd6yW_0tvNlbrw")
        saved_query1 = SavedQuery(saved_query1_url, myrtcclient,
                                  utils_test.savedquery1)
        assert saved_query1.url == saved_query1_url
        assert saved_query1.identifier is None
        assert saved_query1.title == "Closed created by me"
        assert saved_query1.description == ("Work items I have created which "
                                            "have been resolved")
        assert saved_query1.results == ("http://test.url:9443/jazz/oslc/"
                                        "queries/_1CR5MMfiEd6yW_0tvNlbrw/"
                                        "rtc_cm:results")
        assert saved_query1.creator == "tester1@email.com"
        assert saved_query1.modified == "2014-02-22T01:23:47.490Z"
        assert saved_query1.modifiedBy == "ADMIN"

        # ignore this fake data
        assert saved_query1.projectArea == [
            "Closed created by me", "Open Track Build Items", "Open Adoptions"
        ]

        # SavedQuery2
        saved_query2_url = ("http://test.url:9443/jazz/resource/itemOid/"
                            "com.ibm.team.workitem.query.QueryDescriptor/"
                            "_1CTHUMfiEd6yW_0tvNlbrw")
        saved_query2 = SavedQuery(saved_query2_url, myrtcclient,
                                  utils_test.savedquery2)

        # SavedQuery3
        saved_query3_url = ("http://test.url:9443/jazz/resource/itemOid/"
                            "com.ibm.team.workitem.query.QueryDescriptor/"
                            "_1CU8gMfiEd6yW_0tvNlbrw")
        saved_query3 = SavedQuery(saved_query3_url, myrtcclient,
                                  utils_test.savedquery3)

        myquery = myrtcclient.query

        # all saved queries in all project areas
        saved_queries = myquery.getAllSavedQueries()
        assert saved_queries == [saved_query1, saved_query2, saved_query3]

        # invalid project area id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        projectarea_fake_ids = ["fake_id", u"fake_id"]
        for projectarea_id in projectarea_fake_ids:
            with pytest.raises(BadValue):
                myquery.getAllSavedQueries(projectarea_id=projectarea_id)

        # valid project area id
        mocked_check_pa_id.return_value = True
        pa_id = "_0qMJUMfiEd6yW_0tvNlbrw"
        saved_queries = myquery.getAllSavedQueries(projectarea_id=pa_id)
        assert saved_queries == [saved_query1, saved_query2]

        saved_queries = myquery.getAllSavedQueries(projectarea_id=pa_id,
                                                   creator="tester1@email.com")
        assert saved_queries == [saved_query1]

        saved_queries = myquery.getAllSavedQueries(projectarea_id=pa_id,
                                                   creator="tester2@email.com")
        assert saved_queries == [saved_query2]

        # # fake creator
        fake_creators = ["fake@email.com", "fake2@email.com"]
        for fake_creator in fake_creators:
            saved_queries = myquery.getAllSavedQueries(projectarea_id=pa_id,
                                                       creator=fake_creator)
            assert saved_queries is None

        # # fake saved query name
        fake_saved_query_names = ["fake name 1", "fake name 2"]
        for sqname in fake_saved_query_names:
            saved_queries = myquery.getAllSavedQueries(projectarea_id=pa_id,
                                                       saved_query_name=sqname)
            assert saved_queries is None

        sqname = "Open Track Build Items"
        saved_queries = myquery.getAllSavedQueries(projectarea_id=pa_id,
                                                   saved_query_name=sqname,
                                                   creator="tester2@email.com")
        assert saved_queries == [saved_query2]

        saved_queries = myquery.getAllSavedQueries(saved_query_name=sqname)
        assert saved_queries == [saved_query2]

        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        saved_queries = myquery.getAllSavedQueries(projectarea_id=pa_id)
        assert saved_queries == [saved_query3]

        saved_queries = myquery.getAllSavedQueries(creator="tester2@email.com")
        assert saved_queries == [saved_query2, saved_query3]

    def test_get_saved_queries_by_name(self, myrtcclient, mock_getsavedqueries):
        myquery = myrtcclient.query

        # SavedQuery1
        saved_query1_url = ("http://test.url:9443/jazz/resource/"
                            "itemOid/com.ibm.team.workitem.query."
                            "QueryDescriptor/_1CR5MMfiEd6yW_0tvNlbrw")
        saved_query1 = SavedQuery(saved_query1_url, myrtcclient,
                                  utils_test.savedquery1)

        # SavedQuery2
        saved_query2_url = ("http://test.url:9443/jazz/resource/itemOid/"
                            "com.ibm.team.workitem.query.QueryDescriptor/"
                            "_1CTHUMfiEd6yW_0tvNlbrw")
        saved_query2 = SavedQuery(saved_query2_url, myrtcclient,
                                  utils_test.savedquery2)

        # SavedQuery3
        saved_query3_url = ("http://test.url:9443/jazz/resource/itemOid/"
                            "com.ibm.team.workitem.query.QueryDescriptor/"
                            "_1CU8gMfiEd6yW_0tvNlbrw")
        saved_query3 = SavedQuery(saved_query3_url, myrtcclient,
                                  utils_test.savedquery3)

        sqname = "Closed created by me"
        saved_queries = myquery.getSavedQueriesByName(sqname)
        assert saved_queries == [saved_query1]

        sqname = "Open Track Build Items"
        saved_queries = myquery.getSavedQueriesByName(sqname)
        assert saved_queries == [saved_query2]

        creator = "tester2@email.com"
        saved_queries = myquery.getSavedQueriesByName(sqname, creator=creator)
        assert saved_queries == [saved_query2]

        sqname = "Open Adoptions"
        saved_queries = myquery.getSavedQueriesByName(sqname)
        assert saved_queries == [saved_query3]

    def test_get_my_saved_queries(self, myrtcclient, mock_getsavedqueries,
                                  mocker):
        myquery = myrtcclient.query

        # SavedQuery1
        saved_query1_url = ("http://test.url:9443/jazz/resource/"
                            "itemOid/com.ibm.team.workitem.query."
                            "QueryDescriptor/_1CR5MMfiEd6yW_0tvNlbrw")
        saved_query1 = SavedQuery(saved_query1_url, myrtcclient,
                                  utils_test.savedquery1)

        saved_queries = myquery.getMySavedQueries()
        assert saved_queries == [saved_query1]

        # fake saved query name
        fake_saved_query_names = ["fake name 1", "fake name 2"]
        for sqname in fake_saved_query_names:
            saved_queries = myquery.getMySavedQueries(saved_query_name=sqname)
            assert saved_queries is None

        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")

        # invalid project area id
        mocked_check_pa_id.return_value = False
        projectarea_fake_ids = ["fake_id", u"fake_id"]
        for projectarea_id in projectarea_fake_ids:
            with pytest.raises(BadValue):
                myquery.getMySavedQueries(projectarea_id=projectarea_id)

        # valid project area id
        mocked_check_pa_id.return_value = True
        pa_id = "_0qMJUMfiEd6yW_0tvNlbrw"
        saved_queries = myquery.getMySavedQueries(projectarea_id=pa_id)
        assert saved_queries == [saved_query1]

        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        saved_queries = myquery.getMySavedQueries(projectarea_id=pa_id)
        assert saved_queries is None

    @pytest.fixture
    def mock_get_workitems(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.read_fixture("workitems.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_run_saved_query(self, myrtcclient, mock_get_workitems):
        myquery = myrtcclient.query

        # SavedQuery1
        saved_query1_url = ("http://test.url:9443/jazz/resource/"
                            "itemOid/com.ibm.team.workitem.query."
                            "QueryDescriptor/_1CR5MMfiEd6yW_0tvNlbrw")
        saved_query1 = SavedQuery(saved_query1_url, myrtcclient,
                                  utils_test.savedquery1)

        # SavedQuery2
        saved_query2_url = ("http://test.url:9443/jazz/resource/itemOid/"
                            "com.ibm.team.workitem.query.QueryDescriptor/"
                            "_1CTHUMfiEd6yW_0tvNlbrw")
        saved_query2 = SavedQuery(saved_query2_url, myrtcclient,
                                  utils_test.savedquery2)

        # SavedQuery3
        saved_query3_url = ("http://test.url:9443/jazz/resource/itemOid/"
                            "com.ibm.team.workitem.query.QueryDescriptor/"
                            "_1CU8gMfiEd6yW_0tvNlbrw")
        saved_query3 = SavedQuery(saved_query3_url, myrtcclient,
                                  utils_test.savedquery3)

        # Workitem1
        workitem1 = Workitem("http://test.url:9443/jazz/oslc/workitems/161",
                             myrtcclient,
                             workitem_id=161,
                             raw_data=utils_test.workitem1)

        for saved_query in [saved_query1, saved_query2, saved_query3]:
            query_workitems = myquery.runSavedQuery(saved_query)
            assert query_workitems == [workitem1]

        # invalid saved query
        for result in [None, "", True, False, 1234]:
            saved_query1.results = result
            with pytest.raises(exception.RTCException):
                myquery.runSavedQuery(saved_query1)

    def test_run_saved_query_by_url(self, myrtcclient, mock_get_workitems):
        myquery = myrtcclient.query

        valid_urls = [("http://test.url:9443/jazz/web/projects/xxxxxx"
                       "&id=_1CR5MMfiEd6yW_0tvNlbrw"),
                      ("http://test.url:9443/jazz/web/projects/xxxxxx"
                       "&id=_1CTHUMfiEd6yW_0tvNlbr"),
                      ("http://test.url:9443/jazz/web/projects/xxxxxx"
                       "&id=_1CU8gMfiEd6yW_0tvNlbrw")]

        # Workitem1
        workitem1 = Workitem("http://test.url:9443/jazz/oslc/workitems/161",
                             myrtcclient,
                             workitem_id=161,
                             raw_data=utils_test.workitem1)

        for valid_url in valid_urls:
            query_workitems = myquery.runSavedQueryByUrl(valid_url)
            assert query_workitems == [workitem1]

        # invalid saved query urls
        invalid_urls = [
            None, "", True, False, "http://test.xxx", "http://xxxxx=",
            "http://xxxx=xxxx="
        ]
        for invalid_url in invalid_urls:
            with pytest.raises(exception.BadValue):
                myquery.runSavedQueryByUrl(invalid_url)

    def test_run_saved_query_by_id(self, myrtcclient, mock_get_workitems):
        myquery = myrtcclient.query

        valid_ids = ["_1CR5MMfiEd6yW_0tvNlbrw", "12345678", "ABCDEFG"]

        # Workitem1
        workitem1 = Workitem("http://test.url:9443/jazz/oslc/workitems/161",
                             myrtcclient,
                             workitem_id=161,
                             raw_data=utils_test.workitem1)

        for valid_id in valid_ids:
            query_workitems = myquery.runSavedQueryByID(valid_id)
            assert query_workitems == [workitem1]

        # invalid saved query IDs
        invalid_ids = [None, "", True, False]
        for invalid_id in invalid_ids:
            with pytest.raises(exception.BadValue):
                myquery.runSavedQueryByID(invalid_id)
