import pytest

def actions(items):
    return [item["variables"]["action"] for item in items]


def test_empty_query_lists_every_action_with_sync_first(filter_items):
    assert actions(filter_items("")) == ["sync", "build", "status", "edit", "rebuild", "force", "log", "folder"], (
        "an empty query should list every action, sync first"
    )


@pytest.mark.parametrize(
    "query, expected",
    [
        ("s", ["sync", "status"]),
        ("sy", ["sync"]),
        ("re", ["rebuild"]),
        ("b", ["build"]),
        ("fo", ["force", "folder"]),
        ("zzz", []),
    ],
)
def test_typed_prefix_narrows_the_list(filter_items, query, expected):
    assert actions(filter_items(query)) == expected, f"'{query}' should narrow the list to {expected}"


@pytest.mark.parametrize("action", ["sync", "build", "status", "log", "folder"])
def test_safe_actions_run_on_plain_enter(filter_items, action):
    (item,) = filter_items(action)

    assert item["valid"] is True, f"{action} should run on plain Enter"
    assert "mods" not in item, f"{action} should need no modifier"


@pytest.mark.parametrize("action", ["rebuild", "force"])
def test_heavy_actions_need_the_command_key(filter_items, action):
    (item,) = filter_items(action)

    assert item["valid"] is False, f"{action} should do nothing on plain Enter"
    assert item["mods"]["cmd"]["valid"] is True, f"{action} should run with the command key held"


def test_add_without_text_opens_the_editor(filter_items):
    (item,) = filter_items("add")

    assert item["variables"] == {"action": "edit", "card": ""}, "bare add should open the editor"
    assert item["valid"] is True, "the editor should open on plain Enter"
    assert item["autocomplete"] == "add ", "tab should complete to the add command"


@pytest.mark.parametrize(
    "text",
    [
        "this is cloze {{c1::card}}",
        'he said "boo" is {{c1::doo}}',
        "back\\slash is {{c2::kept::hint}}",
        "декілька slugs пішли чекати на {{c1::spring}}",
    ],
)
def test_add_with_a_cloze_writes_the_card_directly(filter_items, text):
    (item,) = filter_items(f"add {text}")

    assert item["variables"] == {"action": "add", "card": text}, "a cloze one-liner should be passed on unchanged"
    assert item["valid"] is True, "a cloze one-liner should be accepted"


@pytest.mark.parametrize("text", ["what is boo ? doo", "just some words", "unfinished {{c1::"])
def test_add_without_a_cloze_is_rejected(filter_items, text):
    (item,) = filter_items(f"add {text}")

    assert item["valid"] is False, "a one-liner without a cloze deletion should not be accepted"
    assert "editor" in item["subtitle"], "the rejection should point to the editor"
