"""
Sugar plugin for docker swarm and docker service.

Swarm Commands:
  - config      Manage Swarm configs
  - node        Manage Swarm nodes
  - secret      Manage Swarm secrets
  - service     Manage Swarm services
  - stack       Manage Swarm stacks
  - swarm       Manage Swarm
"""

from __future__ import annotations

import io
import sys

from typing import Any, Union

import sh
import yaml

from sugar.docs import docparams
from sugar.extensions.compose import SugarCompose, SugarComposeBase
from sugar.logs import SugarError, SugarLogs
from sugar.utils import prepend_stack_name
from sugar.validation import require_not_blank

MSG_ERROR_STACK_NAME = 'Stack name must be provided'
MSG_ERROR_NODES_NAME = 'Node name(s) must be provided'

doc_profile = {
    'profile': 'Specify the profile name of the services you want to use.'
}
doc_options = {
    'options': (
        'Specify the options for the backend command. '
        'E.g.: `--  --advertise-addr 192.168.1.1`.'
    )
}
doc_service = {'service': 'Set the service for the swarm command.'}
doc_services = {
    'services': 'Set the services separated by comma for the swarm command.'
}
doc_node = {'node': 'Set the node for the swarm command.'}
doc_nodes = {
    'nodes': 'Set the nodes separated by comma for the swarm command.'
}
doc_all_services = {'all': 'Use all services for the command.'}
doc_all_nodes = {'all': 'Use all nodes for the command.'}
doc_subcommand = {'subcommand': 'Subcommand to execute for the node command.'}
doc_stack = {'stack': 'Name of the stack to deploy'}
doc_compose_file = {
    'file': 'Path to a Compose file (overrides the one from group/profile)',
}

doc_common_no_services = {**doc_profile, **doc_options}
doc_common_service = {**doc_profile, **doc_service, **doc_options}
doc_common_services = {
    **doc_profile,
    **doc_services,
    **doc_all_services,
    **doc_options,
}

doc_common_services_stack = {**doc_common_services, **doc_stack}

doc_stack_plus_options = {**doc_stack, **doc_options}

doc_common_node = {**doc_profile, **doc_node, **doc_options}
doc_common_nodes = {**doc_profile, **doc_nodes, **doc_all_nodes, **doc_options}
doc_node_command = {
    **doc_profile,
    **doc_options,
    **doc_nodes,
    **doc_all_nodes,
    **doc_subcommand,
}

# Node command specific docs
doc_node_options = {
    'demote': 'Demote one or more nodes from manager in the swarm',
    'inspect': 'Display detailed information on one or more nodes',
    'ls': 'List nodes in the swarm',
    'promote': 'Promote one or more nodes to manager in the swarm',
    'ps': 'List tasks running on one or more nodes, defaults to current node',
    'rm': 'Remove one or more nodes from the swarm',
    'update': 'Update a node',
}

doc_service_options = {
    'create': 'Create a new service',
    'inspect': 'Display detailed information on one or more services',
    'logs': 'Fetch the logs of a service or task',
    'ls': 'List services',
    'ps': 'List the tasks of one or more services',
    'rm': 'Remove one or more services',
    'rollback': "Revert changes to a service's configuration",
    'scale': 'Scale one or multiple replicated services',
    'update': 'Update a service',
}

