"""Logs viewing screen."""

from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Static


class LogsScreen(Screen):
    """View service logs."""

    def compose(self):
        """Compose logs screen."""
        yield Header()
        with Container():
            yield Static('Service Logs', id='title')
            yield Static('Loading logs...', id='logs_content')
        yield Footer()
