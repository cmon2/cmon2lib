import pytest
from cmon2lib.cowui.utils import inject_string_into_system_message

@pytest.fixture
def base_body():
    return {"messages": [
        {"role": "user", "content": "Hello"},
        {"role": "system", "content": "System message."}
    ]}

def test_inject_appends_to_existing_system(base_body):
    body = {"messages": [
        {"role": "user", "content": "Hi"},
        {"role": "system", "content": "Sys:"}
    ]}
    inject_string_into_system_message(body, " injected", prefix=" PREFIX:")
    assert body["messages"][1]["content"] == "Sys: PREFIX: injected"

def test_inject_adds_new_system_if_none():
    body = {"messages": [
        {"role": "user", "content": "Hi"}
    ]}
    inject_string_into_system_message(body, "new system", prefix="[P]")
    assert body["messages"][0]["role"] == "system"
    assert body["messages"][0]["content"] == "[P]new system"

def test_inject_handles_non_list_messages():
    body = {"messages": "notalist"}
    inject_string_into_system_message(body, "should not fail")
    assert body["messages"] == "notalist"

def test_inject_handles_non_dict_body():
    body = "notadict"
    inject_string_into_system_message(body, "should not fail")
    assert body == "notadict"

def test_inject_skips_non_dict_messages():
    body = {"messages": ["notadict", {"role": "system", "content": "A"}]}
    inject_string_into_system_message(body, "B", prefix="C")
    assert body["messages"][1]["content"] == "A" + "C" + "B"
