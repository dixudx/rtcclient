import pytest
from rtcclient.client import RTCClient
import requests
from utils_test import _search_path


@pytest.fixture(scope="function")
def rtcclient(mocker):
    mock_resp = mocker.MagicMock(spec=requests.Response)
    mock_resp.status_code = 200
    mock_resp.cookies = {"set-cookie": "cookie-id"}

    mocked_cookies = mocker.patch("rtcclient.client.RTCClient._get_cookies")
    mocked_cookies.return_value = mock_resp

    return RTCClient(url="http://test.url:9443/jazz",
                     username="tester1@email.com",
                     password="password",
                     searchpath=_search_path)
