"""Tests for HTTP response charset decoding (HTTP-02, D-06, D-07)."""
from __future__ import annotations

from novel.http._encoding import decode_response


def test_decode_uses_content_type_charset():
    """Content-Type charset=gbk is used to decode GBK bytes correctly."""
    chinese_text = '测试中文内容'
    gbk_bytes = chinese_text.encode('gbk')
    result = decode_response(gbk_bytes, 'text/html; charset=gbk')
    assert result == chinese_text


def test_decode_gbk_response():
    """GBK bytes with no Content-Type charset fall back to charset_normalizer detection."""
    chinese_text = '这是一段较长的中文文本，用于测试字符编码自动检测功能。' * 3
    gbk_bytes = chinese_text.encode('gbk')
    result = decode_response(gbk_bytes, '')
    assert result == chinese_text


def test_decode_fallback_charset_normalizer():
    """Longer GBK bytes with no Content-Type are detected correctly by charset_normalizer."""
    chinese_text = (
        '第一章 天才少年\n\n'
        '萧炎站在悬崖边上，望着远方的山脉。'
        '这里是斗气大陆，一个以斗气为尊的世界。'
        '在这个世界里，没有花哨的魔法，有的只是繁衍到极致的斗气。'
    )
    gbk_bytes = chinese_text.encode('gbk')
    result = decode_response(gbk_bytes, 'text/html')
    # No charset in Content-Type, so falls through to charset_normalizer
    assert '萧炎' in result
    assert '斗气大陆' in result


def test_decode_utf8_fallback():
    """Random bytes with no header and failed detection fall back to UTF-8 with replacement."""
    # These bytes are not valid in any common encoding
    bad_bytes = bytes([0x80, 0x81, 0x82, 0x83, 0x84])
    result = decode_response(bad_bytes, '')
    # Should not raise — falls back to UTF-8 replace
    assert isinstance(result, str)
    assert len(result) > 0


def test_decode_utf8_passthrough():
    """Valid UTF-8 content passes through correctly."""
    text = '这是UTF-8编码的中文文本'
    utf8_bytes = text.encode('utf-8')
    result = decode_response(utf8_bytes, 'text/html; charset=utf-8')
    assert result == text
