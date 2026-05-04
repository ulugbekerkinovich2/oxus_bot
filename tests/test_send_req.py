import asyncio

import aiohttp
from aioresponses import aioresponses

from data.config import crm_django_domain
from data.config import domain_name as host
from utils import send_req


CHAT_ID = 935920479
UNIVERSITY_ID = 1
PROFILE_URL = f"https://{crm_django_domain}/detail-user-profile/{CHAT_ID}/{UNIVERSITY_ID}/"
DIRECTIONS_URL = f"https://{host}/v1/directions"


class TestGetUserProfile:
    async def test_returns_json_on_200(self):
        with aioresponses() as m:
            m.get(PROFILE_URL, status=200, payload={"id": 1, "first_name": "Ulug'bek"})
            result = await send_req.get_user_profile(chat_id=CHAT_ID, university_id=UNIVERSITY_ID)
        assert result == {"id": 1, "first_name": "Ulug'bek"}

    async def test_returns_error_dict_on_non_200(self):
        with aioresponses() as m:
            m.get(PROFILE_URL, status=404, body="not found")
            result = await send_req.get_user_profile(chat_id=CHAT_ID, university_id=UNIVERSITY_ID)
        assert result["error"] == "Failed to fetch data"
        assert result["status_code"] == 404
        assert result["detail"] == "not found"

    async def test_returns_error_dict_on_timeout(self):
        """Regression: previously asyncio.TimeoutError propagated and crashed the handler."""
        with aioresponses() as m:
            m.get(PROFILE_URL, exception=asyncio.TimeoutError())
            result = await send_req.get_user_profile(chat_id=CHAT_ID, university_id=UNIVERSITY_ID)
        assert result["error"] == "Request timeout"

    async def test_returns_error_dict_on_client_error(self):
        with aioresponses() as m:
            m.get(PROFILE_URL, exception=aiohttp.ClientConnectionError("boom"))
            result = await send_req.get_user_profile(chat_id=CHAT_ID, university_id=UNIVERSITY_ID)
        assert result["error"] == "Request exception"
        assert "boom" in result["detail"]


class TestDirections:
    TOKEN = "fake-token"

    async def test_returns_list_on_200(self):
        payload = [{"degree_id": 1, "id": 10}, {"degree_id": 2, "id": 20}]
        with aioresponses() as m:
            m.get(DIRECTIONS_URL, status=200, payload=payload)
            result = await send_req.directions(self.TOKEN)
        assert result == payload

    async def test_unwraps_entities_from_paginated_response(self):
        """API may return {entities: [...], pageInfo: {...}} — must unwrap to a list."""
        entities = [{"id": 277, "name_uz": "Kompyuter ilmlari"}]
        payload = {"entities": entities, "pageInfo": {"currentCount": 1, "totalCount": 1}}
        with aioresponses() as m:
            m.get(DIRECTIONS_URL, status=200, payload=payload)
            result = await send_req.directions(self.TOKEN)
        assert result == entities

    async def test_returns_error_dict_on_non_200(self):
        with aioresponses() as m:
            m.get(DIRECTIONS_URL, status=500)
            result = await send_req.directions(self.TOKEN)
        assert result == {"error": "Failed to fetch data", "status_code": 500}

    async def test_returns_error_dict_on_timeout(self):
        """Regression: timeout used to raise and crash the calling handler."""
        with aioresponses() as m:
            m.get(DIRECTIONS_URL, exception=asyncio.TimeoutError())
            result = await send_req.directions(self.TOKEN)
        assert result["error"] == "Request failed"

    async def test_returns_error_dict_on_client_error(self):
        with aioresponses() as m:
            m.get(DIRECTIONS_URL, exception=aiohttp.ClientConnectionError("network down"))
            result = await send_req.directions(self.TOKEN)
        assert result["error"] == "Request failed"
        assert "network down" in result["detail"]
