"""Apple Container CLI Dummy Interface.

Simulates Apple Container CLI for testing on non-Mac systems.
"""

import json
import os

from datetime import datetime
from typing import Any, Dict, Optional, cast


class AppleContainerDummy:
    """Dummy interface that simulates Apple Container CLI.

    Stores state in a JSON file for testing on Linux/CI systems.
    This allows development and testing without requiring macOS hardware.
    """

    def __init__(self, state_file: str = 'apple_container_state.json') -> None:
        """Initialize the dummy Apple Container interface.

        Args:
            state_file: Path to JSON file for storing state
        """
        self.state_file = state_file
        self.state: Dict[str, Any] = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load state from JSON file or initialize empty state."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file) as f:
                    return cast(Dict[str, Any], json.load(f))
            except (json.JSONDecodeError, IOError):
                return self._empty_state()
        return self._empty_state()

    @staticmethod
    def _empty_state() -> Dict[str, Any]:
        """Return empty state structure."""
        return {'containers': {}, 'images': {}, 'networks': {}, 'volumes': {}}

    def _save_state(self) -> None:
        """Save current state to JSON file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except IOError as e:
            raise RuntimeError(f'Failed to save state: {e}')

    def create(self, name: str, image: str, **kwargs: Any) -> bool:
        """Create a container.

        Args:
            name: Container name
            image: Image name
            **kwargs: Additional container configuration

        Returns
        -------
            True if created successfully, False if already exists
        """
        if name in self.state['containers']:
            return False

        self.state['containers'][name] = {
            'image': image,
            'status': 'created',
            'created_at': datetime.now().isoformat(),
            'config': kwargs,
        }
        self._save_state()
        return True

    def start(self, name: str) -> bool:
        """Start a container.

        Args:
            name: Container name

        Returns
        -------
            True if started successfully, False if not found
        """
        if name not in self.state['containers']:
            return False

        self.state['containers'][name]['status'] = 'running'
        self.state['containers'][name]['started_at'] = (
            datetime.now().isoformat()
        )
        self._save_state()
        return True

    def stop(self, name: str) -> bool:
        """Stop a container.

        Args:
            name: Container name

        Returns
        -------
            True if stopped successfully, False if not found
        """
        if name not in self.state['containers']:
            return False

        self.state['containers'][name]['status'] = 'stopped'
        self.state['containers'][name]['stopped_at'] = (
            datetime.now().isoformat()
        )
        self._save_state()
        return True

    def remove(self, name: str) -> bool:
        """Remove a container.

        Args:
            name: Container name

        Returns
        -------
            True if removed successfully, False if not found
        """
        if name not in self.state['containers']:
            return False

        del self.state['containers'][name]
        self._save_state()
        return True

    def pause(self, name: str) -> bool:
        """Pause a running container.

        Args:
            name: Container name

        Returns
        -------
            True if paused successfully, False if not found
        """
        if name not in self.state['containers']:
            return False

        self.state['containers'][name]['status'] = 'paused'
        self._save_state()
        return True

    def unpause(self, name: str) -> bool:
        """Unpause a paused container.

        Args:
            name: Container name

        Returns
        -------
            True if unpaused successfully, False if not found
        """
        if name not in self.state['containers']:
            return False

        self.state['containers'][name]['status'] = 'running'
        self._save_state()
        return True

    def get_containers(self) -> Dict[str, Any]:
        """Get all containers.

        Returns
        -------
            Dictionary of all containers
        """
        containers: Dict[str, Any] = self.state['containers'].copy()
        return containers

    def get_container(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific container.

        Args:
            name: Container name

        Returns
        -------
            Container info if found, None otherwise
        """
        container_data = self.state['containers'].get(name)
        if container_data is not None and isinstance(container_data, dict):
            return cast(Dict[str, Any], container_data)
        return None

    def clean(self) -> None:
        """Reset all state. Useful for testing."""
        self.state = self._empty_state()
        self._save_state()
