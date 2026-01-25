"""Profiles management screen for Sugar TUI."""

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


class ProfileScreen(Screen[T]):
    """Screen for managing profiles."""

    CSS_PATH = Path(__file__).parent.parent / 'styles/screens.css'

    BINDINGS = [
        ('escape', 'app.pop_screen', 'Back'),
        ('s', "app.push_screen('services')", 'Services'),
        ('r', 'refresh', 'Refresh'),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        yield Container(
            Vertical(
                Static('PROFILE MANAGEMENT', classes='title'),
                Horizontal(
                    Static('Manage your Sugar profiles', classes='subtitle'),
                    Static('Total Profiles: 0', classes='subtitle-right', id='total-profiles'),
                    id='screen-header',
                ),
                Vertical(self._create_profiles_table(), id='main-table-container'),
                Horizontal(
                    Button('Add Profile', id='add-profile-btn', variant='primary'),
                    Button('Edit Profile', id='edit-profile-btn', variant='primary'),
                    Button('Delete Profile', id='delete-profile-btn', variant='error'),
                    Button('Back', id='back-btn', variant='default'),
                    id='profile-actions',
                ),
                id='screen-content',
            ),
            id='screen-container',
        )

        yield Footer()

    def _create_profiles_table(self) -> DataTable[Any]:
        profiles_table: DataTable[Any] = DataTable(id='profiles-detail-table')
        profiles_table.cursor_type = 'row'
        profiles_table.add_columns(
            'Profile', 'Project Name', 'Config Path', 'Services', 'Status'
        )
        return profiles_table

    def on_mount(self) -> None:
        self.notify('Profile screen loaded')
        self.refresh_data()

    def on_resume(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        app = self.app
        app.data = app.load_data()

        containers = app.data["system_metrics"].get("containers", [])

        profiles = {}

        for c in containers:
            name = c.name
            profile = name.split('-', 1)[0] if '-' in name else 'default'

            if profile not in profiles:
                profiles[profile] = {
                    "services": [],
                    "status": "● Active",
                    "project": f"project-{profile}",
                    "config": f"containers/{profile}/compose.yaml"
                }

            profiles[profile]["services"].append(name)

            if c.status != "running":
                profiles[profile]["status"] = "○ Inactive"

        table = self.query_one(DataTable)
        table.clear()

        for profile, data in profiles.items():
            services = ", ".join(data["services"])
            table.add_row(
                profile,
                data["project"],
                data["config"],
                services,
                data["status"]
            )

        self.query_one('#total-profiles', Static).update(f"Total Profiles: {len(profiles)}")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = event.data_table
        row_idx = table.cursor_row
        if row_idx is not None:
            row_data = table.get_row_at(row_idx)
            profile_name = row_data[0]
            self.app.data["selected_profile"] = profile_name
            self.notify(f"Selected profile: {profile_name}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == 'add-profile-btn':
            self.notify('Adding new profile...')
        elif button_id == 'edit-profile-btn':
            table = self.query_one('#profiles-detail-table', DataTable)
            if table.cursor_row is not None:
                profile = table.get_row_at(table.cursor_row)[0]
                self.notify(f'Editing profile: {profile}')
            else:
                self.notify('Please select a profile first', severity='error')
        elif button_id == 'delete-profile-btn':
            table = self.query_one('#profiles-detail-table', DataTable)
            if table.cursor_row is not None:
                profile = table.get_row_at(table.cursor_row)[0]
                self.notify(f'Deleting profile: {profile}', severity='warning')
            else:
                self.notify('Please select a profile first', severity='error')
        elif button_id == 'back-btn':
            self.app.pop_screen()