# Service command specific docs
doc_services_logs_options = {
    'details': 'Show extra details provided to logs',
    'stack': 'Name of the stack to inspect',
    'follow': 'Follow log output',
    'no_resolve': 'Do not map IDs to Names in output',
    'no_task_ids': 'Do not include task IDs in output',
    'no_trunc': 'Do not truncate output',
    'raw': 'Do not neatly format logs',
    'since': 'Show logs since timestamp or relative time (e.g. 42m)',
    'tail': 'Number of lines to show from the end of the logs (default all)',
    'timestamps': 'Show timestamps',
}
doc_service_actions = {
    'create': 'Create a new service (use --  for all parameters)',
    'inspect': 'Display detailed information on one or more services',
    'logs': 'Fetch the logs of a service or task',
    'ls': 'List services',
    'ps': 'List the tasks of one or more services',
    'rm': 'Remove one or more services',
    'rollback': "Revert changes to a service's configuration",
    'scale': 'Scale one or multiple replicated services',
    'update': 'Update a service',
}
doc_rollback_options = {
    'detach': (
        'Exit immediately instead of waiting for the service to converge'
    ),
    'quiet': 'Suppress progress output',
}
doc_scale_options = {
    'detach': (
        'Exit immediately instead of waiting for the service to converge'
    ),
    'replicas': (
        'Number of replicas per service '
        '(comma-separated list of service=replicas pairs)'
    ),
}
doc_update_options = {
    'detach': (
        'Exit immediately instead of waiting for the service to converge'
    ),
    'quiet': 'Suppress progress output',
    'image': 'Service image tag',
    'replicas': 'Number of tasks',
    'force': 'Force update even if no changes require it',
    'rollback': 'Rollback to previous specification',
    'env_add': 'Add/update env vars (comma-separated NAME=VALUE list)',
    'label_add': 'Add/update service labels (comma-separated key=value list)',
}


