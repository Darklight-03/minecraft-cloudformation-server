from discord_notifier.lib.message_handler import MessageHandler


def test_set_message():
    m = MessageHandler()
    m.set_message("hello")
    assert m.message.get("content") == "hello"
    assert "embeds" not in m.message.keys()
