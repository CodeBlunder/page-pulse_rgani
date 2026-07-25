import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))



import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from auditor import audit_url


@pytest.mark.asyncio
async def test_valid_url_returns_full_report():
    fake_html = """
    <html>
      <head>
        <title>Test Page</title>
        <meta name="description" content="A test page">
      </head>
      <body>
        <h1>Hello World</h1>
        <img src="a.jpg" alt="image">
        <img src="b.jpg">
        <p>Some sample text content here for word count</p>
      </body>
    </html>
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "text/html; charset=utf-8"}
    mock_response.text = fake_html

    with patch("auditor.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        result = await audit_url("https://example.com")

    assert result["http_status"] == 200
    assert result["title"] == "Test Page"
    assert result["meta_description"] == "A test page"
    assert result["h1_count"] == 1
    assert result["images_missing_alt"] == 1 


@pytest.mark.asyncio
async def test_timeout_returns_error():
    with patch("auditor.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.TimeoutException("timed out")
        )
        result = await audit_url("https://slow-site.com")

    assert "error" in result
    assert "timed out" in result["error"].lower()


@pytest.mark.asyncio
async def test_non_html_response_returns_error():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "application/pdf"}
    mock_response.text = "%PDF binary content"

    with patch("auditor.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        result = await audit_url("https://example.com/report.pdf")

    assert "error" in result
    assert "non-html" in result["error"].lower()
