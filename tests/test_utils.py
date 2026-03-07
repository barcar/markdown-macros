"""Tests for shared utils (meta_from_dict, FRONT_MATTER_RE)."""

from markdown_macros.utils import meta_from_dict


def test_meta_from_dict_non_dict_returns_empty():
    """meta_from_dict returns {} for non-dict input."""
    assert meta_from_dict(None) == {}
    assert meta_from_dict("string") == {}
    assert meta_from_dict([1, 2]) == {}


def test_meta_from_dict_none_value():
    """Keys with None value become [""] in Meta."""
    assert meta_from_dict({"key": None}) == {"key": [""]}


def test_meta_from_dict_list_value():
    """List values are converted to list of strings."""
    assert meta_from_dict({"tags": ["a", "b"]}) == {"tags": ["a", "b"]}


def test_meta_from_dict_lowercase_keys():
    """Keys are lowercased and stripped."""
    assert meta_from_dict({"Title": "x"}) == {"title": ["x"]}
