from datetime import datetime, timedelta
import croniter
import os
from discord_bot.lib.components import Button, ButtonStyle, ComponentRow
from discord_bot.lib.response import Embed, EmbedColor, Response
from discord_bot.lib.server import Server, ServerState


class ServerMenu:
    def __init__(self, type, server: Server):
        if not server.updated:
            server.update()
        self.server = server
        self.init_menu(type)
        self.fetch_menu_update()

    # Setup initial menu
    def init_menu(self, type):
        self.response = Response(type)
        self.status = Embed().with_title(
            f"Server is currently {self.server.current_state.lower()}"
        )
        self.start_button = Button(
            ButtonStyle.SUCCESS, label="Start", custom_id="button_start_server"
        )
        self.stop_button = Button(
            ButtonStyle.DANGER, label="Stop", custom_id="button_stop_server"
        )
        self.refresh_button = Button(
            ButtonStyle.SECONDARY,
            label="Refresh",
            custom_id="button_refresh_menu",
        )
        self.buttons = ComponentRow()
        self.buttons.add_component(self.start_button)
        self.buttons.add_component(self.stop_button)
        self.buttons.add_component(self.refresh_button)
        self.response.add_component_row(self.buttons)
        self.response.add_embed(self.status)

    # Update menu with new information
    def fetch_menu_update(self):
        if self.server.current_state == ServerState.RUNNING:
            self.start_button.disable()
        if self.server.current_state == ServerState.STOPPED:
            self.stop_button.disable()
        if self.server.stack_status not in [
            "UPDATE_COMPLETE",
            "CREATE_COMPLETE",
            "UPDATE_ROLLBACK_COMPLETE",
        ]:
            self.start_button.disable()
            self.stop_button.disable()
            self.status.title = (
                f"Server is currently {ServerState.verb(self.server.current_state)}..."
            )
        elif not self.server.can_start:
            self.start_button.disable()
        self.update_status()

    # Menu assignments
    def set_status(self, description, color):
        self.status.description = description
        self.status.color = color

    # extra response data
    def add_embed(self, embed):
        self.response.add_embed(embed)
        return self

    def update_status(self):
        if self.server.can_start:
            self.set_status(
                "it will be available until " f"{self.get_next_stop_time()}",
                EmbedColor.GREEN,
            )
        else:
            self.set_status(
                "it will next be available to start at "
                f"{self.get_next_start_time()}",
                EmbedColor.RED,
            )

    def get_next_start_time(self):
        now = datetime.now()
        sched = os.environ["START_SCHEDULE"][1 : 1 - 3]
        sched = sched.replace("?", "*")
        cron = croniter.croniter(sched, now)
        next_date = cron.get_next(datetime)
        cent_time = timedelta(hours=-5)
        next_date = next_date + cent_time
        return str(next_date)

    def get_next_stop_time(self):
        now = datetime.now()
        sched = os.environ["STOP_SCHEDULE"][1 : 1 - 3]
        sched = sched.replace("?", "*")
        cron = croniter.croniter(sched, now)
        next_date = cron.get_next(datetime)
        cent_time = timedelta(hours=-5)
        next_date = next_date + cent_time
        return str(next_date)

    def get_response(self):
        return self.response.get_response()
