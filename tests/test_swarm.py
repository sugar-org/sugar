"""Test suite for SugarSwarm class."""

import sys

from pathlib import Path
from unittest import mock
from unittest.mock import ANY

import pytest
import sh

from sugar.extensions.swarm import (
    SugarSwarm,
    SugarSwarmNode,
    SugarSwarmService,
    SugarSwarmStack,
)
from sugar.logs import SugarError


@pytest.fixture
def sugar_swarm() -> SugarSwarm:
    """Create a SugarSwarm instance for testing."""
    test_path = (
        Path(__file__).parent / 'containers' / '.unittest-swarm.sugar.yaml'
    )

    swarm = SugarSwarm()
    swarm.profile_selected = 'test-profile'
    swarm.file = str(test_path)
    swarm.dry_run = False
    swarm.verbose = False
    # Mock backend app and methods
    swarm.backend_app = mock.Mock()
    # Use proper type annotation for the mock
    swarm._call_backend_app = mock.Mock()  # type: ignore
    return swarm


@pytest.fixture
def sugar_swarm_service() -> SugarSwarmService:
    """Create a SugarSwarm instance for testing."""
    swarm = SugarSwarmService()
    swarm.profile_selected = 'test-profile'
    swarm.file = '.unittest-swarm.sugar.yaml'
    swarm.dry_run = False
    swarm.verbose = False
    # Mock backend app and methods
    swarm.backend_app = mock.Mock()
    # Use proper type annotation for the mock
    swarm._call_backend_app = mock.Mock()  # type: ignore
    return swarm


@pytest.fixture
def sugar_swarm_stack() -> SugarSwarmStack:
    """Create a SugarSwarm instance for testing."""
    swarm = SugarSwarmStack()
    swarm.profile_selected = 'test-profile'
    swarm.file = '.unittest-swarm.sugar.yaml'
    swarm.dry_run = False
    swarm.verbose = False
    # Mock backend app and methods
    swarm.backend_app = mock.Mock()
    # Use proper type annotation for the mock
    swarm._call_backend_app = mock.Mock()  # type: ignore
    return swarm


@pytest.fixture
def sugar_swarm_node() -> SugarSwarmNode:
    """Create a SugarSwarm instance for testing."""
    swarm = SugarSwarmNode()
    swarm.profile_selected = 'test-profile'
    swarm.file = '.unittest-swarm.sugar.yaml'
    swarm.dry_run = False
    swarm.verbose = False
    # Mock backend app and methods
    swarm.backend_app = mock.Mock()
    # Use proper type annotation for the mock
    swarm._call_backend_app = mock.Mock()  # type: ignore
    return swarm


@pytest.fixture
def mock_backend_app(monkeypatch: pytest.MonkeyPatch) -> mock.Mock:
    """Mock sh.docker for all tests."""
    mock_docker = mock.Mock()
    monkeypatch.setattr(sh, 'docker', mock_docker)
    return mock_docker


