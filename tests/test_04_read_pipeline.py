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
