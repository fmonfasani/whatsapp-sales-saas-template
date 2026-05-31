"""Tenant subsystem: repository, spawner, router, supervisor, manager."""

from __future__ import annotations

from sample.tenant.manager import TenantManager
from sample.tenant.repository import InMemoryTenantRepository, TenantRepositoryPort
from sample.tenant.router import TenantRouter, UnknownTenantError
from sample.tenant.spawner import InMemoryTenantSpawner, TenantSpawner
from sample.tenant.supervisor import TenantHealth, TenantSupervisor

__all__ = [
    "InMemoryTenantRepository",
    "InMemoryTenantSpawner",
    "TenantHealth",
    "TenantManager",
    "TenantRepositoryPort",
    "TenantRouter",
    "TenantSpawner",
    "TenantSupervisor",
    "UnknownTenantError",
]
