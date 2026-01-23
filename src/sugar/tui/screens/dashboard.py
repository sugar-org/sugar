"""Dashboard screen for Sugar TUI."""

from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Static


class DashboardScreen(Screen):
    """Dashboard showing profiles and services."""

    def compose(self):
        """Compose dashboard layout."""
        yield Header(show_clock=True)
        with Container():
            yield Static('Sugar Dashboard', id='title')
            yield Static('Profiles: Loading...', id='profiles')
            yield Static('Services: Loading...', id='services')
        yield Footer()
