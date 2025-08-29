"""Sugar plugin for podman compose."""

from __future__ import annotations

import io
import os
import sys

from pathlib import Path
from typing import Any, Union

import dotenv
import sh
import yaml

from sugar.docs import docparams
from sugar.extensions.base import SugarBase
from sugar.logs import SugarError, SugarLogs
from sugar.utils import (
    camel_to_snake,
    get_absolute_path,
)

doc_profile = {
    'profile': 'Specify the profile name of the services you want to use.'
}
doc_service = {'service': 'Set the service for the container call.'}
doc_services = {
    'services': 'Set the services separated by comma for the container call.'
}
doc_all_services = {'all': 'Use all services for the command.'}
doc_options = {
    'options': ('Specify the options for the backend command. E.g.: `--  -d`.')
}
doc_cmd = {
    'cmd': (
        'Specify the COMMAND for some podman-compose command. '
        'E.g.: --cmd python -c print(1).'
    )
}

doc_common_no_services = {
    **doc_profile,
    **doc_options,
}

doc_common_service = {
    **doc_profile,
    **doc_service,
    **doc_options,
}

doc_common_service_cmd = {
    **doc_profile,
    **doc_service,
    **doc_options,
    **doc_cmd,
}

doc_common_services = {
    **doc_profile,
    **doc_services,
    **doc_all_services,
    **doc_options,
}

doc_common_services_no_options = {
    **doc_profile,
    **doc_services,
    **doc_all_services,
}


