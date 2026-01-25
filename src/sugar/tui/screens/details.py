"""Details screen for displaying container and service information."""

from datetime import datetime
from typing import Any, TypeVar

from textual.app import ComposeResult
from textual.containers import Container, Grid, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    Static,
)

T = TypeVar('T')


class DetailsScreen(Screen[T]):
    """Screen to display service details."""

    BINDINGS = [
        ('escape', 'app.pop_screen', 'Back'),
        ('r', 'refresh', 'Refresh'),
        ('l', "app.push_screen('logs')", 'Logs'),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        yield Container(
            Vertical(
                Static('SERVICE DETAILS', classes='title'),
                Horizontal(
                    Static(
                        'Container and configuration information',
                        classes='subtitle',
                    ),
                    Static(id='service-name', classes='subtitle-highlight'),
                    id='screen-header',
                ),
                Grid(
                    Vertical(
                        Static('CONFIGURATION', classes='section-title'),
                        self._create_config_panel(),
                        classes='detail-panel',
                    ),
                    Vertical(
                        Static('STATISTICS', classes='section-title'),
                        self._create_stats_panel(),
                        classes='detail-panel',
                    ),
                    Vertical(
                        Static('VOLUMES', classes='section-title'),
                        self._create_volumes_panel(),
                        classes='detail-panel',
                    ),
                    Vertical(
                        Static('NETWORKS', classes='section-title'),
                        self._create_network_panel(),
                        classes='detail-panel',
                    ),
                    id='details-grid',
                ),
                Horizontal(
                    Button('View Logs', id='logs-btn', variant='primary'),
                    Button('Restart', id='restart-btn', variant='warning'),
                    Button('Stop', id='stop-btn', variant='error'),
                    Button('Back', id='back-btn', variant='default'),
                    id='details-actions',
                ),
                id='screen-content',
            ),
            id='screen-container',
        )

        yield Footer()

    def _create_config_panel(self) -> Vertical:
        return Vertical(
            Horizontal(
                Label('Image:', classes='detail-label'),
                Label('', classes='detail-value', id='image-name'),
            ),
            Horizontal(
                Label('Container ID:', classes='detail-label'),
                Label('', classes='detail-value', id='container-id'),
            ),
            Horizontal(
                Label('Created:', classes='detail-label'),
                Label('', classes='detail-value', id='created-at'),
            ),
            Horizontal(
                Label('Status:', classes='detail-label'),
                Label('', classes='detail-value', id='status'),
            ),
            Horizontal(
                Label('Ports:', classes='detail-label'),
                Label('', classes='detail-value', id='ports'),
            ),
            Horizontal(
                Label('Env Vars:', classes='detail-label'),
                Label('', classes='detail-value', id='env-vars'),
            ),
            id='config-details',
        )

    def _create_stats_panel(self) -> Vertical:
        return Vertical(
            Horizontal(
                Label('CPU Usage:', classes='detail-label'),
                Label('', classes='detail-value', id='cpu-usage'),
            ),
            Horizontal(
                Label('Memory:', classes='detail-label'),
                Label('', classes='detail-value', id='memory-usage'),
            ),
            Horizontal(
                Label('Network In:', classes='detail-label'),
                Label('', classes='detail-value', id='network-in'),
            ),
            Horizontal(
                Label('Network Out:', classes='detail-label'),
                Label('', classes='detail-value', id='network-out'),
            ),
            Horizontal(
                Label('Uptime:', classes='detail-label'),
                Label('', classes='detail-value', id='uptime'),
            ),
            Horizontal(
                Label('Restarts:', classes='detail-label'),
                Label('', classes='detail-value', id='restarts'),
            ),
            id='stats-details',
        )

    def _create_volumes_panel(self) -> DataTable[Any]:
        volumes_table: DataTable[Any] = DataTable(id='volumes-table')
        volumes_table.cursor_type = 'row'
        volumes_table.add_columns('Source', 'Destination', 'Mode')
        return volumes_table

    def _create_network_panel(self) -> DataTable[Any]:
        network_table: DataTable[Any] = DataTable(id='network-table')
        network_table.cursor_type = 'row'
        network_table.add_columns('Network', 'IP Address', 'Gateway')
        return network_table

    def on_mount(self) -> None:
        self.refresh_data()

    def on_resume(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        app = self.app

        # Preserve selected container before refresh
        selected_container = app.data.get("selected_container", None)

        app.data = app.load_data()

        # Restore selected container after refresh
        app.data["selected_container"] = selected_container

        selected = app.data.get("selected_container", None)

        # If rowkey or tuple, convert it to string
        if hasattr(selected, "value"):
            selected = selected.value
        if isinstance(selected, tuple):
            selected = selected[0]

        if not selected:
            self.notify("No container selected", severity="error")
            return

        containers = app.data["system_metrics"].get("containers", [])
        container = next((c for c in containers if c.name == selected), None)

        if not container:
            self.notify("Container not found", severity="error")
            return

        self.query_one('#service-name', Static).update(container.name)
        self.query_one('#image-name', Static).update(
            container.image.tags[0] if container.image.tags else "N/A"
        )
        self.query_one('#container-id', Static).update(container.short_id)

        created_str = container.attrs["Created"].replace("Z", "")
        created = datetime.fromisoformat(created_str).strftime("%Y-%m-%d %H:%M:%S")
        self.query_one('#created-at', Static).update(created)

        self.query_one('#status', Static).update(
            "● Running" if container.status == "running" else "○ Stopped"
        )

        ports_dict = container.attrs.get("NetworkSettings", {}).get("Ports") or {}
        ports = []
        for key, mapping in ports_dict.items():
            if mapping:
                for m in mapping:
                    ports.append(f"{m['HostPort']}->{key.split('/')[0]}")

        self.query_one('#ports', Static).update(", ".join(ports) or "N/A")

        env_vars = container.attrs.get("Config", {}).get("Env") or []
        self.query_one('#env-vars', Static).update(", ".join(env_vars) or "N/A")

        volumes_table = self.query_one('#volumes-table', DataTable)
        volumes_table.clear()
        mounts = container.attrs.get("Mounts", []) or []
        for m in mounts:
            volumes_table.add_row(m.get("Source", "-"), m.get("Destination", "-"), m.get("Mode", "-"))

        network_table = self.query_one('#network-table', DataTable)
        network_table.clear()
        networks = container.attrs.get("NetworkSettings", {}).get("Networks", {}) or {}
        for net, info in networks.items():
            network_table.add_row(net, info.get("IPAddress", "-"), info.get("Gateway", "-"))

        self.query_one('#cpu-usage', Static).update("N/A")
        self.query_one('#memory-usage', Static).update("N/A")
        self.query_one('#network-in', Static).update("N/A")
        self.query_one('#network-out', Static).update("N/A")

        # ✅ FIXED UPTIME
        started_str = container.attrs["State"]["StartedAt"].replace("Z", "")
        started = datetime.fromisoformat(started_str)
        uptime = datetime.now() - started
        self.query_one('#uptime', Static).update(str(uptime).split('.')[0])

        self.query_one('#restarts', Static).update(str(container.attrs["RestartCount"]))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        selected = self.app.data.get("selected_container")
        if hasattr(selected, "value"):
            selected = selected.value

        containers = self.app.data["system_metrics"].get("containers", [])
        container = next((c for c in containers if c.name == selected), None)

        if button_id == 'logs-btn':
            self.app.push_screen('logs')

        elif button_id == 'restart-btn':
            if container:
                try:
                    container.restart()
                    self.notify(f'Restarted {container.name}', title='Restarted')
                    self.refresh_data()
                except Exception as e:
                    self.notify(f'Error restarting container: {e}', severity='error')
            else:
                self.notify("No container selected", severity="error")

        elif button_id == 'stop-btn':
            if container:
                try:
                    container.stop()
                    self.notify(f'Stopped {container.name}', title='Stopped')
                    self.refresh_data()
                except Exception as e:
                    self.notify(f'Error stopping container: {e}', severity='error')
            else:
                self.notify("No container selected", severity="error")

        elif button_id == 'back-btn':
            self.app.pop_screen()