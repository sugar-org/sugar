"""Apple Container Extension for Sugar.

Manages Apple Container runtime on macOS M-series chips.
Provides interface compatible with docker-compose workflow.
"""

import subprocess
import sys

from typing import Any, Dict, List, Optional


class AppleContainerExtension:
    """Apple Container extension for Sugar.

    Provides a unified interface for managing containers using
    Apple's container runtime on M-series Macs.
    """

    STANDARD_COMMANDS: List[str] = [
        'build',
        'create',
        'down',
        'exec',
        'images',
        'kill',
        'logs',
        'pause',
        'ps',
        'pull',
        'push',
        'restart',
        'rm',
        'run',
        'start',
        'stop',
        'top',
        'unpause',
        'up',
        'version',
    ]

    EXPERIMENTAL_COMMANDS: List[str] = [
        'attach',
        'cp',
        'ls',
        'scale',
        'wait',
        'watch',
    ]

    def __init__(
        self,
        config: Dict[str, Any],
        use_dummy: bool = False,
        state_file: Optional[str] = None,
    ) -> None:
        """Initialize Apple Container extension.

        Args:
            config: Configuration dict from .sugar.yaml
            use_dummy: Use dummy interface for testing
            state_file: Path to state file for dummy interface
        """
        self.config: Dict[str, Any] = config
        self.use_dummy: bool = use_dummy
        self.state_file: str = state_file or 'apple_container_state.json'
        self._runtime: Any = None

        if use_dummy:
            from sugar.extensions.apple_container_dummy import (
                AppleContainerDummy,
            )

            self._runtime = AppleContainerDummy(self.state_file)

    @property
    def runtime(self) -> Any:
        """Get the runtime instance."""
        return self._runtime

    def _execute_command(
        self, command: str, services: Optional[List[str]] = None
    ) -> int:
        """Execute a command through the container runtime.

        Args:
            command: Command name (e.g., 'build', 'up', 'down')
            services: List of service names (optional)

        Returns
        -------
            Return code (0 for success)
        """
        if self.use_dummy:
            return self._dummy_execute(command, services)
        return self._real_execute(command, services)

    def _handle_create(self, services: Optional[List[str]]) -> None:
        """Handle create command."""
        if services:
            for service in services:
                self.runtime.create(service, f'image-{service}')

    def _handle_start(self, services: Optional[List[str]]) -> None:
        """Handle start command."""
        if services:
            for service in services:
                self.runtime.start(service)

    def _handle_stop(self, services: Optional[List[str]]) -> None:
        """Handle stop command."""
        if services:
            for service in services:
                self.runtime.stop(service)

    def _handle_ps(self) -> None:
        """Handle ps command."""
        containers = self.runtime.get_containers()
        if containers:
            print('CONTAINER ID\tIMAGE\t\tSTATUS')
            for name, info in containers.items():
                print(f'{name[:12]}\t{info["image"]}\t{info["status"]}')

    def _handle_down(self) -> None:
        """Handle down command."""
        for name in list(self.runtime.get_containers().keys()):
            self.runtime.remove(name)

    def _dummy_execute(
        self, command: str, services: Optional[List[str]] = None
    ) -> int:
        """Execute command using dummy interface."""
        try:
            if command == 'create':
                self._handle_create(services)
            elif command == 'start':
                self._handle_start(services)
            elif command == 'stop':
                self._handle_stop(services)
            elif command == 'ps':
                self._handle_ps()
            elif command == 'down':
                self._handle_down()
            return 0
        except Exception as e:
            print(f'Error executing {command}: {e}', file=sys.stderr)
            return 1

    def _real_execute(
        self, command: str, services: Optional[List[str]] = None
    ) -> int:
        """Execute command using real Apple Container CLI."""
        args: List[str] = ['container', command]

        if services:
            args.extend(services)

        try:
            result = subprocess.run(args, check=False)  # nosec
            return result.returncode
        except FileNotFoundError:
            print(
                "Error: 'container' command not found. "
                'Please ensure Apple Container is installed.',
                file=sys.stderr,
            )
            return 1
        except Exception as e:
            print(f'Error executing {command}: {e}', file=sys.stderr)
            return 1

    def build(self, services: Optional[List[str]] = None) -> int:
        """Build services."""
        return self._execute_command('build', services)

    def config(self, services: Optional[List[str]] = None) -> int:
        """Show compose configuration."""
        return self._execute_command('config', services)

    def create(self, services: Optional[List[str]] = None) -> int:
        """Create services."""
        return self._execute_command('create', services)

    def down(self, services: Optional[List[str]] = None) -> int:
        """Stop and remove containers."""
        return self._execute_command('down', services)

    def exec(self, service: str, command: str) -> int:
        """Execute command in service."""
        return self._execute_command('exec', [service])

    def images(self, services: Optional[List[str]] = None) -> int:
        """List images."""
        return self._execute_command('images', services)

    def kill(self, services: Optional[List[str]] = None) -> int:
        """Kill containers."""
        return self._execute_command('kill', services)

    def logs(self, services: Optional[List[str]] = None) -> int:
        """View logs."""
        return self._execute_command('logs', services)

    def pause(self, services: Optional[List[str]] = None) -> int:
        """Pause services."""
        return self._execute_command('pause', services)

    def ps(self, services: Optional[List[str]] = None) -> int:
        """List containers."""
        return self._execute_command('ps', services)

    def pull(self, services: Optional[List[str]] = None) -> int:
        """Pull images."""
        return self._execute_command('pull', services)

    def push(self, services: Optional[List[str]] = None) -> int:
        """Push images."""
        return self._execute_command('push', services)

    def restart(self, services: Optional[List[str]] = None) -> int:
        """Restart services."""
        result = self._execute_command('stop', services)
        if result != 0:
            return result
        return self._execute_command('start', services)

    def rm(self, services: Optional[List[str]] = None) -> int:
        """Remove containers."""
        return self._execute_command('rm', services)

    def run(self, services: Optional[List[str]] = None) -> int:
        """Run one-off command."""
        return self._execute_command('run', services)

    def start(self, services: Optional[List[str]] = None) -> int:
        """Start services."""
        return self._execute_command('start', services)

    def stop(self, services: Optional[List[str]] = None) -> int:
        """Stop services."""
        return self._execute_command('stop', services)

    def top(self, services: Optional[List[str]] = None) -> int:
        """Display running processes."""
        return self._execute_command('top', services)

    def unpause(self, services: Optional[List[str]] = None) -> int:
        """Unpause services."""
        return self._execute_command('unpause', services)

    def up(self, services: Optional[List[str]] = None) -> int:
        """Create and start containers."""
        return self._execute_command('up', services)

    def version(self) -> int:
        """Show version."""
        return self._execute_command('version')
