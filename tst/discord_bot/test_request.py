from pytest import raises


# TESTS #
def test_simple_ping(ping_request):
    assert ping_request.is_ping() is True
    assert ping_request.is_app_command() is False
    assert ping_request.is_component_interaction() is False
    assert ping_request.id == "id"
    assert ping_request.application_id == "application_id"
    assert ping_request.data is None


def test_get_command_invalid_type(ping_request):
    with raises(Exception) as e:
        ping_request.get_command()
    assert "Invalid request type" in str(e)


def test_get_component_invalid_type(ping_request):
    with raises(Exception) as e:
        ping_request.get_component()
    assert "Invalid request type" in str(e)


def test_simple_app_command(get_app_command_request):
    app_command_request = get_app_command_request()
    assert app_command_request.is_app_command() is True
    assert app_command_request.is_ping() is False
    assert app_command_request.is_component_interaction() is False
    assert app_command_request.get_command() == "name"


def test_simple_component_request(get_component_request):
    component_request = get_component_request()
    assert component_request.is_component_interaction() is True
    assert component_request.is_ping() is False
    assert component_request.is_app_command() is False
    assert component_request.get_component() == "custom_id"


def test_interaction_with_member(get_component_request):
    user = {
        "id": "891064634054942740",
        "username": "username",
        "discriminator": "8561",
        "avatar": "abuywe32ba",
    }
    component_request = get_component_request(
        {
            "member": {
                "roles": ["891064634054942740"],
                "joined_at": "329857",
                "deaf": "False",
                "mute": "False",
                "user": user,
            }
        }
    )
    assert component_request.is_component_interaction() is True
    assert component_request.user == user
    assert component_request.member["user"] == user
    assert component_request.member["deaf"] == "False"