class SugarPodmanComposeExt(SugarBase):
    """(Experimental)SugarPodmanCompose provide the podman compose commands."""

    def _load_backend(self) -> None:
        """
        Initialize the backend application and its arguments.

        This method checks if the backend is supported, sets the backend app,
        and loads backend arguments.
        """
        backend_cmd = self.config.get('backend', '')
        supported_backends = ['podman', 'compose']

        if backend_cmd not in supported_backends:
            SugarLogs.raise_error(
                f'"{self.config["backend"]}" not supported yet.'
                f' Supported backends are: {", ".join(supported_backends)}.',
                SugarError.SUGAR_COMPOSE_APP_NOT_SUPPORTED,
            )

        self.backend_app = sh.Command('podman-compose')
        self._load_podman_compose_args()

    def _load_podman_compose_args(self) -> None:
        """Load arguments specific to podman-compose."""
        self._filter_service_profile()

        config_path = []

        if type(self.service_profile['config-path']) is list:
            backend_path_arg = [
                get_absolute_path(path)
                for path in self.service_profile.get('config-path', [])
            ]
        else:
            backend_path_arg = [
                get_absolute_path(self.service_profile['config-path'])
            ]

        if isinstance(backend_path_arg, str):
            # Convert relative path to absolute using project root
            if not backend_path_arg.startswith('/'):
                backend_path_arg = str(
                    Path(self.file).parent / backend_path_arg
                )
            config_path.append(backend_path_arg)
        elif isinstance(backend_path_arg, list):
            config_path.extend(backend_path_arg)
        else:
            SugarLogs.raise_error(
                'The attribute config-path` just supports the data '
                f'types `string` or `list`, {type(backend_path_arg)} '
                'received.',
                SugarError.SUGAR_INVALID_CONFIGURATION,
            )
        # Use -f instead of --file for podman compose
        for p in config_path:
            self.backend_args.extend(['-f', p])

        if self.service_profile.get('project-name'):
            self.backend_args.extend(
                ['-p', self.service_profile['project-name']]
            )

    def _call_backend_app(
        self,
        action: str,
        services: list[str] = [],
        nodes: list[str] = [],
        options_args: list[str] = [],
        cmd_args: list[str] = [],
        _out: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stdout,
        _err: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stderr,
    ) -> None:
        """
        Override _call_backend_app to handle environment variables.

        from .env file.
        instead of using the --env-file flag that's
        not supported by podman compose.
        """
        # validation
        if nodes:
            SugarLogs.raise_error(
                'The argument `nodes` is not supported yet '
                'by the podman plugin.',
                SugarError.SUGAR_INVALID_PARAMETER,
            )
        # Execute pre-run hooks
        extension = camel_to_snake(
            self.__class__.__name__.replace('Sugar', '')
        )
        self._execute_hooks('pre-run', extension, action)

        # Load env vars from env-file if specified
        env_vars = os.environ.copy()
        env_file = self.service_profile.get('env-file')
        if env_file:
            if not env_file.startswith('/'):
                env_file = str(Path(self.file).parent / env_file)

            if Path(env_file).exists():
                try:
                    dotenv_values = {
                        k: str(v)
                        for k, v in dotenv.dotenv_values(env_file).items()
                        if v is not None
                    }
                    env_vars.update(dotenv_values)
                    if self.verbose:
                        SugarLogs.print_info(
                            f'Loaded environment variables from {env_file}'
                        )
                except ImportError:
                    SugarLogs.print_warning(
                        """python-dotenv package not found.
                        Env file variables will not be loaded."""
                    )
                except Exception as e:
                    SugarLogs.print_warning(
                        f'Failed to load env file {env_file}: {e!s}'
                    )

        sh_extras = {
            '_in': sys.stdin,
            '_out': _out,
            '_err': _err,
            '_no_err': True,
            '_env': env_vars,
            '_bg': True,
            '_bg_exc': False,
        }

        positional_parameters = [
            *self.backend_args,
            *[action],
            *options_args,
            *services,
            *cmd_args,
        ]

        if self.verbose or self.dry_run:
            SugarLogs.print_info(
                f'>>> {self.backend_app} {" ".join(positional_parameters)}'
            )
            SugarLogs.print_info('-' * 80)

        if self.dry_run:
            SugarLogs.print_warning(
                'Running it in dry-run mode, the command was skipped.'
            )
            return

        p = self.backend_app(
            *positional_parameters,
            **sh_extras,
        )

        try:
            p.wait()
        except sh.ErrorReturnCode as e:
            SugarLogs.raise_error(str(e), SugarError.SH_ERROR_RETURN_CODE)
        except KeyboardInterrupt:
            pid = p.pid
            p.kill()
            SugarLogs.raise_error(
                f'Process {pid} killed.', SugarError.SH_KEYBOARD_INTERRUPT
            )

        self._execute_hooks('post-run', extension, action)

    def podman_check_services(
        self,
        all: bool,
        services: str,
    ) -> list[str]:
        """Check if difference between default and available podman services.

        Check if difference between default and available
        podman services in .sugar.yml file.
        """
        if all:
            default = self._get_services_names(services=services, all=True)
            available = self._get_services_names(services=services, all=False)
            diffence = set(default) - set(available)
            return list(diffence)
        else:
            default = self._get_services_names(services=services, all=False)
            return default

    def _get_image_filters(self, services_names: list[str]) -> list[str]:
        """Get image filters for the given services."""
        filters = []
        config_paths = self.service_profile.get('config-path', [])
        if isinstance(config_paths, str):
            config_paths = [config_paths]

        for config_path in config_paths:
            path_to_use = config_path
            if not config_path.startswith('/'):
                path_to_use = str(Path(self.file).parent / config_path)
            try:
                with open(path_to_use) as f:
                    compose_config = yaml.safe_load(f)
                    for service in services_names:
                        if service in compose_config.get('services', {}):
                            service_config = compose_config['services'][
                                service
                            ]
                            if 'image' in service_config:
                                filters.extend(
                                    [
                                        '--filter',
                                        f'reference={service_config["image"]}',
                                    ]
                                )
            except (yaml.YAMLError, FileNotFoundError) as e:
                SugarLogs.print_warning(
                    f'Error with compose file {path_to_use}: {e}'
                )
        return filters

    @docparams(doc_common_service)
    def _cmd_attach(
        self,
        service: str = '',
        options: str = '',
    ) -> None:
        """
        Attach to a service's container.

        Attach local standard input, output, and error streams to a
        running container.
        """
        if not service:
            SugarLogs.raise_error(
                'The service parameter is required.',
                SugarError.SUGAR_MISSING_PARAMETER,
            )

        # Use podman command directly instead of podman-compose
        podman_cmd = sh.Command('podman')
        options_args = self._get_list_args(options)

        # Get the container name based on the service name
        # This assumes container name follows podman-compose naming convention
        project_name = self.service_profile.get('project-name', 'sugar')
        container_name = f'{project_name}_{service}_1'

        # Build command arguments
        positional_parameters = ['attach', *options_args, container_name]

        if self.verbose or self.dry_run:
            SugarLogs.print_info(
                f'>>> podman {" ".join(positional_parameters)}'
            )
            SugarLogs.print_info('-' * 80)

        if self.dry_run:
            SugarLogs.print_warning(
                'Running it in dry-run mode, the command was skipped.'
            )
            return

        try:
            podman_cmd(
                *positional_parameters,
                _fg=True,  # Run in foreground to allow direct interaction
            )
        except sh.ErrorReturnCode as e:
            SugarLogs.raise_error(str(e), SugarError.SH_ERROR_RETURN_CODE)
        except KeyboardInterrupt:
            SugarLogs.raise_error(
                'Detached from container.', SugarError.SH_KEYBOARD_INTERRUPT
            )

    @docparams(doc_common_services)
    def _cmd_build(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Build or rebuild services."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'build', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_config(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Parse, resolve and render compose file in canonical format."""
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'config',
            services=[],
            options_args=options_args,
        )

    @docparams(doc_common_no_services)
    def _cmd_cp(
        self,
        options: str = '',
    ) -> None:
        """
        Copy files/folders between a container and the local filesystem.

        Use SRC_PATH and DEST_PATH format where one of them should be a
        container name.
        Example: container_name:/path/to/file /local/path
        """
        # Use podman command directly instead of podman-compose
        podman_cmd = sh.Command('podman')
        options_args = self._get_list_args(options)

        # Build command arguments
        positional_parameters = [
            'cp',
            *options_args,
        ]

        if self.verbose or self.dry_run:
            SugarLogs.print_info(
                f'>>> podman {" ".join(positional_parameters)}'
            )
            SugarLogs.print_info('-' * 80)

        if self.dry_run:
            SugarLogs.print_warning(
                'Running it in dry-run mode, the command was skipped.'
            )
            return

        try:
            podman_cmd(
                *positional_parameters,
                _fg=True,  # Run in foreground to allow direct interaction
            )
        except sh.ErrorReturnCode as e:
            SugarLogs.raise_error(str(e), SugarError.SH_ERROR_RETURN_CODE)
        except KeyboardInterrupt:
            SugarLogs.raise_error(
                'Copy operation interrupted.', SugarError.SH_KEYBOARD_INTERRUPT
            )

    @docparams(doc_common_services)
    def _cmd_create(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Create services."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'run', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_down(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Stop and remove containers, networks."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'down', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_events(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """
        Monitor podman events.

        Shows events from containers matching the specified services.
        Use --filter to filter output (e.g. --  --filter event=create).
        """
        if not services and not all:
            SugarLogs.raise_error(
                'Either service names or --all flag is required.',
                SugarError.SUGAR_MISSING_PARAMETER,
            )

        # Use podman command directly instead of podman-compose
        podman_cmd = sh.Command('podman')
        options_args = self._get_list_args(options)
        services_names = self._get_services_names(services=services, all=all)

        # Get project name for container name prefixing
        project_name = self.service_profile.get('project-name', 'sugar')

        # Build container filters for each service
        filters = []
        for service in services_names:
            container_name = f'{project_name}_{service}_1'
            filters.extend(['--filter', f'container={container_name}'])

        # Build command arguments
        positional_parameters = [
            'events',
            *filters,
            *options_args,
        ]

        if self.verbose or self.dry_run:
            SugarLogs.print_info(
                f'>>> podman {" ".join(positional_parameters)}'
            )
            SugarLogs.print_info('-' * 80)

        if self.dry_run:
            SugarLogs.print_warning(
                'Running it in dry-run mode, the command was skipped.'
            )
            return

        try:
            podman_cmd(
                *positional_parameters,
                _fg=True,  # Run in foreground for live event stream
            )
        except sh.ErrorReturnCode as e:
            SugarLogs.raise_error(str(e), SugarError.SH_ERROR_RETURN_CODE)
        except KeyboardInterrupt:
            SugarLogs.raise_error(
                'Events monitoring interrupted.',
                SugarError.SH_KEYBOARD_INTERRUPT,
            )

    @docparams(doc_common_service_cmd)
    def _cmd_exec(
        self,
        service: str = '',
        cmd: str = '',
        options: str = '',
    ) -> None:
        """Execute a command in a running container."""
        if not service:
            SugarLogs.raise_error(
                'The service parameter is required.',
                SugarError.SUGAR_MISSING_PARAMETER,
            )

        options_args = self._get_list_args(options)
        cmd_args = self._get_list_args(cmd)
        self._call_backend_app(
            'exec',
            services=[service],
            options_args=options_args,
            cmd_args=cmd_args,
        )

    @docparams(doc_common_services)
    def _cmd_images(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """List images used by the created containers."""
        if not services and not all:
            SugarLogs.raise_error(
                'Either service names or --all flag is required.',
                SugarError.SUGAR_MISSING_PARAMETER,
            )

        podman_cmd = sh.Command('podman')
        options_args = self._get_list_args(options)
        services_names = self._get_services_names(services=services, all=all)
        filters = self._get_image_filters(services_names)

        positional_parameters = ['images', *filters, *options_args]

        if self.verbose or self.dry_run:
            SugarLogs.print_info(
                f'>>> podman {" ".join(positional_parameters)}'
            )
            SugarLogs.print_info('-' * 80)

        if self.dry_run:
            SugarLogs.print_warning(
                'Running it in dry-run mode, the command was skipped.'
            )
            return

        try:
            podman_cmd(*positional_parameters, _fg=True)
        except sh.ErrorReturnCode as e:
            SugarLogs.raise_error(str(e), SugarError.SH_ERROR_RETURN_CODE)
        except KeyboardInterrupt:
            SugarLogs.raise_error(
                'Image listing interrupted.', SugarError.SH_KEYBOARD_INTERRUPT
            )

    @docparams(doc_common_services)
    def _cmd_kill(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Kill containers."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'kill', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_logs(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """View output from containers."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'logs', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_pause(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Pause services."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'pause', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_port(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Print the public port for a port binding."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'port', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_ps(
        self,
        options: str = '',
    ) -> None:
        """List containers."""
        # Podman-compose ps doesn't support filtering by services
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'ps',
            services=[],
            options_args=options_args,
        )

    @docparams(doc_common_services)
    def _cmd_pull(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Pull service images."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'pull', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_push(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Push service images."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'push', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_restart(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Restart services."""
        if '-d' in options.split(' '):
            SugarLogs.raise_error(
                'The -d option is not supported for the restart command.',
                SugarError.SUGAR_INVALID_PARAMETER,
            )
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'restart', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_rm(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Remove stopped containers."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args('-v ' + options)
        self._call_backend_app(
            'down', services=services_names, options_args=options_args
        )

    @docparams(doc_common_service_cmd)
    def _cmd_run(
        self,
        service: str = '',
        cmd: str = '',
        options: str = '',
    ) -> None:
        """Run a one-off command on a service."""
        if not service:
            SugarLogs.raise_error(
                'The service parameter is required.',
                SugarError.SUGAR_MISSING_PARAMETER,
            )

        options_args = self._get_list_args(options)
        cmd_args = self._get_list_args(cmd)

        self._call_backend_app(
            'run',
            services=[service],
            options_args=options_args,
            cmd_args=cmd_args,
        )

    @docparams(doc_common_services)
    def _cmd_start(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Start services."""
        options_args = self._get_list_args(options)
        diff_service = self.podman_check_services(services=services, all=all)
        if diff_service != []:
            SugarLogs.print_info(
                'Running un initated service ' + ','.join(diff_service)
            )

            self._call_backend_app(
                'up', services=diff_service, options_args=options_args
            )
        services_names = self._get_services_names(services=services, all=all)
        print(services_names)
        self._call_backend_app(
            'up', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_stop(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Stop services."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'stop', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_stats(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Display a live stream of container(s) resource usage statistics."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'stats', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_unpause(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Unpause services."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'unpause', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_up(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Create and start containers."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'up', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_version(
        self,
        options: str = '',
    ) -> None:
        """Show the podman-compose version information."""
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'version', services=[], options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_wait(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """
        Block until the first service container stops.

        Note: This is an experimental feature.
        """
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'wait', services=services_names, options_args=options_args
        )
