"""Outcome-based tests for Markdown parser task."""
import importlib.util
import os
import pytest


def load_solution():
    """Load parse_markdown from the output directory."""
    output_dir = os.environ.get("OUTPUT_DIR", os.getcwd())
    module_path = os.path.join(output_dir, "markdown_parser.py")
    if not os.path.exists(module_path):
        pytest.skip(f"markdown_parser.py not found in {output_dir}")
    spec = importlib.util.spec_from_file_location("markdown_parser", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse_markdown


@pytest.fixture
def parse():
    return load_solution()


# --- Headings ---

def test_h1(parse):
    assert parse("# Hello") == "<h1>Hello</h1>"

def test_h2(parse):
    assert parse("## World") == "<h2>World</h2>"

def test_h3(parse):
    assert parse("### Subheading") == "<h3>Subheading</h3>"

def test_h6(parse):
    assert parse("###### Deep") == "<h6>Deep</h6>"


# --- Inline formatting ---

def test_bold(parse):
    result = parse("This is **bold** text")
    assert "<strong>bold</strong>" in result

def test_italic(parse):
    result = parse("This is *italic* text")
    assert "<em>italic</em>" in result

def test_inline_code(parse):
    result = parse("Use `print()` here")
    assert "<code>print()</code>" in result

def test_link(parse):
    result = parse("Visit [Google](https://google.com)")
    assert '<a href="https://google.com">Google</a>' in result


# --- Paragraphs ---

def test_paragraph(parse):
    assert parse("Hello world") == "<p>Hello world</p>"

def test_two_paragraphs(parse):
    result = parse("First paragraph\n\nSecond paragraph")
    assert "<p>First paragraph</p>" in result
    assert "<p>Second paragraph</p>" in result

def test_empty_input(parse):
    assert parse("") == ""


# --- Unordered lists ---

def test_single_list_item(parse):
    result = parse("- Item one")
    assert "<ul>" in result
    assert "<li>Item one</li>" in result
    assert "</ul>" in result

def test_multiple_list_items(parse):
    result = parse("- Alpha\n- Beta\n- Gamma")
    assert result.count("<ul>") == 1
    assert result.count("</ul>") == 1
    assert "<li>Alpha</li>" in result
    assert "<li>Beta</li>" in result
    assert "<li>Gamma</li>" in result


# --- Mixed content ---

def test_heading_with_bold(parse):
    result = parse("# Hello **World**")
    assert "<h1>" in result
    assert "<strong>World</strong>" in result

def test_paragraph_with_link(parse):
    result = parse("Go to [site](http://example.com) now")
    assert "<p>" in result
    assert '<a href="http://example.com">site</a>' in result

def test_list_with_inline_code(parse):
    result = parse("- Run `npm install`\n- Run `npm start`")
    assert "<li>" in result
    assert "<code>npm install</code>" in result

def test_full_document(parse):
    doc = "# Title\n\nA paragraph with **bold**.\n\n- Item 1\n- Item 2"
    result = parse(doc)
    assert "<h1>Title</h1>" in result
    assert "<strong>bold</strong>" in result
    assert "<li>Item 1</li>" in result
    assert "<li>Item 2</li>" in result
