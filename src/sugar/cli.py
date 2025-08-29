"""Definition of the CLI structure."""

from __future__ import annotations

import os
import sys

from pathlib import Path
from typing import Any, Callable, Dict, Optional, Type, Union, cast

import click
import typer

from typer import Option

from sugar import __version__
from sugar.core import extensions
from sugar.docs import MetaDocs, MetaDocsParams
from sugar.logs import SugarLogs

EXIT_CODE_CONSTANT = 2

# "count" means the number of parameters expected for each flag
CLI_ROOT_FLAGS_VALUES_COUNT = {
    '--dry-run': 0,
    '--file': 1,
    '--profile': 1,
    '--help': 0,  # not necessary to store this value
    '--verbose': 0,
    '--version': 0,  # not necessary to store this value
}

flags_state: dict[str, bool] = {
    'verbose': False,
}

flags_profile: dict[str, str] = {
    'profile': '',
}

flags_dry_run: dict[str, bool] = {
    'dry_run': False,
}

opt_state: dict[str, list[Any]] = {
    'options': [],
    'cmd': [],
}

sugar_exts = {
    ext_name: ext_class() for ext_name, ext_class in extensions.items()
}

typer_profiles: dict[str, typer.Typer] = {}

app = typer.Typer(
    name='sugar',
    help=(
        'Sugar is a tool that help you to organize'
        "and simplify your containers' stack."
    ),
    epilog=(
        'If you have any problem, open an issue at: '
        'https://github.com/osl-incubator/sugar'
    ),
    short_help="Sugar is a tool that help you \
        to organize containers' stack",
    no_args_is_help=True,
)


def _check_sugar_file(file_path: str = '.sugar.yaml') -> bool:
    return Path(file_path).exists()


def version_callback(value: bool) -> None:
    """Print the Sugar version and exit if flag is set."""
    if value:
        SugarLogs.print_info(f'Sugar version: {__version__}')
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    file: str = Option(
        '',
        '--file',
        help='Set the sugar config file.',
    ),
    profile: str = Option(
        '',
        '--profile',
        help='Set the profile of services for running the sugar command.',
    ),
    version: bool = Option(
        False,
        '--version',
        '-v',
        is_flag=True,
        callback=version_callback,
        is_eager=True,
        help='Show the version of sugar.',
    ),
    verbose: bool = Option(
        False,
        '--verbose',
        is_flag=True,
        is_eager=True,
        help='Show the command executed.',
    ),
    dry_run: bool = Option(
        False,
        '--dry-run',
        is_flag=True,
        is_eager=True,
        help="Don't actually execute the command.",
    ),
) -> None:
    """
    Process commands for specific flags.

    Otherwise, show the help menu.
    """
    ctx.ensure_object(dict)

    if verbose:
        # global
        flags_state['verbose'] = True

    if profile:
        # global
        flags_profile['profile'] = profile

    if dry_run:
        # global
        flags_dry_run['dry_run'] = True

    if ctx.invoked_subcommand is None:
        raise typer.Exit()


def map_type_from_string(type_name: str) -> Type[Union[str, int, float, bool]]:
    """
    Return a type object mapped from the type name.

    Parameters
    ----------
    type_name : str
        The string representation of the type.

    Returns
    -------
    type
        The corresponding Python type.
    """
    type_mapping = {
        'str': str,
        'string': str,
        'int': int,
        'integer': int,
        'float': float,
        'bool': bool,
        'boolean': bool,
    }
    return type_mapping.get(type_name, str)


def normalize_string_type(type_name: str) -> str:
    """
    Normalize the user type definition to the correct name.

    Parameters
    ----------
    type_name : str
        The string representation of the type.

    Returns
    -------
    str
        The corresponding makim type name.
    """
    type_mapping = {
        'str': 'str',
        'string': 'str',
        'int': 'int',
        'integer': 'int',
        'float': 'float',
        'bool': 'bool',
        'boolean': 'bool',
        # Add more mappings as needed
    }
    return type_mapping.get(type_name, 'str')


