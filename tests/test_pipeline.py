import pytest
import asyncio
from app.pipeline import answer_question

@pytest.mark.asyncio
async def test_ambiguous_returns_graceful():
    resp = await answer_question("What color is the sky for Zed?")
    assert resp.answer
    assert resp.confidence >= 0.0
