import pytest

MANY_LINES = "".join(f"line {number}\\n" for number in range(12))


@pytest.mark.parametrize(
    "action, expected_args",
    [
        ("sync", ["sync", "--dir", "{dir}"]),
        ("build", ["build", "--dir", "{dir}"]),
        ("rebuild", ["rebuild", "--dir", "{dir}"]),
        ("status", ["status", "--dir", "{dir}"]),
        ("force", ["sync", "--force", "--dir", "{dir}"]),
    ],
)
def test_action_calls_decks_with_the_configured_directory(run, decks_dir, action, expected_args):
    _, _, called = run(action, output="done\\n")

    expected = [arg.format(dir=decks_dir) for arg in expected_args]
    assert called == expected, f"{action} should call decks with {expected}"


@pytest.mark.parametrize("action", ["sync", "build", "rebuild", "force"])
def test_success_is_a_notification_with_the_summary_line(run, action):
    show, text, _ = run(action, output="building geo\\nbuilt 1, imported 1, removed 0, failed 0\\n")

    assert show == "notify", f"a successful {action} should be a notification"
    assert text == "built 1, imported 1, removed 0, failed 0", "the notification should carry the last output line"


def test_status_opens_in_the_text_view(run):
    show, text, _ = run("status", output="geo.txt: changed\\ntest.txt: 2 new ids\\n")

    assert show == "view", "status should open in the text view"
    assert "geo.txt: changed" in text and "test.txt: 2 new ids" in text, "the text view should show the whole status"


@pytest.mark.parametrize(
    "output, expected_show",
    [
        ("geo.txt: guard tripped, 40% of notes would be deleted\\n", "large"),
        ("already running\\n", "large"),
        (MANY_LINES, "view"),
    ],
)
def test_failure_display_depends_on_its_length(run, output, expected_show):
    show, text, _ = run("sync", output=output, status=1)

    assert show == expected_show, f"a failure of this length should be shown as {expected_show}"
    assert output.split("\\n")[0] in text, "the failure text should be shown"


def test_missing_executable_is_reported_in_large_type(run):
    show, text, called = run("sync", decks_bin="/nowhere/decks")

    assert show == "large", "a missing executable should be reported in large type"
    assert "/nowhere/decks" in text, "the report should name the configured path"
    assert called is None, "nothing should be run"


def test_home_shorthand_is_expanded_in_the_directory(run, tmp_path):
    _, _, called = run("build", output="ok\\n", directory="~/decks")

    assert called[-1] == str(tmp_path / "decks"), "a leading tilde should be expanded to the home directory"


@pytest.mark.parametrize(
    "card",
    [
        "boo is {{c1::doo}}",
        'quote " and backslash \\ stay {{c1::intact}}',
        "Q: What is boo?\nA: Doo.",
        "- starts with a dash {{c1::safely}}",
    ],
)
def test_add_passes_the_card_as_one_argument(run, decks_dir, card):
    show, text, called = run("add", card=card, output="added 1 card, 3 waiting for sync\\n")

    assert called[:4] == ["add", "--dir", str(decks_dir), "--"], "add should end its options before the card"
    assert "\n".join(called[4:]) == card, "the card should arrive as one unchanged argument"
    assert (show, text) == ("notify", "added 1 card, 3 waiting for sync"), "a successful add should be a notification"


def test_rejected_card_is_reported_and_kept_on_the_clipboard(run, stubs):
    show, text, _ = run("add", card="no deletion here", output="line 1: cloze has no deletion\\n", status=2)

    assert show == "large", "a rejected card should be reported in large type"
    assert "cloze has no deletion" in text, "the report should carry the reason"
    assert (stubs / "pbcopy.stdin").read_text() == "no deletion here", "the rejected text should be on the clipboard"


def test_empty_card_is_not_sent(run):
    show, _, called = run("add", card="  ")

    assert show == "large", "an empty card should be reported"
    assert called is None, "decks should not be called for an empty card"


def test_log_opens_the_log_file(run, decks_dir, stubs):
    (decks_dir / "toanki" / "decks.log").write_text("log")
    show, _, _ = run("log")

    assert show == "none", "opening the log should show nothing in Alfred"
    assert (stubs / "open.args").read_text().strip() == str(decks_dir / "toanki" / "decks.log"), (
        "the log file should be opened"
    )


def test_missing_log_is_reported(run):
    show, _, _ = run("log")

    assert show == "large", "a missing log should be reported"


def test_folder_opens_the_decks_directory(run, decks_dir, stubs):
    show, _, _ = run("folder")

    assert show == "none", "opening the folder should show nothing in Alfred"
    assert (stubs / "open.args").read_text().strip() == str(decks_dir), "the decks directory should be opened"
