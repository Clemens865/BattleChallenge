# Task: Markdown to HTML Parser

## Requirements

Create a Python module `markdown_parser.py` that exports a function `parse_markdown(text: str) -> str`.

The function converts a subset of Markdown syntax to HTML.

### Supported Syntax

1. **Headings**: `# H1`, `## H2`, `### H3` through `###### H6`
   - Output: `<h1>H1</h1>`, `<h2>H2</h2>`, etc.
2. **Bold**: `**text**` -> `<strong>text</strong>`
3. **Italic**: `*text*` -> `<em>text</em>`
4. **Inline code**: `` `code` `` -> `<code>code</code>`
5. **Unordered lists**: Lines starting with `- ` become `<ul><li>...</li></ul>`
   - Consecutive list items should be wrapped in a single `<ul>`
6. **Paragraphs**: Non-special lines become `<p>...</p>`
   - Blank lines separate paragraphs
7. **Links**: `[text](url)` -> `<a href="url">text</a>`

### Rules

- Inline formatting (bold, italic, code, links) can appear inside headings, paragraphs, and list items
- Empty input returns empty string
- Leading/trailing whitespace in the output should be stripped

## Acceptance Criteria

- All test cases in `verify/test_outcomes.py` pass
- No external dependencies (stdlib only)
