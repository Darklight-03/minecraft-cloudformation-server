from discord_bot.lib.response import Embed, Response, ResponseType


def test_embed():
    e = Embed()
    e.with_title("6")
    assert e.title == "6"
    embed = (
        e.with_title("title")
        .with_color("color")
        .with_description("description")
        .get_dict()
    )
    assert embed == {"title": "title", "description": "description", "color": "color"}


def test_simple_response():
    r = Response(ResponseType.MESSAGE)
    value = r.get_response()
    assert sorted(list(value.keys())) == sorted(["data", "type"])
    assert value["type"] == ResponseType.MESSAGE
    data = value["data"]
    for k in data.keys():
        assert data[k] in [[], {}, ""]


def test_response_with_embed():
    r = Response(ResponseType.COMPONENT_MESSAGE)
    embed = (
        Embed().with_title("title").with_color("color").with_description("description")
    )
    r.add_embed(embed)

    value = r.get_response()
    assert sorted(list(value.keys())) == sorted(["data", "type"])
    assert value["type"] == ResponseType.COMPONENT_MESSAGE
    data = value["data"]
    assert data["embeds"] == [
        {"title": "title", "description": "description", "color": "color"}
    ]
