"""Profile selection screen."""

from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Static


class ProfileScreen(Screen):
    """Select and manage profiles."""

    def compose(self):
        """Compose profile screen."""
        yield Header()
        with Container():
            yield Static('Available Profiles', id='title')
            yield Static('Loading profiles...', id='profile_list')
        yield Footer()
