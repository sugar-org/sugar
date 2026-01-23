"""Unit tests for Apple Container extension.

Tests the dummy interface and main extension class.
"""

import tempfile

from pathlib import Path
from typing import Generator

import pytest

from sugar.extensions.apple_container import AppleContainerExtension
from sugar.extensions.apple_container_dummy import AppleContainerDummy

CREATED_CONTAINERS = 2


class TestAppleContainerDummy:
    """Test the dummy interface."""

    @pytest.fixture
    def temp_state_file(self) -> Generator[str, None, None]:
        """Create temporary state file."""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            state_file = f.name
        yield state_file
        Path(state_file).unlink(missing_ok=True)

    @pytest.fixture
    def dummy(self, temp_state_file: str) -> AppleContainerDummy:
        """Create dummy instance."""
        return AppleContainerDummy(temp_state_file)

    def test_initialize(self, dummy: AppleContainerDummy) -> None:
        """Test dummy initialization."""
        assert dummy.state is not None
        assert 'containers' in dummy.state
        assert isinstance(dummy.state['containers'], dict)

    def test_create_container(self, dummy: AppleContainerDummy) -> None:
        """Test creating a container."""
        result = dummy.create('test-container', 'test-image')
        assert result is True
        assert 'test-container' in dummy.state['containers']
        assert (
            dummy.state['containers']['test-container']['image']
            == 'test-image'
        )

    def test_create_duplicate_container(
        self, dummy: AppleContainerDummy
    ) -> None:
        """Test creating a container that already exists."""
        dummy.create('test-container', 'test-image')
        result = dummy.create('test-container', 'test-image')
        assert result is False

    def test_start_container(self, dummy: AppleContainerDummy) -> None:
        """Test starting a container."""
        dummy.create('test-container', 'test-image')
        result = dummy.start('test-container')
        assert result is True
        assert (
            dummy.state['containers']['test-container']['status'] == 'running'
        )

    def test_start_nonexistent_container(
        self, dummy: AppleContainerDummy
    ) -> None:
        """Test starting a container that doesn't exist."""
        result = dummy.start('nonexistent')
        assert result is False

    def test_stop_container(self, dummy: AppleContainerDummy) -> None:
        """Test stopping a container."""
        dummy.create('test-container', 'test-image')
        dummy.start('test-container')
        result = dummy.stop('test-container')
        assert result is True
        assert (
            dummy.state['containers']['test-container']['status'] == 'stopped'
        )

    def test_pause_container(self, dummy: AppleContainerDummy) -> None:
        """Test pausing a running container."""
        dummy.create('test-container', 'test-image')
        dummy.start('test-container')
        result = dummy.pause('test-container')
        assert result is True
        assert (
            dummy.state['containers']['test-container']['status'] == 'paused'
        )

    def test_unpause_container(self, dummy: AppleContainerDummy) -> None:
        """Test unpausing a paused container."""
        dummy.create('test-container', 'test-image')
        dummy.start('test-container')
        dummy.pause('test-container')
        result = dummy.unpause('test-container')
        assert result is True
        assert (
            dummy.state['containers']['test-container']['status'] == 'running'
        )

    def test_remove_container(self, dummy: AppleContainerDummy) -> None:
        """Test removing a container."""
        dummy.create('test-container', 'test-image')
        result = dummy.remove('test-container')
        assert result is True
        assert 'test-container' not in dummy.state['containers']

    def test_remove_nonexistent_container(
        self, dummy: AppleContainerDummy
    ) -> None:
        """Test removing a container that doesn't exist."""
        result = dummy.remove('nonexistent')
        assert result is False

    def test_get_containers(self, dummy: AppleContainerDummy) -> None:
        """Test getting all containers."""
        dummy.create('container1', 'image1')
        dummy.create('container2', 'image2')
        containers = dummy.get_containers()
        assert len(containers) == CREATED_CONTAINERS
        assert 'container1' in containers
        assert 'container2' in containers

    def test_get_single_container(self, dummy: AppleContainerDummy) -> None:
        """Test getting a single container."""
        dummy.create('test-container', 'test-image')
        container = dummy.get_container('test-container')
        assert container is not None
        assert container['image'] == 'test-image'

    def test_get_nonexistent_container(
        self, dummy: AppleContainerDummy
    ) -> None:
        """Test getting a container that doesn't exist."""
        container = dummy.get_container('nonexistent')
        assert container is None

    def test_clean_state(self, dummy: AppleContainerDummy) -> None:
        """Test cleaning all state."""
        dummy.create('test-container', 'test-image')
        dummy.clean()
        assert len(dummy.state['containers']) == 0
        assert len(dummy.state['images']) == 0

    def test_state_persistence(self, temp_state_file: str) -> None:
        """Test state persists to file."""
        dummy1 = AppleContainerDummy(temp_state_file)
        dummy1.create('test-container', 'test-image')

        dummy2 = AppleContainerDummy(temp_state_file)
        assert 'test-container' in dummy2.state['containers']
        assert (
            dummy2.state['containers']['test-container']['image']
            == 'test-image'
        )


class TestAppleContainerExtension:
    """Test the main extension class."""

    @pytest.fixture
    def temp_state_file(self) -> Generator[str, None, None]:
        """Create temporary state file."""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            state_file = f.name
        yield state_file
        Path(state_file).unlink(missing_ok=True)

    @pytest.fixture
    def extension(self, temp_state_file: str) -> AppleContainerExtension:
        """Create extension instance with dummy."""
        return AppleContainerExtension(
            {}, use_dummy=True, state_file=temp_state_file
        )

    def test_initialize(self, extension: AppleContainerExtension) -> None:
        """Test extension initialization."""
        assert extension.use_dummy is True
        assert extension.runtime is not None

    def test_create(self, extension: AppleContainerExtension) -> None:
        """Test create command."""
        result = extension.create(['test-service'])
        assert result == 0

    def test_start(self, extension: AppleContainerExtension) -> None:
        """Test start command."""
        extension.create(['test-service'])
        result = extension.start(['test-service'])
        assert result == 0

    def test_stop(self, extension: AppleContainerExtension) -> None:
        """Test stop command."""
        extension.create(['test-service'])
        extension.start(['test-service'])
        result = extension.stop(['test-service'])
        assert result == 0

    def test_restart(self, extension: AppleContainerExtension) -> None:
        """Test restart command."""
        extension.create(['test-service'])
        extension.start(['test-service'])
        result = extension.restart(['test-service'])
        assert result == 0

    def test_down(self, extension: AppleContainerExtension) -> None:
        """Test down command."""
        extension.create(['test-service'])
        result = extension.down(['test-service'])
        assert result == 0

    def test_ps(self, extension: AppleContainerExtension) -> None:
        """Test ps command."""
        extension.create(['test-service'])
        result = extension.ps(['test-service'])
        assert result == 0

    def test_pause(self, extension: AppleContainerExtension) -> None:
        """Test pause command."""
        extension.create(['test-service'])
        extension.start(['test-service'])
        result = extension.pause(['test-service'])
        assert result == 0

    def test_unpause(self, extension: AppleContainerExtension) -> None:
        """Test unpause command."""
        extension.create(['test-service'])
        extension.start(['test-service'])
        extension.pause(['test-service'])
        result = extension.unpause(['test-service'])
        assert result == 0

    def test_down_specific_services(
        self, extension: AppleContainerExtension
    ) -> None:
        """Test down command with specific services."""
        extension.create(['service1', 'service2'])
        extension.start(['service1', 'service2'])
        result = extension.down(['service1'])
        assert result == 0