class SugarSwarmBase(SugarComposeBase):
    """SugarSwarmBase provides base functionalities."""

    def _load_backend(self) -> None:
        """Load the backend for the swarm commands."""
        self._load_backend_app()
        self._load_backend_args()

    def _load_backend_app(self) -> None:
        self.backend_app = sh.docker

    def _load_backend_args(self) -> None:
        self.backend_args = []

    def _get_services_names(self, **kwargs: Any) -> list[str]:
        """
        Override to handle swarm service names without requiring config.

        For swarm commands, services are specified directly on the command line
        and don't need to be defined in a config file.
        """
        if 'all' not in kwargs and 'services' not in kwargs:
            # The command doesn't specify services
            return []

        _arg_services = kwargs.get('services', '')
        _arg_stack = kwargs.get('stack', '')

        # For swarm, we don't use the 'all' flag, only explicit services
        if not _arg_services:
            SugarLogs.raise_error(
                'Service name must be provided for this command '
                '(use --services service1,service2)',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

        # Simply split the comma-separated service names
        services_list: list[str] = _arg_services.split(',')

        if _arg_stack:
            services_list = [f'{_arg_stack}_{name}' for name in services_list]

        return services_list

    def _call_stack_command(
        self,
        stack_name: str = '',
        options_args: list[str] = [],
        backend_args: list[str] = [],
        _out: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stdout,
        _err: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stderr,
    ) -> None:
        """
        Call docker stack commands with proper structure.

        For `stack deploy -c -`, internally pipe the rendered compose YAML.
        """
        self.backend_args = backend_args.copy()

        stdin_payload: Union[str, bytes, io.StringIO, None] = None

        # If we're deploying with stdin (`-c -`),
        # render and feed the compose YAML
        args_size = 3
        if (
            len(self.backend_args) >= args_size
            and self.backend_args[0] == 'stack'
            and self.backend_args[1] == 'deploy'
            and '-c' in self.backend_args
            and '-' in self.backend_args
        ):
            stdin_payload = self._render_compose_config()

        self._call_backend_app(
            stack_name,
            options_args=options_args,
            _out=_out,
            _err=_err,
            stdin_data=stdin_payload,
        )

    def _call_command(
        self,
        subcommand: str,
        services: list[str] = [],
        nodes: list[str] = [],
        options_args: list[str] = [],
        cmd_args: list[str] = [],
        _out: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stdout,
        _err: Union[io.TextIOWrapper, io.StringIO, Any] = sys.stderr,
    ) -> None:
        """Call docker swarm commands with proper structure."""
        if services and nodes:
            SugarLogs.raise_error(
                'Give services or nodes arguments, not both.',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

        kwargs: dict[str, Any] = {
            'options_args': options_args,
            'cmd_args': cmd_args,
            '_out': _out,
            '_err': _err,
        }

        if services:
            kwargs['services'] = services
        elif nodes:
            kwargs['nodes'] = nodes
        else:
            # Important for tests: explicitly pass services=[]
            kwargs['services'] = []

        self._call_backend_app(subcommand, **kwargs)

    def _get_services_from_stack(self, stack: str) -> list[str]:
        """Get all services from a stack."""
        try:
            output = io.StringIO()
            self.backend_app(
                'stack',
                'services',
                stack,
                '--format',
                '{{.Name}}',
                _out=output,
            )
            services_output = output.getvalue()

            services = [
                service
                for service in services_output.strip().split('\n')
                if service
            ]
            if not services:
                SugarLogs.raise_error(
                    f'No services found in stack {stack}',
                    SugarError.SUGAR_INVALID_PARAMETER,
                )
            return services
        except Exception as e:
            SugarLogs.raise_error(
                f'Failed to get services from stack {stack}: {e!s}',
                SugarError.SUGAR_COMMAND_ERROR,
            )
            return []

    def _compose_global_args(self) -> list[str]:
        args: list[str] = ['compose']

        # env-file (optional)
        _env_files = self.service_profile.get('env-file')
        if isinstance(_env_files, str):
            env_files = [_env_files]
        elif isinstance(_env_files, list):
            env_files = [f for f in _env_files if isinstance(f, str)]
        else:
            env_files = []

        for f in env_files:
            args.extend(['--env-file', f])

        for p in self._get_config_files_path():
            args.extend(['--file', p])

        pn = self.service_profile.get('project-name')
        if pn:
            args.extend(['--project-name', pn])

        return args

    def _compose_config_text(self) -> str:
        out_buf = io.StringIO()
        err_buf = io.StringIO()
        try:
            self.backend_app(
                *self._compose_global_args(),
                'config',
                _out=out_buf,
                _err=err_buf,
            )
            return out_buf.getvalue()
        except sh.ErrorReturnCode as e:
            err = err_buf.getvalue().strip()
            out = out_buf.getvalue().strip()
            msg = err or out or str(e)
            SugarLogs.raise_error(
                f'docker compose config failed:\n{msg}',
                SugarError.SUGAR_COMMAND_ERROR,
            )
            return ''

    def _normalize_for_stack(self, doc: dict[str, Any]) -> dict[str, Any]:
        doc.pop('name', None)

        svcs = doc.get('services') or {}
        for svc in svcs.values():
            ports = (svc or {}).get('ports') or []
            for p in ports:
                if not isinstance(p, dict):
                    continue
                for key in ('published', 'target'):
                    v = p.get(key)
                    if isinstance(v, str) and v.isdigit():
                        p[key] = int(v)
        return doc

    def _render_compose_config(self) -> str:
        """
        Use SugarCompose to render the effective YAML.

        It returns it as a string to be piped into `stack deploy -c -`.
        """
        compose = SugarCompose()
        compose.load(
            file=self.file,
            profile=self.profile_selected,
            dry_run=self.dry_run,
            verbose=self.verbose,
        )

        out, err = io.StringIO(), io.StringIO()
        compose._call_backend_app('config', _out=out, _err=err)

        yaml_text = out.getvalue()
        if not yaml_text.strip():
            SugarLogs.raise_error(
                f'Rendered compose configuration is empty.'
                f'\n\nSTDERR:\n{err.getvalue()}',
                SugarError.SUGAR_INVALID_CONFIGURATION,
            )

        doc = self._normalize_for_stack(yaml.safe_load(yaml_text))
        yaml_text = yaml.safe_dump(doc, sort_keys=False)

        return yaml_text


class SugarSwarm(SugarSwarmBase):
    """
    SugarSwarm provides the docker swarm commands.

    Commands: ca, init, join, join, leave, unlock, unlock, update.
    """

    def _load_backend_args(self) -> None:
        self.backend_args = ['swarm']

    @docparams(doc_common_no_services)
    def _cmd_ca(
        self,
        options: str = '',
    ) -> None:
        """Display and rotate the root CA."""
        options_args = self._get_list_args(options)
        self._call_command('join', options_args=options_args)

    @docparams(doc_common_no_services)
    def _cmd_init(
        self,
        options: str = '',
    ) -> None:
        """Initialize a swarm.

        This command initializes a new swarm on the current Docker engine.
        """
        options_args = self._get_list_args(options)
        self._call_command('init', options_args=options_args)

    @docparams(doc_common_no_services)
    def _cmd_join(
        self,
        options: str = '',
    ) -> None:
        """Join a swarm as a node and/or manager."""
        options_args = self._get_list_args(options)
        self._call_command('join', options_args=options_args)

    @docparams(doc_common_no_services)
    def _cmd_join_token(
        self,
        options: str = '',
    ) -> None:
        """Manage join tokens."""
        options_args = self._get_list_args(options)
        self._call_command('join-token', options_args=options_args)

    @docparams(doc_common_no_services)
    def _cmd_leave(
        self,
        options: str = '',
    ) -> None:
        """Leave the swarm."""
        options_args = self._get_list_args(options)
        self._call_command('leave', options_args=options_args)

    @docparams(doc_common_no_services)
    def _cmd_unlock(
        self,
        options: str = '',
    ) -> None:
        """Unlock swarm."""
        options_args = self._get_list_args(options)
        self._call_command('unlock', options_args=options_args)

    @docparams(doc_common_no_services)
    def _cmd_unlock_key(
        self,
        options: str = '',
    ) -> None:
        """Manage the unlock key."""
        options_args = self._get_list_args(options)
        self._call_command('unlock-key', options_args=options_args)

    @docparams({**doc_update_options})
    def _cmd_update(
        self,
        detach: bool = False,
        quiet: bool = False,
        image: str = '',
        replicas: str = '',
        force: bool = False,
        rollback: bool = False,
        env_add: str = '',
        label_add: str = '',
        options: str = '',
    ) -> None:
        """Update services (docker service update)."""
        names: list[str] = []
        opts = self._get_list_args(options)

        if detach:
            opts.append('--detach')
        if quiet:
            opts.append('--quiet')
        if force:
            opts.append('--force')
        if rollback:
            opts.append('--rollback')
        if image:
            opts.extend(['--image', image])
        if replicas:
            opts.extend(['--replicas', replicas])

        if env_add:
            for pair in env_add.split(','):
                if pair.strip():
                    opts.extend(['--env-add', pair.strip()])
        if label_add:
            for pair in label_add.split(','):
                if pair.strip():
                    opts.extend(['--label-add', pair.strip()])

        self._call_command('update', services=names, options_args=opts)


class SugarSwarmService(SugarSwarmBase):
    """
    SugarSwarmService provides the `docker service` commands.

    Commands: create, inspect, logs, ls, ps, rm, rollback, scale, update.
    """

    def _load_backend_args(self) -> None:
        self.backend_args = ['service']

    def _perform_service_rollback(
        self, service: str, options_args: list[str]
    ) -> bool:
        """Perform rollback for a single service; True on success."""
        try:
            output = io.StringIO()
            error = io.StringIO()
            self.backend_app(
                'service',
                'rollback',
                *options_args,
                service,
                _out=output,
                _err=error,
                _ok_code=[0, 1],
            )
            err = error.getvalue()
            if 'does not have a previous spec' in err:
                SugarLogs.print_warning(
                    f'Service {service} has no previous version to rollback to'
                )
                return False
            if err:
                SugarLogs.print_warning(
                    f'Failed to rollback service {service}: {err.strip()}'
                )
                return False
            print(f'Successfully rolled back service {service}')
            return True
        except Exception as e:
            SugarLogs.print_warning(
                f'Error rolling back service {service}: {e!s}'
            )
            return False

    @docparams(doc_options)
    def _cmd_create(self, options: str = '') -> None:
        """Create a new service (docker service create)."""
        if not options:
            SugarLogs.raise_error(
                'Options must be provided for "create". '
                'Include --name, image, etc. inside -- .',
                SugarError.SUGAR_INVALID_PARAMETER,
            )
        self._call_command(
            'create', services=[], options_args=self._get_list_args(options)
        )

    @require_not_blank('stack')
    @docparams({**doc_common_services_stack})
    def _cmd_inspect(
        self,
        stack: str = '',
        services: str = '',
        all: bool = False,
        options: str = '',
    ) -> None:
        """Inspect one or more services (docker service inspect)."""
        services_names = self._get_services_names(
            services=services, all=all, stack=stack
        )
        self._call_command(
            'inspect',
            services=services_names,
            options_args=self._get_list_args(options),
        )

    @docparams({**doc_common_services, **doc_services_logs_options})
    def _cmd_logs(
        self,
        services: str = '',
        all: bool = False,
        stack: str = '',
        details: bool = False,
        follow: bool = False,
        no_resolve: bool = False,
        no_task_ids: bool = False,
        no_trunc: bool = False,
        raw: bool = False,
        since: str = '',
        tail: str = '',
        timestamps: bool = False,
        options: str = '',
    ) -> None:
        """Fetch logs of a service or task (docker service logs)."""
        svc_names = prepend_stack_name(
            stack_name=stack,
            services=self._get_services_names(services=services, all=all),
        )
        opts = self._get_list_args(options)
        if details:
            opts.append('--details')
        if follow:
            opts.append('--follow')
        if no_resolve:
            opts.append('--no-resolve')
        if no_task_ids:
            opts.append('--no-task-ids')
        if no_trunc:
            opts.append('--no-trunc')
        if raw:
            opts.append('--raw')
        if timestamps:
            opts.append('--timestamps')
        if since:
            opts.extend(['--since', since])
        if tail:
            opts.extend(['--tail', tail])

        self._call_command('logs', services=svc_names, options_args=opts)

    @docparams(doc_common_no_services)
    def _cmd_ls(self, options: str = '') -> None:
        """List services (docker service ls)."""
        self._call_command('ls', options_args=self._get_list_args(options))

    @docparams(doc_common_services)
    def _cmd_ps(
        self, services: str = '', all: bool = False, options: str = ''
    ) -> None:
        """List tasks of services (docker service ps)."""
        names = self._get_services_names(services=services, all=all)
        self._call_command(
            'ps', services=names, options_args=self._get_list_args(options)
        )

    @docparams(doc_common_services)
    def _cmd_rm(
        self, services: str = '', all: bool = False, options: str = ''
    ) -> None:
        """Remove services (docker service rm)."""
        names = self._get_services_names(services=services, all=all)
        self._call_command(
            'rm', services=names, options_args=self._get_list_args(options)
        )

    @docparams({**doc_common_service, **doc_rollback_options, **doc_stack})
    def _cmd_rollback(
        self,
        service: str = '',
        stack: str = '',
        detach: bool = False,
        quiet: bool = False,
        options: str = '',
    ) -> None:
        """
        Roll back services to previous versions (docker service rollback).

        Supports either explicit --services or whole --stack.
        """
        opts = self._get_list_args(options)
        if detach:
            opts.append('--detach')
        if quiet:
            opts.append('--quiet')

        targets = self._get_services_names(
            services=service,
            all=False,
            stack=stack,
        )

        if not targets:
            SugarLogs.print_warning('No services specified for rollback')
            return

        ok, bad = 0, 0
        for svc in targets:
            if self._perform_service_rollback(svc, opts):
                ok += 1
            else:
                bad += 1
        print(f'Rollback complete: {ok} succeeded, {bad} failed')

    @require_not_blank(name='replicas')
    @require_not_blank(name='stack')
    @docparams({**doc_scale_options, **doc_stack})
    def _cmd_scale(
        self,
        replicas: str = '',
        stack: str = '',
        detach: bool = False,
        options: str = '',
    ) -> None:
        """
        Scale services (docker service scale).

        Use --replicas "svc1=3,svc2=5".
        """
        if not replicas:
            SugarLogs.raise_error(
                'Services must be provided in format service=replicas[,..]',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

        opts = self._get_list_args(options)
        if detach:
            opts.append('--detach')

        _args_extra = {'all': False, 'stack': stack}

        fn = self._get_services_names

        pairs: list[str] = []

        for pair in replicas.split(','):
            if not pair:
                continue

            service, replica = pair.split('=')
            pairs.append(f'{fn(services=service, **_args_extra)[0]}={replica}')
        self._call_command(
            'scale', services=pairs, options_args=self._get_list_args(options)
        )

    @docparams({**doc_common_services, **doc_update_options})
    def _cmd_update(
        self,
        services: str = '',
        all: bool = False,
        detach: bool = False,
        quiet: bool = False,
        image: str = '',
        replicas: str = '',
        force: bool = False,
        rollback: bool = False,
        env_add: str = '',
        label_add: str = '',
        options: str = '',
    ) -> None:
        """Update services (docker service update)."""
        names = self._get_services_names(services=services, all=all)
        opts = self._get_list_args(options)

        if detach:
            opts.append('--detach')
        if quiet:
            opts.append('--quiet')
        if force:
            opts.append('--force')
        if rollback:
            opts.append('--rollback')
        if image:
            opts.extend(['--image', image])
        if replicas:
            opts.extend(['--replicas', replicas])

        if env_add:
            for pair in env_add.split(','):
                if pair.strip():
                    opts.extend(['--env-add', pair.strip()])
        if label_add:
            for pair in label_add.split(','):
                if pair.strip():
                    opts.extend(['--label-add', pair.strip()])

        self._call_command('update', services=names, options_args=opts)


class SugarSwarmStack(SugarSwarmBase):
    """
    SugarSwarmStack provides the docker stack commands.

    Commands: config, deploy, ls, ps, rm, services.
    """

    def _load_backend_args(self) -> None:
        self.backend_args = ['stack']

    @docparams(
        {
            **doc_stack,
            **doc_options,
        }
    )
    def _cmd_deploy(
        self,
        /,
        stack: str = '',
        options: str = '',
    ) -> None:
        """Deploy a new stack from a compose file (via stdin piping)."""
        if not stack:
            SugarLogs.raise_error(
                MSG_ERROR_STACK_NAME,
                SugarError.SUGAR_INVALID_PARAMETER,
            )

        yaml_text = self._render_compose_config()
        options_args = self._get_list_args(options)

        self.backend_args = ['stack', 'deploy', '-c', '-']
        self._call_backend_app(
            stack,
            options_args=options_args,
            stdin_data=yaml_text,
        )

    @docparams(
        {
            **doc_stack_plus_options,
            'quiet': 'Only display IDs',
        }
    )
    def _cmd_ls(
        self,
        /,
        stack: str = '',
        quiet: bool = False,
        options: str = '',
    ) -> None:
        """List the tasks in the stack."""
        if not stack:
            SugarLogs.raise_error(
                MSG_ERROR_STACK_NAME,
                SugarError.SUGAR_INVALID_PARAMETER,
            )

        backend_args = ['stack', 'ps']
        if quiet:
            backend_args = ['stack', 'ps', '--quiet']

        options_args = self._get_list_args(options)
        self._call_stack_command(
            stack_name=stack,
            options_args=options_args,
            backend_args=backend_args,
        )

    @docparams(
        {
            **doc_stack_plus_options,
            'quiet': 'Only display IDs',
        }
    )
    def _cmd_ps(
        self,
        /,
        stack: str = '',
        quiet: bool = False,
        options: str = '',
    ) -> None:
        """List the tasks in the stack."""
        if not stack:
            SugarLogs.raise_error(
                MSG_ERROR_STACK_NAME,
                SugarError.SUGAR_INVALID_PARAMETER,
            )

        backend_args = ['stack', 'ps']
        if quiet:
            backend_args = ['stack', 'ps', '--quiet']

        options_args = self._get_list_args(options)
        self._call_stack_command(
            stack_name=stack,
            options_args=options_args,
            backend_args=backend_args,
        )

    @docparams(doc_stack_plus_options)
    def _cmd_rm(
        self,
        /,
        stack: str = '',
        options: str = '',
    ) -> None:
        """Remove the stack from the swarm."""
        self._call_stack_command(
            stack_name=stack,
            options_args=self._get_list_args(options),
            backend_args=['stack', 'rm'],
        )


class SugarSwarmNode(SugarSwarmBase):
    """
    SugarSwarmNode provides the docker node commands.

    Commands: demote, inspect, ls, promote, ps, current node, rm, update.
    """

    def _load_backend_args(self) -> None:
        self.backend_args = ['node']

    @docparams(doc_common_nodes)
    def _cmd_demote(
        self,
        nodes: str = '',
        options: str = '',
    ) -> None:
        """Demote one or more nodes from manager in the swarm."""
        node_names = [node for node in nodes.split(',') if node]
        if not node_names:
            SugarLogs.raise_error(
                MSG_ERROR_NODES_NAME,
                SugarError.SUGAR_INVALID_PARAMETER,
            )
        options_args = self._get_list_args(options)
        self._call_command(
            'demote', nodes=node_names, options_args=options_args
        )

    @docparams(doc_common_nodes)
    def _cmd_inspect(
        self,
        nodes: str = '',
        options: str = '',
    ) -> None:
        """Display detailed information on one or more nodes."""
        node_names = [node for node in nodes.split(',') if node]
        if not node_names:
            SugarLogs.raise_error(
                MSG_ERROR_NODES_NAME,
                SugarError.SUGAR_INVALID_PARAMETER,
            )
        options_args = self._get_list_args(options)
        self._call_command(
            'inspect', nodes=node_names, options_args=options_args
        )

    @docparams(doc_common_no_services)
    def _cmd_ls(
        self,
        options: str = '',
    ) -> None:
        """List nodes in the swarm."""
        options_args = self._get_list_args(options)
        self._call_command('ls', options_args=options_args)

    @docparams(doc_common_nodes)
    def _cmd_promote(
        self,
        nodes: str = '',
        options: str = '',
    ) -> None:
        """Promote one or more nodes to manager in the swarm."""
        node_names = [node for node in nodes.split(',') if node]
        if not node_names:
            SugarLogs.raise_error(
                MSG_ERROR_NODES_NAME,
                SugarError.SUGAR_INVALID_PARAMETER,
            )
        options_args = self._get_list_args(options)
        self._call_command(
            'promote', nodes=node_names, options_args=options_args
        )

    @docparams(doc_common_nodes)
    def _cmd_ps(
        self,
        nodes: str = '',
        options: str = '',
    ) -> None:
        """List tasks running on one or more nodes."""
        node_names = [node for node in nodes.split(',') if node]
        if not node_names:
            SugarLogs.raise_error(
                MSG_ERROR_NODES_NAME,
                SugarError.SUGAR_INVALID_PARAMETER,
            )
        options_args = self._get_list_args(options)
        self._call_command('ps', nodes=node_names, options_args=options_args)

    @docparams(doc_common_nodes)
    def _cmd_rm(
        self,
        nodes: str = '',
        options: str = '',
    ) -> None:
        """Remove one or more nodes from the swarm."""
        node_names = [node for node in nodes.split(',') if node]
        if not node_names:
            SugarLogs.raise_error(
                MSG_ERROR_NODES_NAME,
                SugarError.SUGAR_INVALID_PARAMETER,
            )
        options_args = self._get_list_args(options)
        self._call_command('rm', nodes=node_names, options_args=options_args)

    @docparams(doc_common_nodes)
    def _cmd_update(
        self,
        nodes: str = '',
        options: str = '',
    ) -> None:
        """Update a node."""
        node_names = [node for node in nodes.split(',') if node]
        if not node_names:
            SugarLogs.raise_error(
                MSG_ERROR_NODES_NAME,
                SugarError.SUGAR_INVALID_PARAMETER,
            )
        options_args = self._get_list_args(options)
        self._call_command(
            'update', nodes=node_names, options_args=options_args
        )