def get_default_value(
    arg_type: str, value: Any
) -> Optional[Union[str, int, float, bool]]:
    """Return the default value regarding its type in a string format."""
    if arg_type == 'bool':
        return False if value is None else bool(value)
    elif arg_type == 'int':
        return int(value) if value is not None else None
    elif arg_type == 'float':
        return float(value) if value is not None else None
    elif arg_type == 'str':
        return str(value) if value is not None else None
    return None


def get_default_value_str(arg_type: str, value: Any) -> str:
    """Return the default value regarding its type in a string format."""
    if arg_type == 'str':
        return f'"{value}"'

    if arg_type == 'bool':
        return 'False'

    return f'{value or 0}'


def create_args_string(args: dict[str, dict[str, str]]) -> str:
    """Return a string for arguments for a function for typer."""
    args_rendered = []

    arg_template_flag = (
        '{arg_name}: Optional[{arg_type}] = typer.Option('
        '{default_value}, '
        '"--{name_flag}", '
        'help="{help_text}"'
        ')'
    )

    arg_template_positional = (
        '{arg_name}: Optional[{arg_type}] = typer.Argument('
        '{default_value}, '
        'help="{help_text}"'
        ')'
    )

    for name, spec in args.items():
        name_clean = name.replace('-', '_')
        arg_type = normalize_string_type(spec.get('type', 'str'))
        help_text = spec.get('help', '')
        default_value = 'None'
        is_positional_only = (
            spec.get('positional_only', 'true').lower() == 'true'
        )

        if not spec.get('required', False) and not spec.get(
            'interactive', False
        ):
            default_value = spec.get('default', '')
            default_value = get_default_value_str(arg_type, default_value)

        selected_template = (
            arg_template_positional
            if is_positional_only
            else arg_template_flag
        )

        arg_str = selected_template.format(
            **{
                'arg_name': name_clean,
                'arg_type': arg_type,
                'default_value': default_value,
                'name_flag': name,
                'help_text': help_text.replace('\n', '\\n'),
            }
        )

        args_rendered.append(arg_str)

    return ', '.join(args_rendered)


def apply_click_options(
    command_function: Callable[..., Any], options: dict[str, Any]
) -> Callable[..., Any]:
    """
    Apply Click options to a Typer command function.

    Parameters
    ----------
    command_function : callable
        The Typer command function to which options will be applied.
    options : dict
        A dictionary of options to apply.

    Returns
    -------
    callable
        The command function with options applied.
    """
    for opt_name, opt_details in options.items():
        opt_args: dict[
            str, Optional[Union[str, int, float, bool, Type[Any]]]
        ] = {}

        opt_data = cast(Dict[str, str], opt_details)
        opt_type_str = normalize_string_type(opt_data.get('type', 'str'))
        opt_default = get_default_value(opt_type_str, opt_data.get('default'))

        if opt_type_str == 'bool':
            opt_args.update({'is_flag': True})

        opt_args.update(
            {
                'default': None
                if opt_data.get('interactive', False)
                else opt_default,
                'type': map_type_from_string(opt_type_str),
                'help': opt_data.get('help', ''),
                'show_default': True,
            }
        )

        click_option = click.option(
            f'--{opt_name}',
            **opt_args,  # type: ignore[arg-type]
        )
        command_function = click_option(command_function)

    return command_function


