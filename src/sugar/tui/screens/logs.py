"""Log viewer screen for monitoring service and container logs."""

from datetime import datetime
from pathlib import Path
from typing import Optional, TypeVar

import docker
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

MAX_LOG_LINES = 200

T = TypeVar("T", bound=object)


class LogsScreen(Screen[T]):
    """Screen to display service logs with filtering and real-time updates."""

    CSS_PATH = Path(__file__).parent.parent / "styles/screens.css"

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("f", "toggle_follow", "Follow"),
        ("c", "clear_logs", "Clear"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.following = False
        self.log_level: Optional[str] = None
        self.client = docker.from_env()
        self.selected_container_name: Optional[str] = None
        self._interval = None

    def compose(self) -> ComposeResult:
        yield Header()

        yield Container(
            Vertical(
                Static("SERVICE LOGS", classes="title"),
                Horizontal(
                    Static("Real-time container logs", classes="subtitle"),
                    Static(
                        "Auto-refresh: Off",
                        id="refresh-status",
                        classes="auto-refresh-off",
                    ),
                    id="screen-header",
                ),
                Horizontal(
                    Button("All", id="filter-all", variant="primary"),
                    Button("INFO", id="filter-info"),
                    Button("WARN", id="filter-warn", variant="warning"),
                    Button("ERROR", id="filter-error", variant="error"),
                    Button("DEBUG", id="filter-debug", variant="success"),
                    id="log-level-filters",
                ),
                Static(id="logs-display", classes="logs-display"),
                Horizontal(
                    Button("Back", id="back-btn"),
                    Button("Follow", id="follow-btn", variant="primary"),
                    Button("Clear", id="clear-btn", variant="warning"),
                    id="logs-actions",
                ),
                id="screen-content",
            ),
            id="screen-container",
        )

        yield Footer()

    def on_mount(self) -> None:
        self.refresh_logs()

    # ---------------- FIX CORE ---------------- #

    def _get_selected_container(self) -> Optional[str]:
        """Always return container name as string."""
        selected = self.app.data.get("selected_container")

        if isinstance(selected, tuple):
            selected = selected[0]

        if not isinstance(selected, str):
            return None

        return selected

    def refresh_logs(self) -> None:
        """Fetch logs from the selected container."""
        container_name = self._get_selected_container()

        if not container_name:
            self.query_one("#logs-display", Static).update("No container selected.")
            return

        self.selected_container_name = container_name

        try:
            container = self.client.containers.get(container_name)

            logs = container.logs(
                tail=MAX_LOG_LINES,
                timestamps=True,
            ).decode("utf-8", errors="ignore")

            if self.log_level:
                logs = "\n".join(
                    line for line in logs.splitlines()
                    if self.log_level in line
                )

            self.query_one("#logs-display", Static).update(
                logs or "No logs found."
            )

        except Exception as e:
            self.query_one("#logs-display", Static).update(
                f"Error reading logs:\n{e}"
            )

    # ---------------- ACTIONS ---------------- #

    def action_toggle_follow(self) -> None:
        self.following = not self.following

        btn = self.query_one("#follow-btn", Button)
        btn.label = "Following" if self.following else "Follow"
        btn.variant = "success" if self.following else "primary"

        status = self.query_one("#refresh-status", Static)
        status.update(
            "Auto-refresh: On" if self.following else "Auto-refresh: Off"
        )
        status.set_classes(
            "auto-refresh-on" if self.following else "auto-refresh-off"
        )

        if self.following and not self._interval:
            self._interval = self.set_interval(2, self.refresh_logs)
        elif not self.following and self._interval:
            self._interval.stop()
            self._interval = None

    def action_clear_logs(self) -> None:
        self.query_one("#logs-display", Static).update("")

    def apply_filter(self, level: Optional[str] = None) -> None:
        self.log_level = level

        for bid in (
            "filter-all",
            "filter-info",
            "filter-warn",
            "filter-error",
            "filter-debug",
        ):
            self.query_one(f"#{bid}", Button).variant = "default"

        if level:
            self.query_one(f"#filter-{level.lower()}", Button).variant = "primary"
        else:
            self.query_one("#filter-all", Button).variant = "primary"

        self.refresh_logs()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "back-btn":
                self.app.pop_screen()
            case "follow-btn":
                self.action_toggle_follow()
            case "clear-btn":
                self.action_clear_logs()
            case "filter-all":
                self.apply_filter()
            case "filter-info":
                self.apply_filter("INFO")
            case "filter-warn":
                self.apply_filter("WARN")
            case "filter-error":
                self.apply_filter("ERROR")
            case "filter-debug":
                self.apply_filter("DEBUG")