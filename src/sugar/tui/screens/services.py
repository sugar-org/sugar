"""Services management screen."""

from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Static


class ServicesScreen(Screen):
    """Manage services for selected profile."""

    def compose(self):
        """Compose services screen."""
        yield Header()
        with Container():
            yield Static('Services', id='title')
            yield Static('Loading services...', id='services_list')
        yield Footer()
