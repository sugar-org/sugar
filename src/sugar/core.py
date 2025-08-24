"""Sugar class for containers."""

from __future__ import annotations

from typing import Optional, Type, cast

from sugar.extensions.base import SugarBase
from sugar.extensions.compose import SugarCompose
from sugar.extensions.compose_ext import SugarComposeExt
from sugar.extensions.podman_ext import SugarPodmanComposeExt
from sugar.extensions.swarm import (
    SugarSwarm,
    SugarSwarmNode,
    SugarSwarmService,
    SugarSwarmStack,
)
from sugar.extensions.tui import SugarTUI

try:
    from sugar.extensions.stats import SugarStats
except ImportError:
    # SugarStats is optional (extras=tui)
    SugarStats = cast(Optional[Type[SugarBase]], None)  # type: ignore


extensions: dict[str, Type[SugarBase]] = {
    'compose': SugarCompose,
    'compose-ext': SugarComposeExt,
    'podman-ext': SugarPodmanComposeExt,
    'swarm': SugarSwarm,
    'swarm:stack': SugarSwarmStack,
    'swarm:service': SugarSwarmService,
    'swarm:node': SugarSwarmNode,
    'tui': SugarTUI,
    **{'stats': SugarStats for i in range(1) if SugarStats is not None},
}
