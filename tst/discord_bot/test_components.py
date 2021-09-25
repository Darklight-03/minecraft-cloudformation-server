from discord_bot.lib.components import ComponentRow, Button, ButtonStyle, ComponentType
from pytest import fixture


@fixture
def emoji():
    # eventually should make an emoji object if we ever use this functionality
    return {"name": "name", "id": "891064634054942740", "animated": False}


@fixture
def button(emoji):
    return Button(
        ButtonStyle.PRIMARY,
        label="label",
        emoji=emoji,
        custom_id="custom_id",
        disabled=False,
    )


@fixture
def component_row_with_button(button):
    row = ComponentRow()
    row.add_component(button)
    return row


# TESTS #
def test_component_row(component_row_with_button, button):
    assert component_row_with_button.get_component("custom_id") == button
    dict = component_row_with_button.get_dict()
    assert dict["type"] == ComponentType.ROW
    assert dict["components"] == [button.get_dict()]


def test_button(button, emoji):
    dict = button.get_dict()
    assert dict["type"] == ComponentType.BUTTON
    assert dict["style"] == ButtonStyle.PRIMARY
    assert dict["label"] == "label"
    assert dict["emoji"] == emoji
    assert dict["custom_id"] == "custom_id"
    assert dict["disabled"] is False
