from discord_bot.lib.response import Embed, Response, ResponseType
from pytest import fixture


@fixture
def embed():
    return (
        Embed().with_title("title").with_color("color").with_description("description")
    )


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
