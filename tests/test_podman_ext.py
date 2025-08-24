"""Tests for `podman-compose` package."""

import os
import sys

from pathlib import Path
from typing import Generator
from unittest import mock
from unittest.mock import MagicMock, mock_open, patch

import pytest

from sugar.extensions.podman_ext import SugarPodmanComposeExt


@pytest.fixture
def podman_ext() -> SugarPodmanComposeExt:
    """Create a SugarPodmanComposeExt instance for testing."""
    with patch('sugar.extensions.podman_ext.sh'):
        ext = SugarPodmanComposeExt()
        ext.config = {
            'backend': 'podman',
            'profiles': {
                'profile1': {
                    'config-path': '/path/to/docker-compose.yml',
                    'project-name': 'testproject',
                }
            },
            'defaults': {
                'profile': 'profile1',
                'project-name': 'testproject',
            },
        }
        ext.service_profile = {
            'config-path': '/path/to/docker-compose.yml',
            'project-name': 'testproject',
        }
        ext.backend_args = []
        ext.verbose = False
        ext.dry_run = False
        return ext


@pytest.fixture
def mock_sh() -> Generator[MagicMock, None, None]:
    """Mock the sh package."""
    with patch('sugar.extensions.podman_ext.sh') as mock:
        mock.Command.return_value = MagicMock()
        yield mock


@pytest.fixture
def mock_yaml_load() -> Generator[MagicMock, None, None]:
    """Mock yaml.safe_load function."""
    with patch('yaml.safe_load') as mock:
        mock.return_value = {
            'services': {
                'service1': {'image': 'image1'},
                'service2': {'image': 'image2'},
            }
        }
        yield mock


