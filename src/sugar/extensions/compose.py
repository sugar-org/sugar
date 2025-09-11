"""Sugar plugin for docker compose."""

from __future__ import annotations

import sh

from sugar.docs import docparams
from sugar.extensions.base import SugarBase
from sugar.logs import SugarError, SugarLogs

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
        'Specify the COMMAND for some docker-compose command. '
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


class SugarComposeBase(SugarBase):
    """SugarComposeBase provides common functionalities."""

    def _get_config_files_path(self) -> list[str]:
        config_path: list[str] = []

        backend_path_arg = self.service_profile['config-path']
        if isinstance(backend_path_arg, str):
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

        return config_path

    def _load_backend(self) -> None:
        backend_cmd = self.config.get('backend', '')
        supported_backends = ['compose']

        if backend_cmd not in supported_backends:
            SugarLogs.raise_error(
                f'"{self.config["backend"]}" not supported yet.'
                f' Supported backends are: {", ".join(supported_backends)}.',
                SugarError.SUGAR_COMPOSE_APP_NOT_SUPPORTED,
            )

        self.backend_app = sh.docker
        self.backend_args.append(backend_cmd)

        self._load_compose_args()

    def _load_compose_args(self) -> None:
        self._filter_service_profile()

        _env_files = self.service_profile.get('env-file')

        env_files: list[str] = []
        if isinstance(_env_files, str):
            env_files = [_env_files]
        elif isinstance(_env_files, list):
            if any(not isinstance(f, str) for f in _env_files):
                SugarLogs.raise_error(
                    'The attribute `env-file` must be a list of strings.',
                    SugarError.SUGAR_INVALID_CONFIGURATION,
                )
            env_files = _env_files

        for env_file in env_files:
            self.backend_args.extend(['--env-file', env_file])

        config_path = self._get_config_files_path()

        for p in config_path:
            self.backend_args.extend(['--file', p])

        if self.service_profile.get('project-name'):
            self.backend_args.extend(
                ['--project-name', self.service_profile['project-name']]
            )


class SugarCompose(SugarComposeBase):
    """SugarCompose provides the docker compose commands."""

    @docparams(doc_common_service)
    def _cmd_attach(
        self,
        service: str = '',
        /,
        options: str = '',
    ) -> None:
        """
        Attach to a service's running container.

        Attach local standard input, output, and error streams to a service's
        running container.

        Note: This is an experimental feature.
        """
        services_names = self._get_service_name(service)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'attach', services=services_names, options_args=options_args
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
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'config', services=services_names, options_args=options_args
        )

    @docparams(doc_common_no_services)
    def _cmd_cp(
        self,
        options: str = '',
    ) -> None:
        """
        Copy files/folders between a services and local filesystem.

        Note: This is an experimental feature.
        """
        options_args = self._get_list_args(options)
        self._call_backend_app('cp', services=[], options_args=options_args)

    @docparams(doc_common_services)
    def _cmd_create(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Create containers for a service."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'create', services=services_names, options_args=options_args
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
        options_args = [*self._get_list_args(options), *['--remove-orphans']]

        self._call_backend_app(
            'down',
            services=services_names,
            options_args=options_args,
        )

    @docparams(doc_common_services)
    def _cmd_events(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Receive real time events from containers."""
        # port is not complete supported
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'events', services=services_names, options_args=options_args
        )

    @docparams({**doc_common_service, **doc_cmd})
    def _cmd_exec(
        self,
        service: str,
        options: str = '',
        cmd: str = '',
    ) -> None:
        """Execute a command in a running container."""
        services_names = self._get_service_name(service)
        options_args = self._get_list_args(options)
        cmd_args = self._get_list_args(cmd)
        self._call_backend_app(
            'exec',
            services=services_names,
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
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'images', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_kill(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Force stop service containers."""
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

    @docparams(doc_common_no_services)
    def _cmd_ls(
        self,
        options: str = '',
    ) -> None:
        """
        List running compose projects.

        Note: This is an experimental feature.
        """
        options_args = self._get_list_args(options)
        self._call_backend_app('ls', services=[], options_args=options_args)

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

    @docparams(doc_common_no_services)
    def _cmd_port(
        self,
        service: str,
        options: str = '',
    ) -> None:
        """Print the public port for a port binding."""
        # port is not complete supported
        services_names = self._get_service_name(service)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'port', services=services_names, options_args=options_args
        )

    @docparams(doc_common_services)
    def _cmd_ps(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """List containers."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'ps', services=services_names, options_args=options_args
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
        """Restart service containers."""
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
        """
        Remove stopped service containers.

        By default, anonymous volumes attached to containers will not be
        removed. You can override this with -v. To list all volumes, use
        "docker volume ls".

        Any data which is not in a volume will be lost.
        """
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'rm', services=services_names, options_args=options_args
        )

    @docparams({**doc_common_service, **doc_cmd})
    def _cmd_run(
        self,
        service: str,
        options: str = '',
        cmd: str = '',
    ) -> None:
        """Run a one-off command on a service."""
        if not service:
            SugarLogs.raise_error(
                '`run` sub-command expected --service parameter.',
                SugarError.SUGAR_MISSING_PARAMETER,
            )
        services_names = self._get_service_name(service)
        options_args = self._get_list_args(options)
        cmd_args = self._get_list_args(cmd)
        self._call_backend_app(
            'run',
            services=services_names,
            options_args=options_args,
            cmd_args=cmd_args,
        )

    @docparams(doc_common_service)
    def _cmd_scale(
        self,
        service: str = '',
        options: str = '',
    ) -> None:
        """
        Scale services.

        Note: This is an experimental feature.
        """
        options_args = self._get_list_args(options)
        self._call_backend_app('scale', services=[], options_args=options_args)

    @docparams(doc_common_services)
    def _cmd_start(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Start services."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'start', services=services_names, options_args=options_args
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
    def _cmd_top(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Display the running processes."""
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'top', services=services_names, options_args=options_args
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

    @docparams(doc_common_services)
    def _cmd_watch(
        self,
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """
        Watch build context.

        Watch build context for service and rebuild/refresh containers when
        files are updated.

        Note: This is an experimental feature.
        """
        services_names = self._get_services_names(services=services, all=all)
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'watch', services=services_names, options_args=options_args
        )

    @docparams(doc_options)
    def _cmd_version(
        self,
        options: str = '',
    ) -> None:
        """Show the Docker Compose version information."""
        options_args = self._get_list_args(options)
        self._call_backend_app(
            'version', services=[], options_args=options_args
        )
