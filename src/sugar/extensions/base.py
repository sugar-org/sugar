"""SugarBase classes for containers."""

from __future__ import annotations

import io
import json
import os
import shlex
import sys
import tempfile

from abc import ABC, abstractmethod
from copy import deepcopy
from pathlib import Path
from typing import Any, Union

import dotenv
import sh
import yaml

from jinja2 import Environment
from jsonschema import ValidationError, validate

from sugar import __version__
from sugar.logs import SugarError, SugarLogs
from sugar.utils import camel_to_snake

TEMPLATE = Environment(
    autoescape=False,
    variable_start_string='${{',
    variable_end_string='}}',
)

SUGAR_CURRENT_PATH = Path(__file__).parent.parent


class SugarBase(ABC):
    """SugarBase defined the base structure for the Sugar classes."""

    actions: list[str] = []
    args: dict[str, str] = {}
    file: str = ''
    config: dict[str, Any] = {}
    # note: it starts with a simple command
    #       it is replaced later in the execution
    backend_app: sh.Command = sh.echo
    backend_args: list[str] = []
    defaults: dict[str, Any] = {}
    dry_run: bool = False
    env: dict[str, str] = {}
    options_args: list[str] = []
    cmd_args: list[str] = []
    service_profile: dict[str, Any] = {}
    service_names: list[str] = []
    profile_selected: str = ''
    verbose: bool = False
    hooks: dict[str, list[dict[str, Any]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Initialize the actions list for all the created commands."""
        super().__init_subclass__(**kwargs)
        # Ensure each subclass has its own actions list
        cls.actions = cls.actions.copy()
        prefix = '_cmd_'
        prefix_len = len(prefix)
        for name, value in cls.__dict__.items():
            if callable(value) and name.startswith(prefix):
                action_name = name[prefix_len:]
                cls.actions.append(action_name)

    def __init__(self) -> None:
        """Initialize SugarBase instance."""
        self.file = '.sugar.yaml'
        self.verbose = False
        self.dry_run = False
        self.args: dict[str, str] = {}
        self.options_args: list[str] = []
        self.cmd_args: list[str] = []
        self.config: dict[str, Any] = {}
        self.backend_args: list[str] = []
        self.defaults: dict[str, Any] = {}
        self.env: dict[str, str] = {}
        self.service_profile: dict[str, Any] = {}
        self.service_names: list[str] = []
        self.profile_selected: str = ''

    def _setup_load(self, **kwargs: Any) -> None:
        """Set up the configuration for running the commands."""
        args: dict[str, str] = kwargs.get('args', {})
        options_args: list[str] = kwargs.get('options_args', [])
        cmd_args: list[str] = kwargs.get('cmd_args', [])

        self.args = deepcopy(args)
        self.options_args = deepcopy(options_args)
        # note: it needs to be refactored
        self.cmd_args = deepcopy(cmd_args)

        self._load_config()
        self._load_env()
        self._load_defaults()
        self._load_root_services()

        self._load_profile()
        self._load_backend()

        self._verify_config()

    @abstractmethod
    def _load_backend(self) -> None:
        """
        Initialize the backend application and its arguments.

        This method must be implemented by subclasses to set:
        - self.backend_app
        - self.backend_args
        """
        pass

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
        # validation
        if services and nodes:
            SugarLogs.raise_error(
                'Give services or nodes arguments, not both.',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

        nodes_or_services = services or nodes

        # Execute pre-run hooks
        extension = camel_to_snake(
            self.__class__.__name__.replace('Sugar', '')
        )
        self._execute_hooks('pre-run', extension, action)

        sh_extras = {
            '_in': sys.stdin,
            '_out': _out,
            '_err': _err,
            '_no_err': True,
            '_env': os.environ,
            '_bg': True,
            '_bg_exc': False,
        }

        positional_parameters = [
            *self.backend_args,
            *[action],
            *options_args,
            *nodes_or_services,
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

    def _check_config_file(self) -> bool:
        return Path(self.file).exists()

    # Check if services item is given
    def _check_services_item(self) -> bool:
        return hasattr(self.config, 'services')

    def _execute_hooks(
        self, hook_type: str, extension: str, action: str
    ) -> None:
        """Execute hooks specific type, extension, and action."""
        hooks = self.hooks.get(hook_type, [])

        sh_extras = {
            '_in': sys.stdin,
            '_out': sys.stdout,
            '_err': sys.stderr,
            '_no_err': True,
            '_env': os.environ,
        }

        fd, filepath = tempfile.mkstemp(suffix='sugar', text=True)

        for hook in hooks:
            targets = hook.get('targets', {})
            target_ext = targets.get(extension, [])
            hook_name = hook.get('name', '')

            if not target_ext or action not in target_ext:
                continue

            SugarLogs.print_info(f'Running {hook_type} hook: {hook_name} ...')
            cmd = hook.get('run', '').strip()

            with open(filepath, 'w') as f:
                f.write(cmd)

            sh.xonsh(filepath, **sh_extras)

        os.remove(filepath)

    # set default profile main
    def _load_root_services(self) -> None:
        """Load services attribute in the root of the configuration."""
        # must set the default profile
        services = self.config.get('services', {})

        if not services:
            return

        self.config['profiles'] = {
            'main': {
                'project-name': services.get('project-name'),
                'config-path': services.get('config-path'),
                'env-file': services.get('env-file'),
                'services': {
                    'default': services.get('default', []),
                    'available': services.get('available', []),
                },
            }
        }
        self.defaults['profile'] = 'main'
        self.profile_selected = 'main'
        self.service_profile = deepcopy(self.config['profiles']['main'])
        del self.config['services']

    def _filter_service_profile(self) -> None:
        profiles = self.config['profiles']

        # Verify if project-name is not null
        default_project_name = self.defaults.get('project-name', '') or ''

        for profile_name, profile_data in profiles.items():
            if profile_name == self.profile_selected:
                if default_project_name and 'project-name' not in profile_data:
                    # just use default value if "project-name" is not set
                    profile_data['project-name'] = default_project_name
                if not profile_data.get('services', {}).get('default'):
                    # if default is not given or it is empty or null,
                    # use as default all the services available
                    default_services = [
                        service['name']
                        for service in profile_data.get('services', {}).get(
                            'available', []
                        )
                    ]
                    profile_data['services']['default'] = default_services
                self.service_profile = profile_data
                return

        SugarLogs.raise_error(
            f'The given profile service "{self.profile_selected}" '
            'was not found in the configuration file.',
            SugarError.SUGAR_MISSING_PARAMETER,
        )

    def _load_config(self) -> None:
        with open(self.file, 'r') as f:
            # escape template tags
            content = f.read()
            f_content = io.StringIO(content)
            self.config = yaml.safe_load(f_content)

        # check if either  services or  profiles are present
        if not (self.config.get('services') or self.config.get('profiles')):
            SugarLogs.raise_error(
                'Either `services` OR  `profiles` flag must be given',
                SugarError.SUGAR_INVALID_CONFIGURATION,
            )
        # check if both services and profiles are present
        if self.config.get('services') and self.config.get('profiles'):
            SugarLogs.raise_error(
                '`services` and `profiles` flags given, only 1 is allowed.',
                SugarError.SUGAR_INVALID_CONFIGURATION,
            )

        self._validate_config()

        # Load hooks
        self.hooks = self.config.get('hooks', {})

    def _load_defaults(self) -> None:
        _defaults = self.config.get('defaults', {})

        for k, v in _defaults.items():
            unescaped_value = v if isinstance(v, str) else str(v)

            _defaults[k] = yaml.safe_load(
                TEMPLATE.from_string(unescaped_value).render(env=self.env)
            )

        self.defaults = _defaults

    def _load_env(self) -> None:
        self.env = dict(os.environ)

        env_files = self.config.get('env-file', '')

        if isinstance(env_files, str):
            env_files = [env_files] if env_files else []

        if not env_files:
            return

        for env_file in env_files:
            if not env_file:
                continue

            env_file_path = env_file

            if not env_file.startswith('/'):
                # use .sugar file as reference for the working
                # directory for the .env file
                env_file_path = str(Path(self.file).parent / env_file)

            if not Path(env_file_path).exists():
                SugarLogs.raise_error(
                    f'Env file was not found: {env_file_path}',
                    SugarError.SUGAR_INVALID_CONFIGURATION,
                )
            self.env.update(dotenv.dotenv_values(env_file_path))  # type: ignore

    def _load_profile(self) -> None:
        if not self.profile_selected:
            default_profile = self.defaults.get('profile', '')
            if not default_profile:
                SugarLogs.raise_error(
                    'The service profile parameter or default '
                    "profile configuration weren't defined.",
                    SugarError.SUGAR_INVALID_PARAMETER,
                )
            self.profile_selected = default_profile
        self._filter_service_profile()

    def _get_list_args(self, args: str) -> list[str]:
        """Return a list with the name of the service if any."""
        if not args.strip():
            return []

        return shlex.split(args)

    def _get_service_name(self, service: str) -> list[str]:
        """Return a list with the name of the service if any."""
        return [service] if service else []

    def _get_services_names(self, **kwargs: Any) -> list[str]:
        if 'all' not in kwargs and 'services' not in kwargs:
            # the command doesn't specify services (e.g. version)
            return []

        _arg_services = kwargs.get('services', '')
        _arg_all = kwargs.get('all', False)

        services_config = self.service_profile['services']
        service_names: list[str] = []
        services_default = services_config.get('default', [])

        if _arg_all:
            service_names = [
                service['name']
                for service in self.service_profile.get('services', {}).get(
                    'available', []
                )
            ]
        elif _arg_services:
            service_names = _arg_services.split(',')
        elif services_default:
            service_names = services_default
        else:
            SugarLogs.raise_error(
                'If you want to execute the operation for all services, '
                'use --all parameter.',
                SugarError.SUGAR_INVALID_PARAMETER,
            )

        return service_names

    def _validate_config(self) -> None:
        """
        Validate the .sugar.yaml against the predefined JSON Schema.

        Raises
        ------
            SugarError: If the configuration does not conform to the schema.
        """
        try:
            with open(SUGAR_CURRENT_PATH / 'schema.json', 'r') as schema_file:
                schema = json.load(schema_file)

            config_data = self.config

            # Validate the configuration against the schema
            validate(instance=config_data, schema=schema)

            if self.verbose:
                SugarLogs.print_info('Configuration validation successful.')

        except ValidationError as ve:
            error_message = f'Configuration validation error: {ve.message}'
            SugarLogs.raise_error(
                error_message, SugarError.CONFIG_VALIDATION_ERROR
            )
        except yaml.YAMLError as ye:
            error_message = f'YAML parsing error: {ye}'
            SugarLogs.raise_error(error_message, SugarError.YAML_PARSING_ERROR)
        except json.JSONDecodeError as je:
            error_message = f'JSON schema decoding error: {je}'
            SugarLogs.raise_error(
                error_message, SugarError.JSON_SCHEMA_DECODING_ERROR
            )
        except FileNotFoundError:
            error_message = f'Configuration file {self.file} not found.'
            SugarLogs.raise_error(
                error_message, SugarError.SUGAR_CONFIG_FILE_NOT_FOUND
            )
        except Exception as e:
            error_message = (
                f'Unexpected error during configuration validation: {e}'
            )
            SugarLogs.raise_error(
                error_message, SugarError.CONFIG_VALIDATION_UNEXPECTED_ERROR
            )

    def _verify_config(self) -> None:
        if not self._check_config_file():
            SugarLogs.raise_error(
                'Config file .sugar.yaml not found.',
                SugarError.SUGAR_INVALID_CONFIGURATION,
            )

        if not len(self.config.get('profiles', {})):
            SugarLogs.raise_error(
                'No service profiles found.',
                SugarError.SUGAR_INVALID_CONFIGURATION,
            )

    def _version(self) -> None:
        SugarLogs.print_info(f'Sugar Version: {__version__}')

    def load(
        self,
        file: str = '.sugar.yaml',
        profile: str = '',
        dry_run: bool = False,
        verbose: bool = False,
    ) -> None:
        """Load sugar configuration."""
        self.file = file
        self.profile_selected = profile
        self.dry_run = dry_run
        self.verbose = verbose

        self._setup_load()
