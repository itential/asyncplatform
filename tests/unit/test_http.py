# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for asyncplatform.http module."""

from http import HTTPStatus
from unittest.mock import Mock

import pytest

from asyncplatform import http


class TestHTTPMethod:
    """Test suite for HTTPMethod enum."""

    def test_http_method_enum_exists(self):
        """Test that HTTPMethod enum is available.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert hasattr(http, "HTTPMethod")

    def test_http_method_get(self):
        """Test HTTPMethod.GET value.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert http.HTTPMethod.GET.value == "GET"

    def test_http_method_post(self):
        """Test HTTPMethod.POST value.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert http.HTTPMethod.POST.value == "POST"

    def test_http_method_put(self):
        """Test HTTPMethod.PUT value.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert http.HTTPMethod.PUT.value == "PUT"

    def test_http_method_patch(self):
        """Test HTTPMethod.PATCH value.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert http.HTTPMethod.PATCH.value == "PATCH"

    def test_http_method_delete(self):
        """Test HTTPMethod.DELETE value.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert http.HTTPMethod.DELETE.value == "DELETE"

    def test_http_method_head(self):
        """Test HTTPMethod.HEAD value.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert http.HTTPMethod.HEAD.value == "HEAD"

    def test_http_method_options(self):
        """Test HTTPMethod.OPTIONS value.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert http.HTTPMethod.OPTIONS.value == "OPTIONS"

    def test_http_method_trace(self):
        """Test HTTPMethod.TRACE value.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert http.HTTPMethod.TRACE.value == "TRACE"

    def test_http_method_connect(self):
        """Test HTTPMethod.CONNECT value.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert http.HTTPMethod.CONNECT.value == "CONNECT"