def create_dynamic_command(
    ext_name: str,
    typer_profile: typer.Typer,
    meta: MetaDocs,
) -> None:
    """
    Dynamically create a Typer command with the specified options.

    Parameters
    ----------
    typer_profile : typer.Typer
    name : str
        The command name.
    meta : dict
        the action/command metadata
    """
    name = cast(str, meta.get('name', ''))
    args = cast(Dict[str, Dict[str, str]], meta.get('parameters', {}))
    fn_help = cast(str, meta.get('title', ''))

    args_str = create_args_string(args)
    args_param_list: list[str] = []
    for arg, _spec in args.items():
        arg_clean = arg.replace('-', '_')
        args_param_list.append(f'{arg}={arg_clean}')
    args_param_str = ','.join(args_param_list)

    # IMPORTANT: allow extra args so we can capture tokens after `--`
    decorator = typer_profile.command(
        name,
        help=fn_help,
        context_settings={
            'allow_extra_args': True,
            'ignore_unknown_options': True,
        },
    )

    # we need ctx to access ctx.args (the tail after `--`)
    needs_options_glue = (
        'options' in args
    )  # only glue tail if command has `options`

    # build function signature
    params_sig = 'ctx: typer.Context'
    if args_str:
        params_sig += f', {args_str}'

    # build function body
    if needs_options_glue:
        glue = (
            '    # If the user typed a literal `--`, '
            'treat the tail as backend options\n'
            '    # Click removes the `--` token, so we detect it via sys.argv '
            'and read ctx.args\n'
            "    extra_tail = list(ctx.args) if '--' in sys.argv else []\n"
            '    if extra_tail:\n'
            '        # merge tail into the `options` string (works with your '
            'existing _get_list_args)\n'
            "        options = (options or '').strip()\n"
            "        tail_str = ' '.join(extra_tail)\n"
            "        options = f'{options} {tail_str}'.strip() if options "
            'else tail_str\n'
        )
        call_line = f'    sugar._cmd_{name}({args_param_str})\n'
    else:
        glue = (
            '    # Command has no `options` parameter; ignore tail to avoid '
            'swallowing typos\n'
            '    _ = ctx.args  # still available if you later want to use it\n'
        )
        call_line = f'    sugar._cmd_{name}({args_param_str})\n'

    function_code = (
        f'def dynamic_command({params_sig}):\n'
        f"    sugar = sugar_exts.get('{ext_name}')\n"
        f'{glue}'
        f'{call_line}'
    )

    local_vars: dict[str, Any] = {}
    exec(function_code, globals(), local_vars)
    decorator(local_vars['dynamic_command'])


# function to create a callback for each Typer profile
def subcommand_callback() -> Callable[..., None]:
    """Create a callback function for a subcommand Typer instance."""

    def callback(ctx: typer.Context) -> None:
        """Show help when subcommand is invoked without an operation."""
        if ctx.invoked_subcommand is None:
            ctx.obj = ctx.obj or {}
            typer.echo(ctx.command.get_help(ctx))
            raise typer.Exit()

    return callback


def extract_root_config(
    cli_list: list[str] = sys.argv,
) -> dict[str, str | bool]:
    """Extract the root configuration from the CLI."""
    params = cli_list[1:]

    # default values
    sugar_file = '.sugar.yaml'
    profile = ''
    dry_run = False
    verbose = False

    try:
        idx = 0
        while idx < len(params):
            arg = params[idx]
            if arg not in CLI_ROOT_FLAGS_VALUES_COUNT:
                break

            if arg == '--file':
                try:
                    sugar_file = params[idx + 1]
                except IndexError:
                    pass
            elif arg == '--profile':
                try:
                    profile = params[idx + 1]
                except IndexError:
                    pass
            elif arg == '--dry-run':
                dry_run = True
            elif arg == '--verbose':
                verbose = True

            idx += 1 + CLI_ROOT_FLAGS_VALUES_COUNT[arg]
    except Exception:
        red_text = typer.style(
            'The sugar config file was not correctly detected. '
            'Using the default .sugar.yaml.',
            fg=typer.colors.RED,
            bold=True,
        )
        typer.echo(red_text, err=True, color=True)

    return {
        'file': sugar_file,
        'profile': profile,
        'dry_run': dry_run,
        'verbose': verbose,
    }


def _get_command_from_cli() -> str:
    """
    Get the profile and task from CLI.

    This function is based on `CLI_ROOT_FLAGS_VALUES_COUNT`.
    """
    params = sys.argv[1:]
    command = ''

    try:
        idx = 0
        while idx < len(params):
            arg = params[idx]
            if arg not in CLI_ROOT_FLAGS_VALUES_COUNT:
                command = f'flag `{arg}`' if arg.startswith('--') else arg
                break

            idx += 1 + CLI_ROOT_FLAGS_VALUES_COUNT[arg]
    except Exception as e:
        print(e)

    return command


def _is_help_requested() -> bool:
    """Check if help flag is present in arguments."""
    return any(arg in ['--help', '-h'] for arg in sys.argv[1:])


