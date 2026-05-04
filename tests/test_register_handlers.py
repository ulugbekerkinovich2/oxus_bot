from unittest.mock import AsyncMock, patch

from handlers.users import register


class TestHasApplicationStartGuard:
    """Regression tests for the TypeError crash when /v1/directions returned a non-list."""

    async def _make_message_and_state(self):
        message = AsyncMock()
        state = AsyncMock()
        state.get_data.return_value = {"token": "fake-token"}
        return message, state

    async def test_sends_error_message_when_directions_returns_error_dict(self):
        message, state = await self._make_message_and_state()
        with patch.object(register.send_req, "directions", new=AsyncMock(return_value={
            "error": "Request failed", "detail": "timeout"
        })):
            await register.has_application_start(message, state)

        # The error path sends two messages: the initial header, then the error notice.
        sent_texts = [call.args[0] for call in message.answer.call_args_list]
        assert any("xatolik" in t.lower() or "qayta urinib" in t.lower() for t in sent_texts)

    async def test_sends_error_message_when_directions_returns_none(self):
        message, state = await self._make_message_and_state()
        with patch.object(register.send_req, "directions", new=AsyncMock(return_value=None)):
            # Must not raise — previously crashed with TypeError.
            await register.has_application_start(message, state)
        assert message.answer.await_count >= 1

    async def test_processes_normally_when_directions_returns_list(self):
        message, state = await self._make_message_and_state()
        directions_payload = [
            {"degree_id": 1, "id": 10},
            {"degree_id": 2, "id": 20},
            {"degree_id": 1, "id": 11},  # duplicate degree → should be deduped
        ]
        with patch.object(register.send_req, "directions", new=AsyncMock(return_value=directions_payload)):
            await register.has_application_start(message, state)

        # Final answer carries an InlineKeyboardMarkup with one button per unique degree.
        last_call = message.answer.call_args_list[-1]
        markup = last_call.kwargs.get("reply_markup") or (
            last_call.args[2] if len(last_call.args) > 2 else None
        )
        assert markup is not None
        buttons = markup.inline_keyboard[0]
        assert len(buttons) == 2  # Bakalavr + Magistratura, deduplicated
        labels = {b.text for b in buttons}
        assert labels == {"Bakalavr", "Magistratura"}


class TestHasApplicationCallbackGuard:
    """Regression: line 1682 site — directions() returning a non-list crashed the loop."""

    async def _make_callback_and_state(self, callback_data="degree_1degree_Bakalavr"):
        callback_query = AsyncMock()
        callback_query.data = callback_data
        callback_query.from_user.id = 935920479
        state = AsyncMock()
        state.get_data.return_value = {"token": "fake-token", "degree_id": 1}
        return callback_query, state

    async def test_does_not_crash_when_directions_returns_error_dict(self):
        callback_query, state = await self._make_callback_and_state()
        fake_bot = AsyncMock()
        with patch.object(register.send_req, "directions", new=AsyncMock(return_value={
            "error": "Request failed", "detail": "timeout"
        })), patch.object(register, "bot", new=fake_bot):
            await register.has_application(callback_query, state)
            assert fake_bot.send_message.await_count >= 1