class TestHTTPStatus:
    """Test suite for HTTPStatus availability."""

    def test_http_status_is_imported(self):
        """Test that HTTPStatus is imported from http module.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert hasattr(http, "HTTPStatus")
        assert http.HTTPStatus == HTTPStatus

    def test_http_status_ok(self):
        """Test HTTPStatus.OK is available.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert http.HTTPStatus.OK.value == 200

    def test_http_status_bad_request(self):
        """Test HTTPStatus.BAD_REQUEST is available.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        assert http.HTTPStatus.BAD_REQUEST.value == 400


class TestResponse:
    """Test suite for Response wrapper class."""

    def create_mock_response(
        self,
        status_code=200,
        headers=None,
        content=b"",
        text="",
        url="http://example.com",
    ):
        """Create a mock ipsdk Response object.

        Args:
            status_code (int): HTTP status code
            headers (dict): Response headers
            content (bytes): Response content as bytes
            text (str): Response content as text
            url (str): Request URL

        Returns:
            Mock: A mock response object

        Raises:
            None
        """
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.headers = headers or {}
        mock_response.content = content
        mock_response.text = text
        mock_response.url = url
        mock_response.request = Mock()
        return mock_response

    def test_response_initialization(self):
        """Test Response wrapper initialization.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_response = self.create_mock_response()
        response = http.Response(mock_response)

        assert response._response == mock_response

    def test_response_status_code(self):
        """Test Response.status_code property.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_response = self.create_mock_response(status_code=201)
        response = http.Response(mock_response)

        assert response.status_code == 201

    def test_response_headers(self):
        """Test Response.headers property.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        headers = {"Content-Type": "application/json"}
        mock_response = self.create_mock_response(headers=headers)
        response = http.Response(mock_response)

        assert response.headers == headers

    def test_response_content(self):
        """Test Response.content property.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        content = b"test content"
        mock_response = self.create_mock_response(content=content)
        response = http.Response(mock_response)

        assert response.content == content

    def test_response_text(self):
        """Test Response.text property.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        text = "test response"
        mock_response = self.create_mock_response(text=text)
        response = http.Response(mock_response)

        assert response.text == text

    def test_response_url(self):
        """Test Response.url property.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        url = "http://api.example.com/endpoint"
        mock_response = self.create_mock_response(url=url)
        response = http.Response(mock_response)

        assert response.url == url

    def test_response_request(self):
        """Test Response.request property.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_response = self.create_mock_response()
        response = http.Response(mock_response)

        assert response.request == mock_response.request

    def test_response_json_success(self):
        """Test Response.json() with valid JSON.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        json_data = {"key": "value", "count": 42}
        mock_response = self.create_mock_response()
        mock_response.json = Mock(return_value=json_data)

        response = http.Response(mock_response)
        result = response.json()

        assert result == json_data
        mock_response.json.assert_called_once()

    def test_response_json_failure(self):
        """Test Response.json() with invalid JSON raises ValueError.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_response = self.create_mock_response()
        mock_response.json = Mock(side_effect=Exception("Invalid JSON"))

        response = http.Response(mock_response)

        with pytest.raises(ValueError) as exc_info:
            response.json()

        assert "Failed to parse response as JSON" in str(exc_info.value)

    def test_response_raise_for_status(self):
        """Test Response.raise_for_status() calls underlying method.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_response = self.create_mock_response()
        mock_response.raise_for_status = Mock()

        response = http.Response(mock_response)
        response.raise_for_status()

        mock_response.raise_for_status.assert_called_once()

    def test_response_is_success_with_2xx_status(self):
        """Test Response.is_success() returns True for 2xx status codes.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        for status_code in [200, 201, 204, 299]:
            mock_response = self.create_mock_response(status_code=status_code)
            response = http.Response(mock_response)
            assert response.is_success() is True, f"Failed for status {status_code}"

    def test_response_is_success_with_non_2xx_status(self):
        """Test Response.is_success() returns False for non-2xx status codes.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        for status_code in [100, 199, 300, 400, 500]:
            mock_response = self.create_mock_response(status_code=status_code)
            response = http.Response(mock_response)
            assert response.is_success() is False, f"Failed for status {status_code}"

    def test_response_is_error_with_4xx_status(self):
        """Test Response.is_error() returns True for 4xx status codes.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        for status_code in [400, 401, 403, 404, 499]:
            mock_response = self.create_mock_response(status_code=status_code)
            response = http.Response(mock_response)
            assert response.is_error() is True, f"Failed for status {status_code}"

    def test_response_is_error_with_5xx_status(self):
        """Test Response.is_error() returns True for 5xx status codes.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        for status_code in [500, 502, 503, 504]:
            mock_response = self.create_mock_response(status_code=status_code)
            response = http.Response(mock_response)
            assert response.is_error() is True, f"Failed for status {status_code}"

    def test_response_is_error_with_2xx_status(self):
        """Test Response.is_error() returns False for 2xx status codes.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        for status_code in [200, 201, 204]:
            mock_response = self.create_mock_response(status_code=status_code)
            response = http.Response(mock_response)
            assert response.is_error() is False, f"Failed for status {status_code}"

    def test_response_is_error_with_3xx_status(self):
        """Test Response.is_error() returns False for 3xx status codes.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        for status_code in [300, 301, 302, 304]:
            mock_response = self.create_mock_response(status_code=status_code)
            response = http.Response(mock_response)
            assert response.is_error() is False, f"Failed for status {status_code}"

    def test_response_repr(self):
        """Test Response.__repr__() string representation.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        url = "http://api.example.com/test"
        mock_response = self.create_mock_response(status_code=200, url=url)
        response = http.Response(mock_response)

        repr_str = repr(response)

        assert "Response" in repr_str
        assert "200" in repr_str
        assert url in repr_str


class TestResponseIntegration:
    """Integration tests for Response class."""

    def test_response_workflow_success(self):
        """Test typical successful response workflow.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        json_data = {"status": "success", "data": [1, 2, 3]}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value=json_data)
        mock_response.url = "http://api.example.com/data"
        mock_response.raise_for_status = Mock()

        response = http.Response(mock_response)

        assert response.is_success() is True
        assert response.is_error() is False
        response.raise_for_status()
        assert response.json() == json_data

    def test_response_workflow_error(self):
        """Test typical error response workflow.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.url = "http://api.example.com/notfound"
        mock_response.text = "Not Found"

        response = http.Response(mock_response)

        assert response.is_success() is False
        assert response.is_error() is True
        assert response.status_code == 404
        assert response.text == "Not Found"
