"""Tests for the Compose extension."""

from pathlib import Path

import pytest

from pytest import CaptureFixture
from sugar.extensions.compose import SugarCompose


@pytest.fixture
def sugar_ext() -> SugarCompose:
    """Return a fixture for the Sugar extension instance."""
    test_path = Path(__file__).parent
    compose = SugarCompose()
    compose.load(
        file=str(test_path / 'containers' / '.services.sugar.yaml'),
        dry_run=True,
        verbose=True,
    )
    return compose


def test_cmd_build_service(
    sugar_ext: SugarCompose, capsys: CaptureFixture[str]
) -> None:
    """Test build command with services argument."""
    sugar_ext._cmd_build(services='service1-1', all=False, options='')
    captured = capsys.readouterr()
    for term in 'docker compose build service1-1'.split(' '):
        assert term in captured.out


def test_cmd_build_all(
    sugar_ext: SugarCompose, capsys: CaptureFixture[str]
) -> None:
    """Test build command with all argument."""
    sugar_ext._cmd_build(services='', all=True, options='')
    captured = capsys.readouterr()
    for term in 'docker compose build service1-1 service1-2'.split(' '):
        assert term in captured.out


def test_cmd_pull_service(
    sugar_ext: SugarCompose, capsys: CaptureFixture[str]
) -> None:
    """Test pull command with services argument."""
    sugar_ext._cmd_pull(services='service1-1', all=False, options='')
    captured = capsys.readouterr()
    for term in 'docker compose pull service1-1'.split(' '):
        assert term in captured.out


def test_cmd_pull_all(
    sugar_ext: SugarCompose, capsys: CaptureFixture[str]
) -> None:
    """Test pull command with all argument."""
    sugar_ext._cmd_pull(services='', all=True, options='')
    captured = capsys.readouterr()
    for term in 'docker compose pull service1-1 service1-2'.split(' '):
        assert term in captured.out


def test_cmd_up_all(
    sugar_ext: SugarCompose, capsys: CaptureFixture[str]
) -> None:
    """Test up command with all argument."""
    sugar_ext._cmd_up(services='', all=True, options='-d')
    captured = capsys.readouterr()
    for term in 'docker compose up -d service1-1 service1-2'.split(' '):
        assert term in captured.out


def test_cmd_exec(
    sugar_ext: SugarCompose, capsys: CaptureFixture[str]
) -> None:
    """Test exec command with services argument."""
    sugar_ext._cmd_exec(service='service1-1', options='-T', cmd='env')
    captured = capsys.readouterr()
    for term in 'docker compose exec -T service1-1 env'.split(' '):
        assert term in captured.out


def test_cmd_stop_all(
    sugar_ext: SugarCompose, capsys: CaptureFixture[str]
) -> None:
    """Test stop command with all argument."""
    sugar_ext._cmd_stop(services='', all=True, options='')
    captured = capsys.readouterr()
    for term in 'docker compose stop service1-1 service1-2'.split(' '):
        assert term in captured.out


def test_cmd_run(sugar_ext: SugarCompose, capsys: CaptureFixture[str]) -> None:
    """Test run command with services argument."""
    sugar_ext._cmd_run(service='service1-1', options='-T', cmd='env')
    captured = capsys.readouterr()
    for term in 'docker compose run -T service1-1 env'.split(' '):
        assert term in captured.out


def test_cmd_down(
    sugar_ext: SugarCompose, capsys: CaptureFixture[str]
) -> None:
    """Test down command."""
    sugar_ext._cmd_down(services='', all=False, options='')
    captured = capsys.readouterr()
    for term in 'docker compose down --remove-orphans'.split(' '):
        assert term in captured.out


def test_cmd_start_all(
    sugar_ext: SugarCompose, capsys: CaptureFixture[str]
) -> None:
    """Test start command with all argument."""
    sugar_ext._cmd_restart(services='', all=True)
    captured = capsys.readouterr()
    for term in 'docker compose start service1-1 service1-2'.split(' '):
        assert term in captured.out


def test_cmd_restart_all(
    sugar_ext: SugarCompose, capsys: CaptureFixture[str]
) -> None:
    """Test restart command with all argument."""
    sugar_ext._cmd_restart(services='', all=True)
    captured = capsys.readouterr()
    for term in 'docker compose restart service1-1 service1-2'.split(' '):
        assert term in captured.out


def test_cmd_logs(
    sugar_ext: SugarCompose, capsys: CaptureFixture[str]
) -> None:
    """Test logs command."""
    sugar_ext._cmd_logs(services='', all=False, options='')
    captured = capsys.readouterr()
    for term in 'docker compose logs'.split(' '):
        assert term in captured.out


def test_cmd_images(
    sugar_ext: SugarCompose, capsys: CaptureFixture[str]
) -> None:
    """Test images command."""
    sugar_ext._cmd_images(services='', all=False, options='')
    captured = capsys.readouterr()
    for term in 'docker compose images'.split(' '):
        assert term in captured.out


def test_cmd_version(
    sugar_ext: SugarCompose, capsys: CaptureFixture[str]
) -> None:
    """Test version command."""
    sugar_ext._cmd_version(options='')
    captured = capsys.readouterr()
    for term in 'docker compose version'.split(' '):
        assert term in captured.out


def test_cmd_pause(
    sugar_ext: SugarCompose, capsys: CaptureFixture[str]
) -> None:
    """Test pause command with all argument."""
    sugar_ext._cmd_pause(services='', all=True, options='')
    captured = capsys.readouterr()
    for term in 'docker compose pause service1-1 service1-2'.split(' '):
        assert term in captured.out


def test_cmd_unpause(
    sugar_ext: SugarCompose, capsys: CaptureFixture[str]
) -> None:
    """Test unpause command with all argument."""
    sugar_ext._cmd_unpause(services='', all=True, options='')
    captured = capsys.readouterr()
    for term in 'docker compose unpause service1-1 service1-2'.split(' '):
        assert term in captured.out


def test_cmd_kill(
    sugar_ext: SugarCompose, capsys: CaptureFixture[str]
) -> None:
    """Test kill command with all argument."""
    sugar_ext._cmd_kill(services='', all=True, options='')
    captured = capsys.readouterr()
    for term in 'docker compose kill service1-1 service1-2'.split(' '):
        assert term in captured.out


def test_cmd_build_services_with_spaces(
    sugar_ext: SugarCompose, capsys: CaptureFixture[str]
) -> None:
    """Test that spaces around service names in comma-separated list are trimmed."""
    sugar_ext._cmd_build(services='service1-1, service1-2', all=False, options='')
    captured = capsys.readouterr()
    for term in 'docker compose build service1-1 service1-2'.split(' '):
        assert term in captured.out
