from discord_bot.lib.response import Response, ResponseType


# TESTS #
def test_embed(embed):
    assert embed.get_dict() == {
        "title": "title",
        "description": "description",
        "color": "color",
    }
    assert embed.with_title("no").get_dict() == {
        "title": "no",
        "description": "description",
        "color": "color",
    }


def test_simple_response():
    response = Response(ResponseType.MESSAGE)
    value = response.get_response()
    assert sorted(list(value.keys())) == sorted(["data", "type"])
    assert value["type"] == ResponseType.MESSAGE
    data = value["data"]
    for k in data.keys():
        assert data[k] in [[], {}, ""]


def test_response_with_embed(embed):
    r = Response(ResponseType.COMPONENT_MESSAGE)
    r.add_embed(embed)

    value = r.get_response()
    assert sorted(list(value.keys())) == sorted(["data", "type"])
    assert value["type"] == ResponseType.COMPONENT_MESSAGE
    data = value["data"]
    assert data["embeds"] == [embed.get_dict()]


def test_response_with_components(component_row_with_button):
    r = Response(ResponseType.COMPONENT_MESSAGE)
    r.add_component_row(component_row_with_button)
    value = r.get_response()
    assert value["data"]["components"] == [component_row_with_button.get_dict()]
