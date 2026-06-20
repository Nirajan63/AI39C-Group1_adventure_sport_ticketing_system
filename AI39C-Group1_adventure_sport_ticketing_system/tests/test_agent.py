"""
Tests for app/chatbot/agent.py.

Covers:
  - _build_llm
  - get_agent_response (happy path, history trimming, list-content replies,
    empty-messages fallback, blank-reply fallback)
"""
import pytest
from unittest.mock import patch, MagicMock

from app.chatbot import agent


# ── _build_llm ───────────────────────────────────────────────────────────
@patch("langchain_openai.ChatOpenAI")
def test_build_llm_uses_env_vars(mock_chat_openai, monkeypatch):
    monkeypatch.setenv("OPENROUTER_MODEL", "openrouter/some-model")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    mock_chat_openai.return_value = "LLM_INSTANCE"

    result = agent._build_llm()

    mock_chat_openai.assert_called_once_with(
        model="openrouter/some-model",
        api_key="test-key",
        base_url="https://openrouter.ai/api/v1",
        temperature=0.3,
        timeout=20,
    )
    assert result == "LLM_INSTANCE"


@patch("langchain_openai.ChatOpenAI")
def test_build_llm_defaults_model_when_env_unset(mock_chat_openai, monkeypatch):
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    agent._build_llm()

    _, kwargs = mock_chat_openai.call_args
    assert kwargs["model"] == "openrouter/free"
    assert kwargs["api_key"] is None


# ── get_agent_response ───────────────────────────────────────────────────
@patch("langchain.agents.create_agent")
@patch("app.chatbot.agent.build_tools")
@patch("app.chatbot.agent._build_llm")
def test_get_agent_response_happy_path(mock_build_llm, mock_build_tools, mock_create_agent):
    mock_build_llm.return_value = "LLM"
    mock_build_tools.return_value = ["TOOL1"]
    mock_agent = MagicMock()
    final_message = MagicMock(content="Paragliding costs NPR 4500.")
    mock_agent.invoke.return_value = {"messages": [final_message]}
    mock_create_agent.return_value = mock_agent

    result = agent.get_agent_response("How much is paragliding?", [], user_id=1)

    mock_build_tools.assert_called_once_with(user_id=1)
    mock_create_agent.assert_called_once_with("LLM", ["TOOL1"], system_prompt=agent.SYSTEM_PROMPT)
    assert result == "Paragliding costs NPR 4500."


@patch("langchain.agents.create_agent")
@patch("app.chatbot.agent.build_tools")
@patch("app.chatbot.agent._build_llm")
def test_get_agent_response_builds_message_history_capped_at_ten(
    mock_build_llm, mock_build_tools, mock_create_agent
):
    mock_build_tools.return_value = []
    mock_agent = MagicMock()
    final_message = MagicMock(content="ok")
    mock_agent.invoke.return_value = {"messages": [final_message]}
    mock_create_agent.return_value = mock_agent

    history = [{"role": "user", "content": f"msg {i}"} for i in range(15)]
    agent.get_agent_response("latest message", history, user_id=None)

    invoke_args = mock_agent.invoke.call_args[0][0]
    messages = invoke_args["messages"]
    # last 10 of history + the new message = 11
    assert len(messages) == 11
    assert messages[-1].content == "latest message"


@patch("langchain.agents.create_agent")
@patch("app.chatbot.agent.build_tools")
@patch("app.chatbot.agent._build_llm")
def test_get_agent_response_no_final_messages_returns_fallback(
    mock_build_llm, mock_build_tools, mock_create_agent
):
    mock_build_tools.return_value = []
    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {"messages": []}
    mock_create_agent.return_value = mock_agent

    result = agent.get_agent_response("hello", [])

    assert result == "I'm not sure how to answer that -- could you rephrase?"


@patch("langchain.agents.create_agent")
@patch("app.chatbot.agent.build_tools")
@patch("app.chatbot.agent._build_llm")
def test_get_agent_response_blank_reply_returns_fallback(
    mock_build_llm, mock_build_tools, mock_create_agent
):
    mock_build_tools.return_value = []
    mock_agent = MagicMock()
    final_message = MagicMock(content="")
    mock_agent.invoke.return_value = {"messages": [final_message]}
    mock_create_agent.return_value = mock_agent

    result = agent.get_agent_response("hello", [])

    assert result == "I'm not sure how to answer that -- could you rephrase?"


@patch("langchain.agents.create_agent")
@patch("app.chatbot.agent.build_tools")
@patch("app.chatbot.agent._build_llm")
def test_get_agent_response_handles_list_content_blocks(
    mock_build_llm, mock_build_tools, mock_create_agent
):
    mock_build_tools.return_value = []
    mock_agent = MagicMock()
    final_message = MagicMock(content=[{"text": "Hello "}, {"text": "world"}, "!"])
    mock_agent.invoke.return_value = {"messages": [final_message]}
    mock_create_agent.return_value = mock_agent

    result = agent.get_agent_response("hi", [])

    assert result == "Hello world!"


@patch("langchain.agents.create_agent")
@patch("app.chatbot.agent.build_tools")
@patch("app.chatbot.agent._build_llm")
def test_get_agent_response_skips_unknown_roles_in_history(
    mock_build_llm, mock_build_tools, mock_create_agent
):
    mock_build_tools.return_value = []
    mock_agent = MagicMock()
    final_message = MagicMock(content="ok")
    mock_agent.invoke.return_value = {"messages": [final_message]}
    mock_create_agent.return_value = mock_agent

    history = [
        {"role": "user", "content": "hi"},
        {"role": "system", "content": "ignored"},
        {"role": "assistant", "content": "hello"},
    ]
    agent.get_agent_response("next message", history)

    invoke_args = mock_agent.invoke.call_args[0][0]
    messages = invoke_args["messages"]
    # user + assistant + new message = 3 (system role skipped)
    assert len(messages) == 3