class TestSugarPodmanComposeExt:
    """Tests for the SugarPodmanComposeExt class.

    This class contains tests for the functionality provided by the
    SugarPodmanComposeExt class, including backend loading, command execution,
    and various podman-compose operations.
    """

    def test_load_backend_supported(
        self, podman_ext: SugarPodmanComposeExt, mock_sh: MagicMock
    ) -> None:
        """Test _load_backend with a supported backend."""
        with patch.object(
            podman_ext, '_load_podman_compose_args'
        ) as mock_load_args:
            podman_ext._load_backend()
            mock_load_args.assert_called_once()
            mock_sh.Command.assert_called_with('podman-compose')

    def test_load_backend_unsupported(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test _load_backend with an unsupported backend."""
        with mock.patch(
            'sugar.logs.SugarLogs.raise_error', side_effect=SystemExit
        ) as mock_error:
            podman_ext.config['backend'] = 'unsupported'
            with pytest.raises(SystemExit):
                podman_ext._load_backend()
            mock_error.assert_called_once()

    def test_load_podman_compose_args_string_path(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test _load_podman_compose_args with string config path."""
        with (
            patch.object(podman_ext, '_filter_service_profile'),
            patch(
                'sugar.extensions.podman_ext.get_absolute_path'
            ) as mock_get_path,
        ):
            mock_get_path.return_value = '/absolute/path/to/docker-compose.yml'
            podman_ext._load_podman_compose_args()
            assert podman_ext.backend_args == [
                '-f',
                '/absolute/path/to/docker-compose.yml',
                '-p',
                'testproject',
            ]

    def test_load_podman_compose_args_list_path(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test _load_podman_compose_args with list config path."""
        podman_ext.service_profile['config-path'] = [
            '/path1/docker-compose.yml',
            '/path2/docker-compose.yml',
        ]
        with (
            patch.object(podman_ext, '_filter_service_profile'),
            patch(
                'sugar.extensions.podman_ext.get_absolute_path'
            ) as mock_get_path,
        ):
            mock_get_path.side_effect = lambda x: f'/absolute{x}'
            podman_ext._load_podman_compose_args()
            assert podman_ext.backend_args == [
                '-f',
                '/absolute/path1/docker-compose.yml',
                '-f',
                '/absolute/path2/docker-compose.yml',
                '-p',
                'testproject',
            ]

    def test_load_podman_compose_args_invalid_path_type_with_proper_error(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test that _load_podman_compose_args raise TypeError invalid path."""
        podman_ext.service_profile['config-path'] = 123  # Integer is invalid

        with patch.object(podman_ext, '_filter_service_profile'):
            with pytest.raises(TypeError) as excinfo:
                podman_ext._load_podman_compose_args()

            # pathlib (handles both Python version formats)
            error_msg = str(excinfo.value)
            assert any(
                expected in error_msg
                for expected in [
                    'argument should be a str or an os.PathLike object',
                    'expected str, bytes or os.PathLike object',
                ]
            )
            assert 'int' in error_msg

    def test_load_podman_compose_args_none_path(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test _load_podman_compose_args with None as config path."""
        podman_ext.service_profile['config-path'] = None

        with patch.object(podman_ext, '_filter_service_profile'):
            with pytest.raises(TypeError):
                podman_ext._load_podman_compose_args()

    def test_load_podman_compose_args_boolean_path(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test _load_podman_compose_args with boolean as config path."""
        podman_ext.service_profile['config-path'] = True

        with patch.object(podman_ext, '_filter_service_profile'):
            with pytest.raises(TypeError):
                podman_ext._load_podman_compose_args()

    def test_load_podman_compose_args_empty_list(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test _load_podman_compose_args with an empty list."""
        podman_ext.service_profile['config-path'] = []

        with patch.object(podman_ext, '_filter_service_profile'):
            podman_ext._load_podman_compose_args()

            # Should only have project name, no -f args
            assert podman_ext.backend_args == ['-p', 'testproject']

    def test_load_podman_compose_args_list_with_none(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test _load_podman_compose_args with a list containing None."""
        podman_ext.service_profile['config-path'] = [None]

        with patch.object(podman_ext, '_filter_service_profile'):
            with pytest.raises(TypeError):
                podman_ext._load_podman_compose_args()

    def test_load_podman_compose_args_with_pathlib_path(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test _load_podman_compose_args with a pathlib.Path object."""
        test_path = Path('/test/path/compose.yml')
        podman_ext.service_profile['config-path'] = test_path

        with (
            patch.object(podman_ext, '_filter_service_profile'),
            patch(
                'sugar.extensions.podman_ext.get_absolute_path'
            ) as mock_get_path,
        ):
            mock_get_path.return_value = '/absolute/test/path/compose.yml'
            podman_ext._load_podman_compose_args()

            assert podman_ext.backend_args == [
                '-f',
                '/absolute/test/path/compose.yml',
                '-p',
                'testproject',
            ]
            mock_get_path.assert_called_once_with(test_path)

    def test_call_backend_app_basic(
        self, podman_ext: SugarPodmanComposeExt, mock_sh: MagicMock
    ) -> None:
        """Test _call_backend_app basic functionality."""
        EXPECTED_HOOK_CALLS = 2

        mock_process = MagicMock()
        mock_backend_app = mock_sh.Command.return_value
        mock_backend_app.return_value = mock_process
        podman_ext.backend_app = mock_backend_app

        with patch.object(podman_ext, '_execute_hooks') as mock_hooks:
            podman_ext._call_backend_app(
                action='up', services=['service1'], options_args=['-d']
            )

            podman_ext.backend_app.assert_called_with(
                *podman_ext.backend_args,
                'up',
                '-d',
                'service1',
                _in=sys.stdin,
                _out=sys.stdout,
                _err=sys.stderr,
                _no_err=True,
                _env=os.environ.copy(),
                _bg=True,
                _bg_exc=False,
            )
            mock_process.wait.assert_called_once()
            assert mock_hooks.call_count == EXPECTED_HOOK_CALLS

    def test_call_backend_app_with_env_file(
        self, podman_ext: SugarPodmanComposeExt, mock_sh: MagicMock
    ) -> None:
        """Test _call_backend_app with env file."""
        podman_ext.service_profile['env-file'] = '/path/to/.env'

        with (
            patch('sugar.extensions.podman_ext.Path.exists') as mock_exists,
            patch(
                'sugar.extensions.podman_ext.dotenv.dotenv_values'
            ) as mock_dotenv_values,
            patch.object(podman_ext, '_execute_hooks'),
        ):
            mock_exists.return_value = True
            mock_dotenv_values.return_value = {'KEY': 'value'}
            mock_process = MagicMock()
            mock_backend_app = mock_sh.Command.return_value
            mock_backend_app.return_value = mock_process
            podman_ext.backend_app = mock_backend_app

            podman_ext._call_backend_app('up')

            mock_exists.assert_called_once()
            mock_dotenv_values.assert_called_once_with('/path/to/.env')
            mock_process.wait.assert_called_once()

    def test_call_backend_app_dry_run(
        self, podman_ext: SugarPodmanComposeExt, mock_sh: MagicMock
    ) -> None:
        """Test _call_backend_app in dry run mode."""
        podman_ext.dry_run = True
        with patch.object(podman_ext, '_execute_hooks'):
            podman_ext._call_backend_app('up')
            mock_sh.Command.return_value.assert_not_called()

    def test_call_backend_app_error(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test _call_backend_app error handling."""
        # Create a mock error class that matches what the code will catch
        MockErrorReturnCode = type('ErrorReturnCode', (Exception,), {})
        mock_error = MockErrorReturnCode('Mock error')

        # Setup the mock process and backend_app
        mock_process = MagicMock()
        mock_process.wait.side_effect = mock_error
        podman_ext.backend_app = MagicMock(return_value=mock_process)

        # Test the error handling
        with patch.object(podman_ext, '_execute_hooks') as mock_hooks:
            with (
                patch(
                    'sugar.extensions.podman_ext.sh.ErrorReturnCode',
                    new=MockErrorReturnCode,
                ),
                patch(
                    'sugar.extensions.podman_ext.SugarLogs.raise_error',
                    side_effect=SystemExit,
                ) as mock_raise_error,
            ):
                with pytest.raises(SystemExit):
                    podman_ext._call_backend_app('up')

                mock_raise_error.assert_called_once()
                assert mock_hooks.call_count == 1

    def test_call_backend_app_keyboard_interrupt(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test _call_backend_app keyboard interrupt handling."""
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_backend_app = MagicMock(return_value=mock_process)
        podman_ext.backend_app = mock_backend_app
        mock_process.wait.side_effect = KeyboardInterrupt()

        with patch(
            'sugar.extensions.podman_ext.sh.ErrorReturnCode',
            new=type('ErrorReturnCode', (Exception,), {}),
        ):
            with patch.object(podman_ext, '_execute_hooks'):
                with patch(
                    'sugar.extensions.podman_ext.SugarLogs.raise_error',
                    side_effect=SystemExit,
                ):
                    with pytest.raises(SystemExit):
                        podman_ext._call_backend_app('up')
            mock_process.kill.assert_called_once()

    def test_podman_check_services(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test podman_check_services method."""
        with patch.object(
            podman_ext, '_get_services_names'
        ) as mock_get_services_names:
            mock_get_services_names.side_effect = (
                lambda services, all: ['service1', 'service2', 'service3']
                if all
                else ['service1', 'service2']
            )

            # Test with all=True to find difference
            result = podman_ext.podman_check_services(all=True, services='')
            assert result == ['service3']

            # Test with all=False to get default services
            result = podman_ext.podman_check_services(all=False, services='')
            assert result == ['service1', 'service2']

    def test_get_image_filters(
        self, podman_ext: SugarPodmanComposeExt, mock_yaml_load: MagicMock
    ) -> None:
        """Test _get_image_filters method."""
        with patch('builtins.open', mock_open(read_data='dummy yaml')):
            result = podman_ext._get_image_filters(['service1'])
            assert isinstance(result, list)

    def test_cmd_build(self, podman_ext: SugarPodmanComposeExt) -> None:
        """Test _cmd_build method."""
        with (
            patch.object(
                podman_ext, '_get_services_names'
            ) as mock_get_services_names,
            patch.object(podman_ext, '_call_backend_app') as mock_call_backend,
            patch.object(podman_ext, '_get_list_args') as mock_get_list_args,
        ):
            mock_get_services_names.return_value = ['service1', 'service2']
            mock_get_list_args.return_value = ['-d']

            podman_ext._cmd_build(services='service1,service2', options='-d')

            mock_call_backend.assert_called_once_with(
                'build', services=['service1', 'service2'], options_args=['-d']
            )

    def test_cmd_config(self, podman_ext: SugarPodmanComposeExt) -> None:
        """Test _cmd_config method."""
        with (
            patch.object(podman_ext, '_call_backend_app') as mock_call_backend,
            patch.object(podman_ext, '_get_list_args') as mock_get_list_args,
        ):
            mock_get_list_args.return_value = ['--services']

            podman_ext._cmd_config(options='--services')

            mock_call_backend.assert_called_once_with(
                'config', services=[], options_args=['--services']
            )

    def test_cmd_create(self, podman_ext: SugarPodmanComposeExt) -> None:
        """Test _cmd_create method."""
        with (
            patch.object(
                podman_ext, '_get_services_names'
            ) as mock_get_services_names,
            patch.object(podman_ext, '_call_backend_app') as mock_call_backend,
            patch.object(podman_ext, '_get_list_args') as mock_get_list_args,
        ):
            mock_get_services_names.return_value = ['service1']
            mock_get_list_args.return_value = ['--no-start']

            podman_ext._cmd_create(services='service1', options='--no-start')

            mock_call_backend.assert_called_once_with(
                'run', services=['service1'], options_args=['--no-start']
            )

    def test_cmd_down(self, podman_ext: SugarPodmanComposeExt) -> None:
        """Test _cmd_down method."""
        with (
            patch.object(
                podman_ext, '_get_services_names'
            ) as mock_get_services_names,
            patch.object(podman_ext, '_call_backend_app') as mock_call_backend,
            patch.object(podman_ext, '_get_list_args') as mock_get_list_args,
        ):
            mock_get_services_names.return_value = ['service1', 'service2']
            mock_get_list_args.return_value = ['--volumes']

            podman_ext._cmd_down(
                services='service1,service2', options='--volumes'
            )

            mock_call_backend.assert_called_once_with(
                'down',
                services=['service1', 'service2'],
                options_args=['--volumes'],
            )

    def test_cmd_exec(self, podman_ext: SugarPodmanComposeExt) -> None:
        """Test _cmd_exec method."""
        with (
            patch.object(podman_ext, '_call_backend_app') as mock_call_backend,
            patch.object(podman_ext, '_get_list_args') as mock_get_list_args,
        ):
            mock_get_list_args.side_effect = (
                lambda x: ['-it'] if x == '-it' else ['echo', 'hello']
            )

            podman_ext._cmd_exec(
                service='service1', cmd='echo hello', options='-it'
            )

            mock_call_backend.assert_called_once_with(
                'exec',
                services=['service1'],
                options_args=['-it'],
                cmd_args=['echo', 'hello'],
            )

    def test_cmd_exec_no_service(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test _cmd_exec method with no service specified."""
        with mock.patch(
            'sugar.logs.SugarLogs.raise_error', side_effect=SystemExit
        ) as mock_error:
            with pytest.raises(SystemExit):
                podman_ext._cmd_exec()
            mock_error.assert_called_once()

    def test_cmd_kill(self, podman_ext: SugarPodmanComposeExt) -> None:
        """Test _cmd_kill method."""
        with (
            patch.object(
                podman_ext, '_get_services_names'
            ) as mock_get_services_names,
            patch.object(podman_ext, '_call_backend_app') as mock_call_backend,
            patch.object(podman_ext, '_get_list_args') as mock_get_list_args,
        ):
            mock_get_services_names.return_value = ['service1']
            mock_get_list_args.return_value = ['-s', 'SIGTERM']

            podman_ext._cmd_kill(services='service1', options='-s SIGTERM')

            mock_call_backend.assert_called_once_with(
                'kill', services=['service1'], options_args=['-s', 'SIGTERM']
            )

    def test_cmd_logs(self, podman_ext: SugarPodmanComposeExt) -> None:
        """Test _cmd_logs method."""
        with (
            patch.object(
                podman_ext, '_get_services_names'
            ) as mock_get_services_names,
            patch.object(podman_ext, '_call_backend_app') as mock_call_backend,
            patch.object(podman_ext, '_get_list_args') as mock_get_list_args,
        ):
            mock_get_services_names.return_value = ['service1']
            mock_get_list_args.return_value = ['-f']

            podman_ext._cmd_logs(services='service1', options='-f')

            mock_call_backend.assert_called_once_with(
                'logs', services=['service1'], options_args=['-f']
            )

    def test_cmd_start(self, podman_ext: SugarPodmanComposeExt) -> None:
        """Test _cmd_start method."""
        with (
            patch.object(
                podman_ext, 'podman_check_services'
            ) as mock_check_services,
            patch.object(
                podman_ext, '_get_services_names'
            ) as mock_get_services_names,
            patch.object(podman_ext, '_call_backend_app') as mock_call_backend,
            patch.object(podman_ext, '_get_list_args') as mock_get_list_args,
        ):
            mock_check_services.return_value = []
            mock_get_services_names.return_value = ['service1', 'service2']
            mock_get_list_args.return_value = ['-d']

            podman_ext._cmd_start(services='service1,service2', options='-d')

            mock_call_backend.assert_called_once_with(
                'up', services=['service1', 'service2'], options_args=['-d']
            )

    def test_cmd_start_with_diff_services_correct(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test _cmd_start method with services that don't exist."""
        with (
            mock.patch.object(
                podman_ext, '_get_services_names'
            ) as mock_get_services_names,
            mock.patch.object(
                podman_ext, 'podman_check_services'
            ) as mock_check_services,
            mock.patch.object(
                podman_ext, '_call_backend_app'
            ) as mock_call_backend,
            mock.patch.object(
                podman_ext, '_get_list_args'
            ) as mock_get_list_args,
        ):
            mock_check_services.return_value = ['service3']
            mock_get_services_names.return_value = ['service1', 'service2']
            mock_get_list_args.return_value = ['-d']

            podman_ext._cmd_start(
                services='service1,service2,service3', options='-d'
            )

            mock_check_services.assert_called_once_with(
                services='service1,service2,service3', all=False
            )
            expected_call_count = 2
            assert mock_call_backend.call_count == expected_call_count
            mock_call_backend.assert_any_call(
                'up', services=['service3'], options_args=['-d']
            )
            mock_call_backend.assert_any_call(
                'up', services=['service1', 'service2'], options_args=['-d']
            )

    def test_cmd_start_with_error_from_backend(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test _cmd_start when _call_backend_app raises SystemExit."""
        with (
            mock.patch.object(podman_ext, '_get_services_names'),
            mock.patch.object(
                podman_ext, 'podman_check_services'
            ) as mock_check_services,
            mock.patch.object(
                podman_ext, '_call_backend_app', side_effect=SystemExit
            ) as mock_call_backend,
            mock.patch.object(
                podman_ext, '_get_list_args'
            ) as mock_get_list_args,
        ):
            mock_check_services.return_value = ['service3']
            mock_get_list_args.return_value = []

            with pytest.raises(SystemExit):
                podman_ext._cmd_start(services='service1,service3')

            mock_call_backend.assert_called_once_with(
                'up', services=['service3'], options_args=[]
            )

    def test_cmd_start_logs_info_message(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test _cmd_start logs info message for uninitiated services."""
        with (
            mock.patch.object(podman_ext, '_get_services_names'),
            mock.patch.object(
                podman_ext, 'podman_check_services'
            ) as mock_check_services,
            mock.patch.object(podman_ext, '_call_backend_app'),
            mock.patch('sugar.logs.SugarLogs.print_info') as mock_print_info,
        ):
            mock_check_services.return_value = ['service3']

            podman_ext._cmd_start(services='service1,service3')

            mock_print_info.assert_called_once_with(
                'Running un initated service service3'
            )

    def test_cmd_start_with_all_flag(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test _cmd_start method with all flag set to True."""
        with (
            mock.patch.object(
                podman_ext, '_get_services_names'
            ) as mock_get_services_names,
            mock.patch.object(
                podman_ext, 'podman_check_services'
            ) as mock_check_services,
            mock.patch.object(
                podman_ext, '_call_backend_app'
            ) as mock_call_backend,
            mock.patch.object(
                podman_ext, '_get_list_args'
            ) as mock_get_list_args,
        ):
            mock_check_services.return_value = []
            mock_get_services_names.return_value = [
                'service1',
                'service2',
                'service3',
            ]
            mock_get_list_args.return_value = []

            podman_ext._cmd_start(all=True)

            mock_check_services.assert_called_once_with(services='', all=True)
            mock_call_backend.assert_called_once_with(
                'up',
                services=['service1', 'service2', 'service3'],
                options_args=[],
            )

    def test_cmd_start_print_statement_capture(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test _cmd_start method captures the print statement."""
        with (
            mock.patch.object(
                podman_ext, '_get_services_names'
            ) as mock_get_services_names,
            mock.patch.object(
                podman_ext, 'podman_check_services'
            ) as mock_check_services,
            mock.patch.object(podman_ext, '_call_backend_app'),
            mock.patch('builtins.print') as mock_print,
        ):
            mock_check_services.return_value = []
            mock_get_services_names.return_value = ['service1', 'service2']

            podman_ext._cmd_start(services='service1,service2')

            mock_print.assert_called_once_with(['service1', 'service2'])

    def test_cmd_run(self, podman_ext: SugarPodmanComposeExt) -> None:
        """Test _cmd_run method."""
        with (
            patch.object(podman_ext, '_call_backend_app') as mock_call_backend,
            patch.object(podman_ext, '_get_list_args') as mock_get_list_args,
        ):
            mock_get_list_args.side_effect = (
                lambda x: ['-it'] if x == '-it' else ['echo', 'hello']
            )

            podman_ext._cmd_run(
                service='service1', cmd='echo hello', options='-it'
            )

            mock_call_backend.assert_called_once_with(
                'run',
                services=['service1'],
                options_args=['-it'],
                cmd_args=['echo', 'hello'],
            )

    def test_cmd_run_no_service(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test _cmd_run method with no service specified."""
        with mock.patch(
            'sugar.logs.SugarLogs.raise_error', side_effect=SystemExit
        ) as mock_error:
            with pytest.raises(SystemExit):
                podman_ext._cmd_run()
            mock_error.assert_called_once()

    def test_cmd_rm(self, podman_ext: SugarPodmanComposeExt) -> None:
        """Test _cmd_rm method."""
        with (
            patch.object(
                podman_ext, '_get_services_names'
            ) as mock_get_services_names,
            patch.object(podman_ext, '_call_backend_app') as mock_call_backend,
            patch.object(podman_ext, '_get_list_args') as mock_get_list_args,
        ):
            mock_get_services_names.return_value = ['service1']
            mock_get_list_args.return_value = ['-v', '--force']

            podman_ext._cmd_rm(services='service1', options='--force')

            mock_call_backend.assert_called_once_with(
                'down', services=['service1'], options_args=['-v', '--force']
            )

    def test_cmd_restart_with_detach_flag(
        self, podman_ext: SugarPodmanComposeExt
    ) -> None:
        """Test _cmd_restart method with -d flag."""
        with mock.patch(
            'sugar.logs.SugarLogs.raise_error', side_effect=SystemExit
        ) as mock_error:
            with pytest.raises(SystemExit):
                podman_ext._cmd_restart(options='-d')
            mock_error.assert_called_once()