def _handle_config_file(help_requested: bool, config_file_path: str) -> None:
    """Handle config file validation and errors."""
    if not help_requested and not _check_sugar_file(config_file_path):
        typer.secho(
            f"Error: Sugar config file '{config_file_path}' "
            'not found in current directory.',
            fg='red',
            err=True,
        )
        raise typer.Exit(1)


def _show_warning_config_file_not_found(config_file_path: str) -> None:
    if not _check_sugar_file(config_file_path):
        typer.secho(
            f"Warning: Sugar config file '{config_file_path}' "
            'not found. Some commands may not be fully documented.',
            fg='yellow',
            err=True,
        )


def _handle_autocomplete(
    help_requested: bool, config_file_path: str
) -> tuple[dict[str, str | bool], str]:
    """Handle autocomplete when config file is not found."""
    cli_completion_words = [
        w for w in os.getenv('COMP_WORDS', '').split('\n') if w
    ]

    root_config = extract_root_config()

    if (
        not help_requested
        and not _check_sugar_file(config_file_path)
        and cli_completion_words
    ):
        # autocomplete call
        root_config = extract_root_config(cli_completion_words)
        config_file_path = cast(str, root_config.get('file', '.sugar.yaml'))

    return root_config, config_file_path


def _process_extensions(
    help_requested: bool,
    config_file_path: str,
    root_config: dict[str, str | bool],
) -> dict[str, list[MetaDocs]]:
    """Process extensions and extract commands."""
    for sugar_ext in sugar_exts.values():
        if not help_requested:
            sugar_ext.load(
                file=config_file_path,
                profile=cast(str, root_config.get('profile', '')),
                dry_run=cast(bool, root_config.get('dry_run', False)),
                verbose=cast(bool, root_config.get('verbose', False)),
            )

    commands: dict[str, list[MetaDocs]] = {}

    for ext_name, ext_class in extensions.items():
        ext_obj = ext_class()
        commands[ext_name] = []

        for action in ext_obj.actions:
            fn_name = f'_cmd_{action}'
            fn = getattr(ext_obj, fn_name)
            title = fn._meta_docs.get('title', '')

            commands[ext_name].append(
                cast(
                    MetaDocs,
                    {
                        'name': action,
                        'title': title,
                        'parameters': cast(
                            MetaDocsParams, fn._meta_docs.get('parameters', {})
                        ),
                    },
                )
            )

    return commands


def _setup_typer_app(commands: dict[str, list[MetaDocs]]) -> None:
    """Set up the Typer app with commands."""
    for ext_name, actions_meta in commands.items():
        ext_obj = extensions[ext_name]()

        if not ext_obj:
            SugarLogs.raise_error(f'Extension not found ({ext_name}).')

        typer_profile = typer.Typer(
            help=ext_obj.__doc__,
            invoke_without_command=True,
        )

        # callback to show help when subcommand is invoked without operation
        typer_profile.callback()(subcommand_callback())

        typer_profiles[ext_name] = typer_profile

        for action_meta in actions_meta:
            create_dynamic_command(ext_name, typer_profile, action_meta)

    # Add each profile to the main app
    for ext_name, typer_profile in typer_profiles.items():
        app.add_typer(
            typer_profile,
            name=ext_name,
            rich_help_panel='COMMAND',
            no_args_is_help=True,
        )


def run_app() -> None:
    """Run the typer app."""
    root_config = extract_root_config()
    help_requested = _is_help_requested()

    config_file_path = cast(str, root_config.get('file', '.sugar.yaml'))

    # Show warning if config file not found while showing help
    _show_warning_config_file_not_found(config_file_path)

    # Handle autocomplete
    root_config, config_file_path = _handle_autocomplete(
        help_requested, config_file_path
    )

    if not _check_sugar_file(config_file_path) and not help_requested:
        return

    _handle_config_file(help_requested, config_file_path)

    # Process extensions and extract commands
    commands = _process_extensions(
        help_requested, config_file_path, root_config
    )

    # Set up Typer app with commands
    _setup_typer_app(commands)

    try:
        app()
    except SystemExit as e:
        # code 2 means command not found
        if e.code == EXIT_CODE_CONSTANT:
            app(['--help'], standalone_mode=False)
            typer.Exit(code=1)
            os._exit(1)
        raise e


if __name__ == '__main__':
    run_app()
