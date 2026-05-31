"""sample — WhatsApp Sales SaaS SDK.

Public entrypoints:
    Client  — high-level facade (manager + router + supervisor wired)
    TenantManager     — sync CRUD + SOUL rendering
    TenantRouter      — resolve(phone_number_id) → Tenant
    TenantSupervisor  — bring_up / bring_down / health
    SoulBuilder       — render a tenant's behavioral prompt (SOUL.md)
    SkillRegistry     — discover and invoke sales skills
    GoalJudge         — deterministic goal evaluation
"""

from __future__ import annotations

from sample.agent.loop import AgentLoop, AgentTurn
from sample.agent.soul import SoulBuilder, SoulConfig
from sample.client import Client, buyer_id_for
from sample.events import Event, EventBusPort, EventHandler, InMemoryEventBus
from sample.goal import Goal, GoalJudge, GoalResult, GoalStatus, GoalType
from sample.ingestion import (
    CsvExtractor,
    DocxExtractor,
    ExtractedChunk,
    ExtractorPort,
    HindsightPort,
    InMemoryHindsight,
    MockAudioExtractor,
    MockImageExtractor,
    MockVideoExtractor,
    PdfExtractor,
    PostgresHindsight,
    Preprocessor,
    UnsupportedFormatError,
)
from sample.llm import (
    EchoLLM,
    LLMError,
    LLMMessage,
    LLMPort,
    LLMReply,
    OpenRouterLLM,
    ScriptedLLM,
)
from sample.memory import (
    BuyerInteraction,
    BuyerMemoryPort,
    HonchoBuyerMemory,
    InMemoryBuyerMemory,
)
from sample.models import Fact, InboundMessage, Tenant, TenantStatus
from sample.onboarding import (
    MetaSignupPayload,
    OnboardingError,
    OnboardingFlow,
    OnboardingResult,
    slugify,
)
from sample.security import (
    CryptoError,
    SecretRedactingFilter,
    TokenCipher,
    generate_key,
    install_redaction,
    redact,
)
from sample.skills import (
    CatalogLookupSkill,
    LeadQualifierSkill,
    SalesCloserSkill,
    SkillBase,
    SkillRegistry,
    SkillResult,
)
from sample.tenant import (
    InMemoryTenantRepository,
    InMemoryTenantSpawner,
    TenantHealth,
    TenantManager,
    TenantRepositoryPort,
    TenantRouter,
    TenantSpawner,
    TenantSupervisor,
    UnknownTenantError,
)
from sample.whatsapp import (
    GatewayError,
    InMemoryGateway,
    KapsoGateway,
    OutboundMessage,
    WhatsAppGatewayPort,
)

__all__ = [
    "AgentLoop",
    "AgentTurn",
    "buyer_id_for",
    "BuyerInteraction",
    "BuyerMemoryPort",
    "CatalogLookupSkill",
    "Client",
    "CryptoError",
    "CsvExtractor",
    "DocxExtractor",
    "EchoLLM",
    "Event",
    "EventBusPort",
    "EventHandler",
    "ExtractedChunk",
    "ExtractorPort",
    "Fact",
    "GatewayError",
    "generate_key",
    "Goal",
    "GoalJudge",
    "GoalResult",
    "GoalStatus",
    "GoalType",
    "HindsightPort",
    "HonchoBuyerMemory",
    "InboundMessage",
    "InMemoryBuyerMemory",
    "InMemoryEventBus",
    "InMemoryGateway",
    "InMemoryHindsight",
    "InMemoryTenantRepository",
    "InMemoryTenantSpawner",
    "install_redaction",
    "KapsoGateway",
    "LeadQualifierSkill",
    "LLMError",
    "LLMMessage",
    "LLMPort",
    "LLMReply",
    "MetaSignupPayload",
    "MockAudioExtractor",
    "MockImageExtractor",
    "MockVideoExtractor",
    "OnboardingError",
    "OnboardingFlow",
    "OnboardingResult",
    "OpenRouterLLM",
    "OutboundMessage",
    "PdfExtractor",
    "PostgresHindsight",
    "Preprocessor",
    "redact",
    "SalesCloserSkill",
    "ScriptedLLM",
    "SecretRedactingFilter",
    "SkillBase",
    "SkillRegistry",
    "SkillResult",
    "SoulBuilder",
    "SoulConfig",
    "Tenant",
    "TenantHealth",
    "TenantManager",
    "TenantRepositoryPort",
    "TenantRouter",
    "TenantSpawner",
    "TenantStatus",
    "TenantSupervisor",
    "TokenCipher",
    "UnknownTenantError",
    "UnsupportedFormatError",
    "WhatsAppGatewayPort",
]

__version__ = "0.10.0"
