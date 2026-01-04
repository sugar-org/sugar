"""Tests for Sugar TUI application."""



class TestSugarTUI:
    """Test Sugar TUI app."""

    def test_import_tui(self) -> None:
        """Test TUI can be imported."""
        from sugar.tui.app import SugarApp

        assert SugarApp is not None

    def test_dashboard_screen(self) -> None:
        """Test dashboard screen import."""
        from sugar.tui.screens.dashboard import DashboardScreen

        assert DashboardScreen is not None

    def test_profile_screen(self) -> None:
        """Test profile screen import."""
        from sugar.tui.screens.profile import ProfileScreen

        assert ProfileScreen is not None

    def test_services_screen(self) -> None:
        """Test services screen import."""
        from sugar.tui.screens.services import ServicesScreen

        assert ServicesScreen is not None

    def test_logs_screen(self) -> None:
        """Test logs screen import."""
        from sugar.tui.screens.logs import LogsScreen

        assert LogsScreen is not None
