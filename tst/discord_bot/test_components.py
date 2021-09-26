from discord_bot.lib.components import ButtonStyle, ComponentType


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


def test_enable_button(button):
    button.disabled = True
    button.enable()
    assert not button.disabled


def test_disable_button(button):
    button.disable()
    assert button.disabled


def test_iterator(component_row_with_buttons):
    iterator = iter(component_row_with_buttons)
    assert next(iterator).custom_id == "1"
    assert next(iterator).custom_id == "2"
    assert next(iterator).custom_id == "3"
