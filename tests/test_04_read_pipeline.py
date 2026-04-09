import json
import pytest
import respx
from httpx import Response
from pathlib import Path
from novel.commands import dispatch
from novel.state import load_search_cache

@pytest.fixture
def fake_source(tmp_path):
    source_path = tmp_path / "fake_source.json"
    source_config = {
        "bookSourceName": "Fake Source",
        "bookSourceUrl": "https://example.com",
        "searchUrl": "https://example.com/search/{{key}}/{{page}}",
        "ruleSearch": "$.items[*]",
        "ruleSearchName": "$.name",
        "ruleSearchAuthor": "$.author",
        "ruleBookUrl": "$.url"
    }
    source_path.write_text(json.dumps(source_config))
    return source_path

def test_search_flow(capsys, fake_source, monkeypatch):
    import novel.state
    monkeypatch.setattr(novel.state, "STATE_DIR", fake_source.parent)
    novel.state.SEARCH_CACHE_FILE = fake_source.parent / "search_cache.json"
    novel.state.STATE_FILE = fake_source.parent / "state.json"
    novel.state.ensure_dirs()
    
    # First use source
    dispatch(["use", str(fake_source)])
    
    # Mock HTTP response
    with respx.mock:
        json_resp = {
            "items": [
                {"name": "Book 1", "author": "Author 1", "url": "/book/1"},
                {"name": "Book 2", "author": "Author 2", "url": "/book/2"}
            ]
        }
        respx.get("https://example.com/search/test_query/1").mock(return_value=Response(200, json=json_resp))
        
        dispatch(["search", "test_query"])
        
    captured = capsys.readouterr().out
    assert "Book 1" in captured
    assert "Author 2" in captured
    
    cache = load_search_cache()
    assert len(cache) == 2
    assert cache[0]["name"] == "Book 1"
    assert cache[1]["author"] == "Author 2"


def test_book_info_and_add(capsys, fake_source, monkeypatch):
    import novel.state
    monkeypatch.setattr(novel.state, "STATE_DIR", fake_source.parent)
    novel.state.SEARCH_CACHE_FILE = fake_source.parent / "search_cache.json"
    novel.state.SHELF_FILE = fake_source.parent / "shelf.json"
    novel.state.STATE_FILE = fake_source.parent / "state.json"
    novel.state.ensure_dirs()
    
    source_config = json.loads(fake_source.read_text())
    source_config["ruleBookInfoIntro"] = "$.intro"
    fake_source.write_text(json.dumps(source_config))

    dispatch(["use", str(fake_source)])
    
    # Pre-populate search cache
    cache = [
        {"name": "Book 1", "author": "Author 1", "bookUrl": "/book/1/info"}
    ]
    novel.state.save_search_cache(cache)
    
    with respx.mock:
        book_resp = {"intro": "A great book intro."}
        respx.get("https://example.com/book/1/info").mock(return_value=Response(200, json=book_resp))
        
        dispatch(["add", "1"])
        
    captured = capsys.readouterr().out
    assert "Added 'Book 1' to shelf" in captured
    
    shelf = novel.state.load_shelf()
    assert len(shelf) == 1
    assert shelf[0]["name"] == "Book 1"
    assert shelf[0]["intro"] == "A great book intro."
    
    dispatch(["shelf"])
    captured = capsys.readouterr().out
    assert "[1]  Book 1 - Author 1" in captured

    # Test read command
    dispatch(["read", "1"])
    captured = capsys.readouterr().out
    assert "Now reading: Book 1" in captured
    
    # Test info command
    dispatch(["info"])
    captured = capsys.readouterr().out
    assert "Title:  Book 1" in captured
    assert "A great book intro." in captured


def test_toc_flow(capsys, fake_source, monkeypatch):
    import novel.state
    monkeypatch.setattr(novel.state, "STATE_DIR", fake_source.parent)
    novel.state.SEARCH_CACHE_FILE = fake_source.parent / "search_cache.json"
    novel.state.SHELF_FILE = fake_source.parent / "shelf.json"
    novel.state.STATE_FILE = fake_source.parent / "state.json"
    novel.state.ensure_dirs()
    
    # Configure fake source with TOC rules
    source_config = json.loads(fake_source.read_text())
    source_config["ruleToc"] = "$.items[*]"
    source_config["ruleTocName"] = "$.name"
    source_config["ruleTocUrl"] = "$.url"
    source_config["ruleTocNextUrl"] = "$.nextUrl"
    fake_source.write_text(json.dumps(source_config))
    
    dispatch(["use", str(fake_source)])
    
    # Pre-populate shelf and active book
    shelf = [
        {"name": "Book TOC", "author": "Author A", "tocUrl": "/toc/1"}
    ]
    novel.state.save_shelf(shelf)
    novel.state.set_active_book("Book TOC")
    
    with respx.mock:
        toc_page_1 = {
            "items": [{"name": "Chapter 1", "url": "/ch1"}],
            "nextUrl": "/toc/2"
        }
        toc_page_2 = {
            "items": [{"name": "Chapter 2", "url": "/ch2"}],
            "nextUrl": ""
        }
        respx.get("https://example.com/toc/1").mock(return_value=Response(200, json=toc_page_1))
        respx.get("https://example.com/toc/2").mock(return_value=Response(200, json=toc_page_2))
        
        dispatch(["toc"])
        
    captured = capsys.readouterr().out
    assert "[1] Chapter 1" in captured
    assert "[2] Chapter 2" in captured
    
    # Verify cached correctly
    shelf = novel.state.load_shelf()
    assert "chapters" in shelf[0]
    assert len(shelf[0]["chapters"]) == 2
    assert shelf[0]["chapters"][0]["name"] == "Chapter 1"
