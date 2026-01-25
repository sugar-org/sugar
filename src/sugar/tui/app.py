"""Main application module for the Sugar Terminal User Interface."""

import docker
from pathlib import Path
from typing import Any, Dict, TypeVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Grid, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Label, Rule, Static

from sugar.logs import SugarLogs

# Define type variables for App and Screen
A = TypeVar("A", bound=object)
T = TypeVar("T", bound=object)

# Import screens here (outside class)
from sugar.tui.screens.profiles import ProfileScreen
from sugar.tui.screens.services import ServiceScreen
from sugar.tui.screens.logs import LogsScreen
from sugar.tui.screens.details import DetailsScreen


class SugarTUI(App[A]):
    """Sugar Terminal User Interface application."""

    TITLE = "Sugar TUI — Container Management Simplified"
    CSS_PATH = Path(__file__).parent / "styles/styles.css"

    # ✅ SCREENS dictionary (correct format)
    SCREENS = {
        "profiles": ProfileScreen,
        "services": ServiceScreen,
        "logs": LogsScreen,
        "details": DetailsScreen,
    }

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("p", "app.push_screen('profiles')", "Profiles"),
        Binding("s", "app.push_screen('services')", "Services"),
        Binding("l", "app.push_screen('logs')", "Logs"),
        Binding("d", "app.push_screen('details')", "Details"),
        Binding("r", "refresh", "Refresh"),
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.data = self.load_data()

    def load_data(self) -> Dict[str, Any]:
        """Load real docker data (only)."""
        try:
            client = docker.from_env()
            containers = client.containers.list(all=True)

            profiles = []
            services = []

            for c in containers:
                services.append({
                    "service": c.name,
                    "status": c.status,
                    "ports": str(c.ports),
                    "cpu": "N/A",
                    "memory": "N/A"
                })

            profiles.append({
                "profile": "default",
                "services": ", ".join([c.name for c in containers]),
                "status": "Active" if containers else "Inactive"
            })

            return {
                "profiles": profiles,
                "services": services,
                "system_metrics": {
                    "containers": containers,
                    "active_profiles": str(1 if containers else 0),
                    "running_containers": str(len([c for c in containers if c.status == "running"])),
                    "cpu_usage": "N/A",
                    "memory_usage": "N/A",
                    "disk_usage": "N/A",
                    "network_in": "N/A",
                    "network_out": "N/A",
                    "uptime": "N/A",
                }
            }

        except Exception as e:
            # If docker is not available, return empty but no crash
            SugarLogs.print_warning(f"Docker not available: {e}")
            return {
                "profiles": [],
                "services": [],
                "system_metrics": {
                    "active_profiles": "0",
                    "running_containers": "0",
                    "cpu_usage": "N/A",
                    "memory_usage": "N/A",
                    "disk_usage": "N/A",
                    "network_in": "N/A",
                    "network_out": "N/A",
                    "uptime": "N/A",
                }
            }

    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        yield Header()

        yield Container(
            Vertical(
                Static("SUGAR TERMINAL USER INTERFACE", classes="title"),
                Static("Container Management Dashboard", classes="subtitle"),
                Grid(
                    Vertical(
                        Static("ACTIVE PROFILES", classes="dashboard-header"),
                        self._create_profiles_panel(),
                        classes="dashboard-panel profiles-panel",
                    ),
                    Vertical(
                        Static("RUNNING SERVICES", classes="dashboard-header"),
                        self._create_services_panel(),
                        classes="dashboard-panel services-panel",
                    ),
                    Vertical(
                        Static("SYSTEM METRICS", classes="dashboard-header"),
                        self._create_status_panel(),
                        classes="dashboard-panel metrics-panel",
                    ),
                    Vertical(
                        Static("QUICK ACTIONS", classes="dashboard-header"),
                        self._create_actions_panel(),
                        classes="dashboard-panel actions-panel",
                    ),
                    id="dashboard-grid",
                ),
                id="main-content",
            ),
            id="app-container",
        )

        yield Footer()

    def _create_profiles_panel(self) -> DataTable[Any]:
        profiles_table: DataTable[Any] = DataTable()
        profiles_table.cursor_type = "row"
        profiles_table.add_columns("Profile", "Services", "Status")

        if self.data.get("profiles"):
            for profile in self.data["profiles"]:
                profiles_table.add_row(
                    profile["profile"], profile["services"], profile["status"]
                )
        return profiles_table

    def _create_services_panel(self) -> DataTable[Any]:
        services_table: DataTable[Any] = DataTable()
        services_table.cursor_type = "row"
        services_table.add_columns("Service", "Status", "Ports", "CPU", "Memory")

        if self.data.get("services"):
            for service in self.data["services"]:
                services_table.add_row(
                    service["service"],
                    service["status"],
                    service["ports"],
                    service["cpu"],
                    service["memory"],
                )
        return services_table

    def _create_status_panel(self) -> Vertical:
        metrics = self.data.get("system_metrics", {})

        return Vertical(
            Horizontal(
                Label("Active Profiles:", classes="data-label"),
                Label(metrics.get("active_profiles", "0"), classes="data-value"),
            ),
            Horizontal(
                Label("Running Containers:", classes="data-label"),
                Label(metrics.get("running_containers", "0"), classes="data-value"),
            ),
            Rule(),
            Horizontal(
                Label("CPU Usage:", classes="data-label"),
                Label(metrics.get("cpu_usage", "N/A"), classes="data-value-highlight"),
            ),
            Horizontal(
                Label("Memory Usage:", classes="data-label"),
                Label(
                    metrics.get("memory_usage", "N/A"),
                    classes="data-value-highlight",
                ),
            ),
            Horizontal(
                Label("Disk Usage:", classes="data-label"),
                Label(metrics.get("disk_usage", "N/A"), classes="data-value"),
            ),
            Rule(),
            Horizontal(
                Label("Network In:", classes="data-label"),
                Label(metrics.get("network_in", "N/A"), classes="data-value-blue"),
            ),
            Horizontal(
                Label("Network Out:", classes="data-label"),
                Label(metrics.get("network_out", "N/A"), classes="data-value-purple"),
            ),
            Rule(),
            Horizontal(
                Label("Uptime:", classes="data-label"),
                Label(metrics.get("uptime", "N/A"), classes="data-value"),
            ),
            classes="dashboard-data",
        )

    def _create_actions_panel(self) -> Vertical:
        return Vertical(
            Button("Start All Services", id="start-all-btn", variant="success"),
            Button("Stop All Services", id="stop-all-btn", variant="error"),
            Button("Restart Services", id="restart-all-btn", variant="warning"),
            Button("View Logs", id="view-logs-btn", variant="primary"),
            Button("Service Details", id="details-btn", variant="default"),
            Button("Run Health Checks", id="health-btn", variant="success"),
            classes="action-buttons",
        )

    def on_mount(self) -> None:
        SugarLogs.print_info("Screens loaded from SCREENS dict")

    def action_refresh(self) -> None:
        self.notify("Refreshing dashboard data...")
        self.data = self.load_data()
        self.refresh()

    def action_logs(self) -> None:
        self.notify("Viewing logs...")
        try:
            self.app.push_screen("logs")
        except Exception:
            self.notify("Logs screen not available", severity="error")

    def action_details(self) -> None:
        self.notify("Viewing details...")
        try:
            self.app.push_screen("details")
        except Exception:
            self.notify("Details screen not available", severity="error")

    async def action_back(self) -> None:
        try:
            self.app.pop_screen()
        except Exception as e:
            self.log.debug(f"Could not pop screen: {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button = event.button
        button_text = button.label if hasattr(button, "label") else ""
        button_text_str = str(button_text)

        if "Start" in button_text_str:
            self.notify("Starting all services...", title="Starting")
        elif "Stop" in button_text_str:
            self.notify("Stopping all services...", title="Stopping")
        elif "Restart" in button_text_str:
            self.notify("Restarting all services...", title="Restarting")
        elif "Logs" in button_text_str:
            self.action_logs()
        elif "Details" in button_text_str:
            self.action_details()
        elif "Health" in button_text_str:
            self.notify("Running health checks...", title="Health Check")


def run() -> None:
    SugarLogs.print_info("Inside run() function")
    app: SugarTUI[object] = SugarTUI()
    app.run()


if __name__ == "__main__":
    run()