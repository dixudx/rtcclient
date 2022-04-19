import requests

from rtcclient.base import RTCBase


class BaseTestRTC(RTCBase):

    def __str__(self):
        return "Test Base"

    def get_rtc_obj(self):
        pass


class TestRTCBase:

    test_urls = [
        "http://test.url:9443/////", "http://test.url:9443/jazz////",
        "http://test.url:9443/jazz"
    ]

    valid_test_urls = [
        "http://test.url:9443", "http://test.url:9443/jazz",
        "http://test.url:9443/jazz"
    ]

    def test_validate_url(self):
        for idx, test_url in enumerate(self.test_urls):
            test_rtc = BaseTestRTC(test_url)
            assert (
                test_rtc.validate_url(test_url) == self.valid_test_urls[idx])

    def test_validate_url_cls(self):
        for idx, test_url in enumerate(self.test_urls):
            assert (
                BaseTestRTC.validate_url(test_url) == self.valid_test_urls[idx])

    def test_str(self):
        for test_url in self.test_urls:
            test_rtc = BaseTestRTC(test_url)
            assert str(test_rtc) == "Test Base"

    def test_repr(self):
        for test_url in self.test_urls:
            test_rtc = BaseTestRTC(test_url)
            assert repr(test_rtc) == "<BaseTestRTC Test Base>"

    def test_getattr(self):
        for idx, test_url in enumerate(self.test_urls):
            test_rtc = BaseTestRTC(test_url)
            assert test_rtc.url == self.valid_test_urls[idx]
            assert test_rtc["url"] == self.valid_test_urls[idx]

    def test_get_resp(self, mocker):
        # actually the GET method is inherited from requests.get
        # no need for more tests
        mocked_get = mocker.patch("requests.get")
        test_url = "http://test.url:9443/jazz"
        test_rtc = BaseTestRTC(test_url)

        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'get-test': "test"}
        mocked_get.return_value = mock_resp

        resp = test_rtc.get(test_rtc.url,
                            verify=False,
                            headers=test_rtc.CONTENT_XML,
                            proxies=None,
                            timeout=30)
        mocked_get.assert_called_once_with(test_rtc.url,
                                           verify=False,
                                           headers=test_rtc.CONTENT_XML,
                                           proxies=None,
                                           timeout=30)
        assert resp == mock_resp

    def test_post_resp(self, mocker):
        # actually the POST method is inherited from requests.post
        # no need for more tests
        mocked_post = mocker.patch("requests.post")
        test_url = "http://test.url:9443/jazz"
        test_rtc = BaseTestRTC(test_url)

        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'post-test': "post"}
        mocked_post.return_value = mock_resp

        post_data = {"data": "test"}
        resp = test_rtc.post(test_rtc.url,
                             data=post_data,
                             json=None,
                             verify=False,
                             proxies=None,
                             headers=test_rtc.CONTENT_XML,
                             timeout=30)
        mocked_post.assert_called_once_with(test_rtc.url,
                                            data=post_data,
                                            json=None,
                                            verify=False,
                                            proxies=None,
                                            headers=test_rtc.CONTENT_XML,
                                            timeout=30)
        assert resp == mock_resp

    def test_put_resp(self, mocker):
        # actually the PUT method is inherited from requests.put
        # no need for more tests
        mocked_put = mocker.patch("requests.put")
        test_url = "http://test.url:9443/jazz"
        test_rtc = BaseTestRTC(test_url)

        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'post-test': "post"}
        mocked_put.return_value = mock_resp

        post_data = {"data": "test"}
        resp = test_rtc.put(test_rtc.url,
                            data=post_data,
                            json=None,
                            verify=False,
                            proxies=None,
                            headers=test_rtc.CONTENT_XML,
                            timeout=30)
        mocked_put.assert_called_once_with(test_rtc.url,
                                           data=post_data,
                                           json=None,
                                           verify=False,
                                           proxies=None,
                                           headers=test_rtc.CONTENT_XML,
                                           timeout=30)
        assert resp == mock_resp
