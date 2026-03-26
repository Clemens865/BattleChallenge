"""Outcome-based tests for chat bot task."""
import importlib.util
import os
import pytest


def load_solution():
    """Load ChatBot from the output directory."""
    output_dir = os.environ.get("OUTPUT_DIR", os.getcwd())
    module_path = os.path.join(output_dir, "chatbot.py")
    if not os.path.exists(module_path):
        pytest.skip(f"chatbot.py not found in {output_dir}")
    spec = importlib.util.spec_from_file_location("chatbot", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.ChatBot


@pytest.fixture
def ChatBot():
    return load_solution()


@pytest.fixture
def bot(ChatBot):
    b = ChatBot("TestBot")
    b.add_rule(r"hello|hi|hey", "Hello! I'm {name}. How can I help?")
    b.add_rule(r"bye|goodbye", "Goodbye! Have a nice day!")
    b.add_rule(r"my name is (\w+)", "Nice to meet you, {match}!")
    b.add_rule(r"help", "I can chat with you. Try saying hello!", priority=5)
    return b


# --- Basic responses ---

def test_greeting(bot):
    response = bot.respond("hello")
    assert "TestBot" in response

def test_greeting_case_insensitive(bot):
    response = bot.respond("HELLO")
    assert "TestBot" in response

def test_goodbye(bot):
    response = bot.respond("bye")
    assert "Goodbye" in response

def test_pattern_with_capture_group(bot):
    response = bot.respond("my name is Alice")
    assert "Alice" in response


# --- Priority ---

def test_higher_priority_matches_first(ChatBot):
    b = ChatBot()
    b.add_rule(r".*", "Low priority match", priority=0)
    b.add_rule(r"hello", "High priority hello", priority=10)
    response = b.respond("hello")
    assert response == "High priority hello"


# --- Default response ---

def test_default_response(bot):
    response = bot.respond("asdfghjkl")
    assert "don't understand" in response.lower() or "rephrase" in response.lower()

def test_custom_default_response(ChatBot):
    b = ChatBot()
    b.set_default_response("Sorry, no idea.")
    response = b.respond("random input")
    assert response == "Sorry, no idea."


# --- History ---

def test_history_recorded(bot):
    bot.respond("hello")
    history = bot.get_history()
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["message"] == "hello"
    assert history[1]["role"] == "bot"

def test_history_multiple_exchanges(bot):
    bot.respond("hello")
    bot.respond("bye")
    history = bot.get_history()
    assert len(history) == 4

def test_reset_clears_history(bot):
    bot.respond("hello")
    bot.reset()
    assert bot.get_history() == []


# --- Context ---

def test_context_in_response(ChatBot):
    b = ChatBot()
    b.add_context("location", "NYC")
    b.add_rule(r"where", "I'm located in {context.location}")
    response = b.respond("where are you?")
    assert "NYC" in response


# --- Name substitution ---

def test_name_in_response(ChatBot):
    b = ChatBot("Jarvis")
    b.add_rule(r"who are you", "I am {name}")
    response = b.respond("who are you?")
    assert "Jarvis" in response


# --- Edge cases ---

def test_empty_input(bot):
    response = bot.respond("")
    assert isinstance(response, str)
    assert len(response) > 0

def test_no_rules_bot(ChatBot):
    b = ChatBot()
    response = b.respond("anything")
    assert isinstance(response, str)

def test_multiple_matches_uses_first_by_insertion_order(ChatBot):
    b = ChatBot()
    b.add_rule(r"test", "First rule")
    b.add_rule(r"test", "Second rule")
    response = b.respond("test")
    assert response == "First rule"
