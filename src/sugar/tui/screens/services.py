"""Services management screen for interacting with running containers."""

from pathlib import Path
from typing import Any, TypeVar

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Static,
)

T = TypeVar('T')


class ServiceScreen(Screen[T]):
    """Screen to display and manage services."""

    CSS_PATH = Path(__file__).parent.parent / 'styles/screens.css'

    BINDINGS = [
        ('escape', 'app.pop_screen', 'Back'),
        ('l', "app.push_screen('logs')", 'Logs'),
        ('d', "app.push_screen('details')", 'Details'),
        ('r', 'refresh', 'Refresh'),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        yield Container(
            Vertical(
                Static('SERVICE MANAGEMENT', classes='title'),
                Horizontal(
                    Static('Manage your container services', classes='subtitle'),
                    Static('Total Services: 0', classes='subtitle-right', id='total-services'),
                    id='screen-header',
                ),
                Vertical(self._create_services_table(), id='main-table-container'),
                Horizontal(
                    Button('Start', id='start-service', variant='success'),
                    Button('Stop', id='stop-service', variant='error'),
                    Button('Restart', id='restart-service', variant='warning'),
                    Button('Logs', id='logs-service', variant='primary'),
                    Button('Details', id='details-service', variant='default'),
                    Button('Back', id='back-btn', variant='default'),
                    id='profile-actions',
                ),
                id='screen-content',
            ),
            id='screen-container',
        )

        yield Footer()

    def _create_services_table(self) -> DataTable[Any]:
        table: DataTable[Any] = DataTable(id='services-table')
        table.cursor_type = 'row'
        table.styles.height = 7
        table.styles.max_height = 7

        table.add_columns(
            'Service', 'Status', 'Ports', 'Image', 'Container ID'
        )
        return table

    def on_mount(self) -> None:
        self.notify('Services screen loaded')
        self.refresh_data()

    def on_data_table_row_highlighted(self, event):
        self.app.data["selected_container"] = event.row_key.value

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.app.data["selected_container"] = event.row_key.value

    def on_resume(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        app = self.app
        app.data = app.load_data()

        containers = app.data["system_metrics"].get("containers", [])

        table = self.query_one(DataTable)
        table.clear()

        for c in containers:
            ports_dict = c.attrs.get("NetworkSettings", {}).get("Ports") or {}
            ports = []
            for key, mapping in ports_dict.items():
                if mapping:
                    for m in mapping:
                        ports.append(f"{m['HostPort']}->{key.split('/')[0]}")

            # ✅ IMPORTANT: add key=c.name
            table.add_row(
                c.name,
                "● Running" if c.status == "running" else "○ Stopped",
                ", ".join(ports) or "-",
                c.image.tags[0] if c.image.tags else "N/A",
                c.short_id,
                key=c.name
            )

        self.query_one('#total-services', Static).update(f"Total Services: {len(containers)}")

    def action_refresh(self) -> None:
        self.refresh_data()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == 'back-btn':
            self.app.pop_screen()
            return

        table = self.query_one('#services-table', DataTable)
        if table.cursor_row is None:
            self.notify('Please select a service first', severity='error')
            return

        service = table.get_row_at(table.cursor_row)[0]

        containers = self.app.data["system_metrics"].get("containers", [])
        container_obj = next((c for c in containers if c.name == service), None)

        if not container_obj:
            self.notify('Container not found', severity='error')
            return

        try:
            if button_id == 'start-service':
                container_obj.start()
                self.notify(f'Started {service}')

            elif button_id == 'stop-service':
                container_obj.stop()
                self.notify(f'Stopped {service}')

            elif button_id == 'restart-service':
                container_obj.restart()
                self.notify(f'Restarted {service}')

            elif button_id == 'logs-service':
                self.app.data["selected_container"] = service
                self.app.push_screen('logs')

            elif button_id == 'details-service':
                self.app.data["selected_container"] = service
                self.app.push_screen('details')

        except Exception as e:
            self.notify(f'Error: {e}', severity='error')