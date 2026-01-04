"""Main TUI application for Sugar."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header


class SugarApp(Screen):
    """Main Sugar TUI application."""

    CSS = """
    Screen {
        layout: vertical;
    }
    """

    BINDINGS = [
        ('q', 'quit', 'Quit'),
        ('d', 'dashboard', 'Dashboard'),
        ('p', 'profiles', 'Profiles'),
        ('l', 'logs', 'Logs'),
    ]

    def compose(self) -> ComposeResult:
        """Compose the app layout."""
        yield Header()
        yield Container()
        yield Footer()

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def action_dashboard(self) -> None:
        """Go to dashboard."""
        pass

    def action_profiles(self) -> None:
        """Go to profiles."""
        pass

    def action_logs(self) -> None:
        """Go to logs."""
        pass
