# Task: Rule-Based Chat Bot

## Requirements

Create a Python module `chatbot.py` that implements a rule-based chatbot with conversation state.

### `ChatBot` Class

```python
class ChatBot:
    def __init__(self, name: str = "Bot"):
        """Initialize the chatbot with a display name."""

    def add_rule(self, pattern: str, response: str, priority: int = 0) -> None:
        """Add a response rule.
        - pattern: regex pattern to match against user input (case-insensitive)
        - response: response template. Can contain {name} for bot name,
          {input} for the user's message, and {match} for the matched group.
        - priority: higher priority rules are checked first (default 0)
        """

    def respond(self, user_input: str) -> str:
        """Generate a response to user input.
        - Matches rules by priority (highest first), then by insertion order
        - Returns the response from the first matching rule
        - If no rule matches, returns a default response
        """

    def set_default_response(self, response: str) -> None:
        """Set the fallback response when no rules match."""

    def get_history(self) -> list[dict]:
        """Return conversation history as list of dicts with 'role' ('user'/'bot') and 'message' keys."""

    def reset(self) -> None:
        """Clear conversation history."""

    def add_context(self, key: str, value: str) -> None:
        """Store context that can be referenced in response templates as {context.key}."""
```

### Default Behavior

- Default response (if not set): "I don't understand. Could you rephrase?"
- The bot should store all exchanges in history
- Pattern matching uses Python `re` module with `re.IGNORECASE`

## Acceptance Criteria

- All test cases in `verify/test_outcomes.py` pass
- No external dependencies (stdlib only)