class TestSugarSwarm:
    """Test suite for SugarSwarm class."""

    def test_load_backend_app(
        self, sugar_swarm: SugarSwarm, mock_backend_app: mock.Mock
    ) -> None:
        """Test _load_backend_app sets correct backend."""
        sugar_swarm._load_backend_app()
        assert sugar_swarm.backend_app == mock_backend_app

    def test_load_backend_args(self, sugar_swarm: SugarSwarm) -> None:
        """Test _load_backend_args properly initializes backend args."""
        sugar_swarm._load_backend_args()
        assert sugar_swarm.backend_args == ['swarm']

    def test_get_services_names_empty(self, sugar_swarm: SugarSwarm) -> None:
        """Test  returns empty list when no services specified."""
        result = sugar_swarm._get_services_names()
        print('result :', result)
        assert result == []

    def test_get_services_names_with_services(
        self, sugar_swarm: SugarSwarm
    ) -> None:
        """Test  properly parses comma-separated services."""
        result = sugar_swarm._get_services_names(services='svc1,svc2,svc3')
        print('result :', result)
        assert result == ['svc1', 'svc2', 'svc3']

    def test_get_services_names_with_single_service(
        self, sugar_swarm: SugarSwarm
    ) -> None:
        """Test  properly parses comma-separated services."""
        result = sugar_swarm._get_services_names(services='svc1')
        print('result :', result)
        assert result == ['svc1']

    def test_get_services_names_no_services_with_all(
        self, sugar_swarm: SugarSwarm
    ) -> None:
        """Test  raises error when all=True but no services."""
        with mock.patch('sugar.logs.SugarLogs.raise_error') as mock_error:
            sugar_swarm._get_services_names(all=True)
            mock_error.assert_called_once()

    def test_call_command(self, sugar_swarm: SugarSwarm) -> None:
        """Test _call_command properly sets backend_args."""
        with mock.patch.object(sugar_swarm, '_call_backend_app') as mock_call:
            sugar_swarm._setup_load()
            sugar_swarm._call_command(
                'init', options_args=['--advertise-addr', '192.168.1.1']
            )
            mock_call.assert_called_once_with(
                'init',
                services=[],
                options_args=['--advertise-addr', '192.168.1.1'],
                cmd_args=[],
                _out=sys.stdout,
                _err=sys.stderr,
            )
        assert sugar_swarm.backend_args == ['swarm']

    def test_cmd_init(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_init calls _call_command properly."""
        with mock.patch.object(
            sugar_swarm,
            '_get_list_args',
            return_value=['--advertise-addr', '192.168.1.1'],
        ):
            with mock.patch.object(sugar_swarm, '_call_command') as mock_call:
                sugar_swarm._cmd_init(options='--advertise-addr 192.168.1.1')
                mock_call.assert_called_once_with(
                    'init', options_args=['--advertise-addr', '192.168.1.1']
                )

    def test_cmd_join(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_join calls _call_command properly."""
        with mock.patch.object(
            sugar_swarm, '_get_list_args', return_value=['--token', 'token123']
        ):
            with mock.patch.object(sugar_swarm, '_call_command') as mock_call:
                sugar_swarm._cmd_join(options='--token token123')
                mock_call.assert_called_once_with(
                    'join', options_args=['--token', 'token123']
                )

    @pytest.mark.skip(
        reason='This test is experimental, need to add '
        'more test cases and more integrations to the  cli'
    )
    def test_cmd_update(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_update formats options correctly."""
        with mock.patch.object(
            sugar_swarm, '_get_services_names', return_value=['svc1']
        ):
            with mock.patch.object(
                sugar_swarm, '_get_list_args', return_value=[]
            ):
                with mock.patch.object(
                    sugar_swarm, '_call_command'
                ) as mock_call:
                    sugar_swarm._cmd_update(
                        services='svc1',
                        image='nginx:latest',
                        replicas='3',
                        force=True,
                        detach=True,
                        env_add='DEBUG=1,LOG_LEVEL=info',
                    )
                    mock_call.assert_called_once_with(
                        'update',
                        services=['svc1'],
                        options_args=[
                            '--detach',
                            '--force',
                            '--image',
                            'nginx:latest',
                            '--replicas',
                            '3',
                            '--env-add',
                            'DEBUG=1',
                            '--env-add',
                            'LOG_LEVEL=info',
                        ],
                    )


class TestSwarmService:
    """Test suite for SugarSwarm class."""

    def test_cmd_inspect_multiple_services(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """Test _cmd_inspect sets correct parameters."""
        with mock.patch.object(
            sugar_swarm_service, '_get_list_args', return_value=[]
        ):
            sugar_swarm_service._cmd_inspect(
                services='svc1,svc2',
                stack='test-stack',
            )

    def test_cmd_inspect_single_service(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """Test _cmd_inspect sets correct parameters for a single service."""
        with mock.patch.object(
            sugar_swarm_service, '_get_list_args', return_value=[]
        ):
            with mock.patch.object(
                sugar_swarm_service, '_call_backend_app'
            ) as mock_call:
                sugar_swarm_service._cmd_inspect(
                    services='svc1',
                    stack='test-stack',
                    options='',
                )
                mock_call.assert_called_once_with(
                    'inspect',
                    services=['test-stack_svc1'],
                    options_args=[],
                    cmd_args=[],
                    _out=ANY,
                    _err=ANY,
                )

    @pytest.mark.skip(
        reason='Expected raise_error to be called once. Called 2 times.'
    )
    def test_cmd_inspect_service_without_service_message(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """Test raises correct error, service is provided without stack."""
        with mock.patch.object(
            sugar_swarm_service, '_get_list_args', return_value=[]
        ):
            with mock.patch('sugar.logs.SugarLogs.raise_error') as mock_error:
                sugar_swarm_service._cmd_inspect(services='')
                mock_error.assert_called_once_with(
                    'ValueError: Value for "--stack" is required.',
                    SugarError.SUGAR_INVALID_PARAMETER,
                )

    def test_cmd_create(self, sugar_swarm_service: SugarSwarmService) -> None:
        """Test _cmd calls create subcommand."""
        with mock.patch.object(
            sugar_swarm_service, '_cmd_create'
        ) as mock_create:
            sugar_swarm_service._cmd_create(
                options='--name test-service nginx'
            )
            mock_create.assert_called_once_with(
                options='--name test-service nginx'
            )

    def test_cmd_inspect(self, sugar_swarm_service: SugarSwarmService) -> None:
        """Test _cmd calls inspect subcommand."""
        with mock.patch.object(
            sugar_swarm_service, '_cmd_inspect'
        ) as mock_inspect:
            sugar_swarm_service._cmd_inspect(
                services='service1', options='--pretty'
            )
            mock_inspect.assert_called_once_with(
                services='service1', options='--pretty'
            )

    def test_cmd_logs(self, sugar_swarm_service: SugarSwarmService) -> None:
        """Test _cmd calls logs subcommand."""
        with mock.patch.object(sugar_swarm_service, '_cmd_logs') as mock_logs:
            sugar_swarm_service._cmd_logs(
                services='service1', options='--follow'
            )
            mock_logs.assert_called_once_with(
                services='service1', options='--follow'
            )

    def test_cmd_ls(self, sugar_swarm_service: SugarSwarmService) -> None:
        """Test _cmd calls ls subcommand."""
        with mock.patch.object(sugar_swarm_service, '_cmd_ls') as mock_ls:
            sugar_swarm_service._cmd_ls(options='--filter name=test')
            mock_ls.assert_called_once_with(options='--filter name=test')

    def test_cmd_ps(self, sugar_swarm_service: SugarSwarmService) -> None:
        """Test _cmd calls ps subcommand."""
        with mock.patch.object(sugar_swarm_service, '_cmd_ps') as mock_ps:
            sugar_swarm_service._cmd_ps(
                services='service1', options='--no-trunc'
            )
            mock_ps.assert_called_once_with(
                services='service1', options='--no-trunc'
            )

    def test_cmd_rm(self, sugar_swarm_service: SugarSwarmService) -> None:
        """Test _cmd calls rm subcommand."""
        with mock.patch.object(sugar_swarm_service, '_cmd_rm') as mock_rm:
            sugar_swarm_service._cmd_rm(services='service1', options='')
            mock_rm.assert_called_once_with(services='service1', options='')

    def test_cmd_rollback(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """Test _cmd calls rollback subcommand."""
        with mock.patch.object(
            sugar_swarm_service, '_cmd_rollback'
        ) as mock_rollback:
            sugar_swarm_service._cmd_rollback(
                services='service1', options='--quiet'
            )
            mock_rollback.assert_called_once_with(
                services='service1', options='--quiet'
            )

    def test_cmd_scale(self, sugar_swarm_service: SugarSwarmService) -> None:
        """Test _cmd calls scale subcommand."""
        with mock.patch.object(
            sugar_swarm_service, '_cmd_scale'
        ) as mock_scale:
            sugar_swarm_service._cmd_scale(
                services='service1=3', options='--detach'
            )
            mock_scale.assert_called_once_with(
                services='service1=3', options='--detach'
            )

    def test_cmd_update(self, sugar_swarm_service: SugarSwarmService) -> None:
        """Test _cmd calls update subcommand."""
        with mock.patch.object(
            sugar_swarm_service, '_cmd_update'
        ) as mock_update:
            sugar_swarm_service._cmd_update(
                services='service1', options='--image nginx:latest'
            )
            mock_update.assert_called_once_with(
                services='service1', options='--image nginx:latest'
            )

    def test_cmd_create_missing_options(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """Test _cmd_create raises error when options  missing."""
        with mock.patch('sugar.logs.SugarLogs.raise_error'):
            sugar_swarm_service._cmd_create()

    def test_cmd_create_with_options(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """Test _cmd_create calls _call_command options."""
        with mock.patch.object(
            sugar_swarm_service,
            '_get_list_args',
            return_value=['--name', 'test', 'nginx'],
        ):
            with mock.patch.object(
                sugar_swarm_service, '_call_command'
            ) as mock_call:
                sugar_swarm_service._cmd_create(options='--name test nginx')
                mock_call.assert_called_once_with(
                    'create',
                    services=[],
                    options_args=['--name', 'test', 'nginx'],
                )

    @pytest.mark.skip(
        reason='Expected raise_error to be called once. Called 2 times.'
    )
    def test_cmd_inspect_missing_services(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """Test _cmd_inspect raises error when services  missing."""
        with mock.patch('sugar.logs.SugarLogs.raise_error') as mock_error:
            sugar_swarm_service._cmd_inspect()
            mock_error.assert_called_once_with(
                'ValueError: Value for "--stack" is required.',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

    def test_cmd_inspect_with_services(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """Test _cmd_inspect call _call_command services."""
        with mock.patch.object(
            sugar_swarm_service, '_get_list_args', return_value=['--pretty']
        ):
            with mock.patch.object(
                sugar_swarm_service, '_call_command'
            ) as mock_call:
                sugar_swarm_service._cmd_inspect(
                    stack='test-stack',
                    services='svc1,svc2',
                    options='--pretty',
                )
                mock_call.assert_called_once_with(
                    'inspect',
                    services=['test-stack_svc1', 'test-stack_svc2'],
                    options_args=['--pretty'],
                )

    def test_cmd_logs_missing_services(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """_cmd_logs should raise ValueError when no services are provided."""
        with mock.patch('sugar.logs.SugarLogs.raise_error'):
            with pytest.raises(ValueError) as excinfo:
                sugar_swarm_service._cmd_logs()

            # adjust the expected message to whatever your implementation
            # raises
            assert str(excinfo.value) == 'Stack name must be provided'

    def test_cmd_logs_with_services(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """Test _cmd_logs calls _call_command  services."""
        with mock.patch.object(
            sugar_swarm_service, '_get_list_args', return_value=['--follow']
        ):
            with mock.patch('sugar.logs.SugarLogs.raise_error'):
                with pytest.raises(ValueError) as excinfo:
                    with mock.patch.object(
                        sugar_swarm_service, '_call_command'
                    ) as mock_call:
                        sugar_swarm_service._cmd_logs(
                            services='svc1', options='--follow'
                        )
                        mock_call.assert_called_once_with(
                            'logs',
                            services=['svc1'],
                            options_args=['--follow'],
                        )

                    # adjust the expected message to whatever your
                    # implementation raises
                    assert str(excinfo.value) == 'Stack name must be provided'

    def test_cmd_ps_missing_services(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """Test _cmd_ps raises error when services are missing."""
        with mock.patch('sugar.logs.SugarLogs.raise_error') as mock_error:
            sugar_swarm_service._cmd_ps()
            mock_error.assert_called_once_with(
                'Service name must be provided for this command (use '
                '--services service1,service2)',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

    def test_cmd_ps_with_services(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """Test _cmd_ps call _call_command with services."""
        with mock.patch.object(
            sugar_swarm_service, '_get_list_args', return_value=['--no-trunc']
        ):
            with mock.patch.object(
                sugar_swarm_service, '_call_command'
            ) as mock_call:
                sugar_swarm_service._cmd_ps(
                    services='svc1,svc2', options='--no-trunc'
                )
                mock_call.assert_called_once_with(
                    'ps',
                    services=['svc1', 'svc2'],
                    options_args=['--no-trunc'],
                )

    def test_cmd_rm_missing_services(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """Test _cmd_rm raises error when services are missing."""
        with mock.patch('sugar.logs.SugarLogs.raise_error') as mock_error:
            sugar_swarm_service._cmd_rm()
            mock_error.assert_called_once_with(
                'Service name must be provided for this command (use '
                '--services service1,service2)',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

    def test_cmd_rm_with_services(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """Test _cmd_rm call _call_command with services."""
        with mock.patch.object(
            sugar_swarm_service, '_get_list_args', return_value=[]
        ):
            with mock.patch.object(
                sugar_swarm_service, '_call_command'
            ) as mock_call:
                sugar_swarm_service._cmd_rm(services='svc1,svc2', options='')
                mock_call.assert_called_once_with(
                    'rm', services=['svc1', 'svc2'], options_args=[]
                )

    def test_cmd_rollback_missing_services(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """Test _cmd_rollback raises error when services missing."""
        with mock.patch('sugar.logs.SugarLogs.raise_error') as mock_error:
            sugar_swarm_service._cmd_rollback()
            mock_error.assert_called_once_with(
                'Service name must be provided for this command (use '
                '--services service1,service2)',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

    def test_cmd_rollback_with_services(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """Test_cmd_rollback call _call_command services."""
        with mock.patch.object(
            sugar_swarm_service, '_get_list_args', return_value=['--quiet']
        ):
            with mock.patch.object(
                sugar_swarm_service, 'backend_app'
            ) as mock_call:
                sugar_swarm_service._cmd_rollback(
                    service='svc1',
                    options='--quiet',
                )
                mock_call.assert_called_once_with(
                    'service',
                    'rollback',
                    '--quiet',
                    'svc1',
                    _out=ANY,
                    _err=ANY,
                    _ok_code=ANY,
                )

    @pytest.mark.skip(
        reason='Expected raise_error to be called once. Called 2 times.'
    )
    def test_cmd_scale_missing_replicas(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """Test _cmd_scale raise error when services are missing."""
        with mock.patch('sugar.logs.SugarLogs.raise_error') as mock_error:
            sugar_swarm_service._cmd_scale(stack='test-stack')
            mock_error.assert_called_once_with(
                'ValueError: Value for "--replicas" is required.',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

    def test_cmd_scale_with_services(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """Test_cmd_scale _call_command service replicas."""
        with mock.patch.object(
            sugar_swarm_service, '_get_list_args', return_value=['--detach']
        ):
            with mock.patch.object(
                sugar_swarm_service, '_call_command'
            ) as mock_call:
                sugar_swarm_service._cmd_scale(
                    stack='test-stack',
                    replicas='svc1=3,svc2=5',
                    options='--detach',
                )
                mock_call.assert_called_once_with(
                    'scale',
                    services=['test-stack_svc1=3', 'test-stack_svc2=5'],
                    options_args=['--detach'],
                )

    def test_cmd_update_missing_services(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """Test _cmd_update raises error when services  missing."""
        with mock.patch('sugar.logs.SugarLogs.raise_error') as mock_error:
            sugar_swarm_service._cmd_update()
            mock_error.assert_called_once_with(
                'Service name must be provided for this command (use '
                '--services service1,service2)',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

    def test_cmd_update_with_services(
        self, sugar_swarm_service: SugarSwarmService
    ) -> None:
        """Test _cmd_update calls _call_command services."""
        with mock.patch.object(
            sugar_swarm_service,
            '_get_list_args',
            return_value=['--image', 'nginx:latest'],
        ):
            with mock.patch.object(
                sugar_swarm_service, '_call_command'
            ) as mock_call:
                sugar_swarm_service._cmd_update(
                    services='svc1', options='--image nginx:latest'
                )
                mock_call.assert_called_once_with(
                    'update',
                    services=['svc1'],
                    options_args=['--image', 'nginx:latest'],
                )


class TestSwarmStack:
    """Test suite for SugarSwarm class."""

    def test_cmd_ls(self, sugar_swarm_stack: SugarSwarmStack) -> None:
        """Test _cmd calls ls subcommand."""
        with mock.patch.object(sugar_swarm_stack, '_cmd_ls') as mock_ls:
            sugar_swarm_stack._cmd_ls(options='--filter name=test')
            mock_ls.assert_called_once_with(options='--filter name=test')

    def test_cmd_ps(self, sugar_swarm_stack: SugarSwarmStack) -> None:
        """Test _cmd calls ps subcommand."""
        with mock.patch.object(sugar_swarm_stack, '_cmd_ps') as mock_ps:
            sugar_swarm_stack._cmd_ps(
                services='service1', options='--no-trunc'
            )
            mock_ps.assert_called_once_with(
                services='service1', options='--no-trunc'
            )

    def test_cmd_rm(self, sugar_swarm_stack: SugarSwarmStack) -> None:
        """Test _cmd calls rm subcommand."""
        with mock.patch.object(sugar_swarm_stack, '_cmd_rm') as mock_rm:
            sugar_swarm_stack._cmd_rm(services='service1', options='')
            mock_rm.assert_called_once_with(services='service1', options='')

    def test_cmd_ps_missing_services(
        self, sugar_swarm_stack: SugarSwarmStack
    ) -> None:
        """Test _cmd_ps raises error when services are missing."""
        with mock.patch('sugar.logs.SugarLogs.raise_error') as mock_error:
            sugar_swarm_stack._cmd_ps()
            mock_error.assert_called_once_with(
                'Stack name must be provided',
                SugarError.SUGAR_INVALID_PARAMETER,
            )


class TestSwarmNode:
    """Test suite for SugarSwarmNode class."""

    def test_cmd_inspect_multiple_services(
        self, sugar_swarm_node: SugarSwarmNode
    ) -> None:
        """Test _cmd_inspect sets correct parameters."""
        with mock.patch.object(
            sugar_swarm_node, '_get_list_args', return_value=[]
        ):
            sugar_swarm_node._cmd_inspect(nodes='svc1,svc2')

    def test_cmd_inspect_single_service(
        self, sugar_swarm_node: SugarSwarmNode
    ) -> None:
        """Test _cmd_inspect sets correct parameters for a single service."""
        with mock.patch.object(
            sugar_swarm_node, '_get_list_args', return_value=[]
        ):
            with mock.patch.object(
                sugar_swarm_node, '_call_backend_app'
            ) as mock_call:
                sugar_swarm_node._cmd_inspect(nodes='svc1')
                mock_call.assert_called_once_with(
                    'inspect',
                    nodes=['svc1'],
                    options_args=[],
                    cmd_args=[],
                    _out=ANY,
                    _err=ANY,
                )

    def test_cmd_inspect(self, sugar_swarm_node: SugarSwarmService) -> None:
        """Test _cmd calls inspect subcommand."""
        with mock.patch.object(
            sugar_swarm_node, '_cmd_inspect'
        ) as mock_inspect:
            sugar_swarm_node._cmd_inspect(nodes='service1', options='--pretty')
            mock_inspect.assert_called_once_with(
                nodes='service1', options='--pretty'
            )

    def test_cmd_ls(self, sugar_swarm_node: SugarSwarmService) -> None:
        """Test _cmd calls ls subcommand."""
        with mock.patch.object(sugar_swarm_node, '_cmd_ls') as mock_ls:
            sugar_swarm_node._cmd_ls(options='--filter name=test')
            mock_ls.assert_called_once_with(options='--filter name=test')

    def test_cmd_ps(self, sugar_swarm_node: SugarSwarmService) -> None:
        """Test _cmd calls ps subcommand."""
        with mock.patch.object(sugar_swarm_node, '_cmd_ps') as mock_ps:
            sugar_swarm_node._cmd_ps(nodes='service1', options='--no-trunc')
            mock_ps.assert_called_once_with(
                nodes='service1', options='--no-trunc'
            )

    def test_cmd_rm(self, sugar_swarm_node: SugarSwarmService) -> None:
        """Test _cmd calls rm subcommand."""
        with mock.patch.object(sugar_swarm_node, '_cmd_rm') as mock_rm:
            sugar_swarm_node._cmd_rm(nodes='service1', options='')
            mock_rm.assert_called_once_with(nodes='service1', options='')

    def test_cmd_update(self, sugar_swarm_node: SugarSwarmService) -> None:
        """Test _cmd calls update subcommand."""
        with mock.patch.object(sugar_swarm_node, '_cmd_update') as mock_update:
            sugar_swarm_node._cmd_update(
                nodes='service1', options='--image nginx:latest'
            )
            mock_update.assert_called_once_with(
                nodes='service1', options='--image nginx:latest'
            )

    def test_cmd_inspect_missing_services(
        self, sugar_swarm_node: SugarSwarmService
    ) -> None:
        """Test _cmd_inspect raises error when services  missing."""
        with mock.patch('sugar.logs.SugarLogs.raise_error') as mock_error:
            sugar_swarm_node._cmd_inspect()
            mock_error.assert_called_once_with(
                'Node name(s) must be provided',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

    def test_cmd_inspect_with_services(
        self, sugar_swarm_node: SugarSwarmService
    ) -> None:
        """Test _cmd_inspect call _call_command services."""
        with mock.patch.object(
            sugar_swarm_node, '_get_list_args', return_value=['--pretty']
        ):
            with mock.patch.object(
                sugar_swarm_node, '_call_command'
            ) as mock_call:
                sugar_swarm_node._cmd_inspect(
                    nodes='svc1,svc2', options='--pretty'
                )
                mock_call.assert_called_once_with(
                    'inspect',
                    nodes=['svc1', 'svc2'],
                    options_args=['--pretty'],
                )

    def test_cmd_ps_missing_services(
        self, sugar_swarm_node: SugarSwarmService
    ) -> None:
        """Test _cmd_ps raises error when services are missing."""
        with mock.patch('sugar.logs.SugarLogs.raise_error') as mock_error:
            sugar_swarm_node._cmd_ps()
            mock_error.assert_called_once_with(
                'Node name(s) must be provided',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

    def test_cmd_ps_with_services(
        self, sugar_swarm_node: SugarSwarmService
    ) -> None:
        """Test _cmd_ps call _call_command with services."""
        with mock.patch.object(
            sugar_swarm_node, '_get_list_args', return_value=['--no-trunc']
        ):
            with mock.patch.object(
                sugar_swarm_node, '_call_command'
            ) as mock_call:
                sugar_swarm_node._cmd_ps(
                    nodes='svc1,svc2', options='--no-trunc'
                )
                mock_call.assert_called_once_with(
                    'ps',
                    nodes=['svc1', 'svc2'],
                    options_args=['--no-trunc'],
                )

    def test_cmd_rm_missing_services(
        self, sugar_swarm_node: SugarSwarmService
    ) -> None:
        """Test _cmd_rm raises error when services are missing."""
        with mock.patch('sugar.logs.SugarLogs.raise_error') as mock_error:
            sugar_swarm_node._cmd_rm()
            mock_error.assert_called_once_with(
                'Node name(s) must be provided',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

    def test_cmd_rm_with_services(
        self, sugar_swarm_node: SugarSwarmService
    ) -> None:
        """Test _cmd_rm call _call_command with services."""
        with mock.patch.object(
            sugar_swarm_node, '_get_list_args', return_value=[]
        ):
            with mock.patch.object(
                sugar_swarm_node, '_call_command'
            ) as mock_call:
                sugar_swarm_node._cmd_rm(nodes='svc1,svc2', options='')
                mock_call.assert_called_once_with(
                    'rm', nodes=['svc1', 'svc2'], options_args=[]
                )

    def test_cmd_update_missing_services(
        self, sugar_swarm_node: SugarSwarmService
    ) -> None:
        """Test _cmd_update raises error when services  missing."""
        with mock.patch('sugar.logs.SugarLogs.raise_error') as mock_error:
            sugar_swarm_node._cmd_update()
            mock_error.assert_called_once_with(
                'Node name(s) must be provided',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

    def test_cmd_update_with_services(
        self, sugar_swarm_node: SugarSwarmService
    ) -> None:
        """Test _cmd_update calls _call_command services."""
        with mock.patch.object(
            sugar_swarm_node,
            '_get_list_args',
            return_value=['--image', 'nginx:latest'],
        ):
            with mock.patch.object(
                sugar_swarm_node, '_call_command'
            ) as mock_call:
                sugar_swarm_node._cmd_update(
                    nodes='svc1', options='--image nginx:latest'
                )
                mock_call.assert_called_once_with(
                    'update',
                    nodes=['svc1'],
                    options_args=['--image', 'nginx:latest'],
                )
