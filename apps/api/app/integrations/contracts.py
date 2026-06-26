from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class IntegrationCapability:
    id: str
    name: str
    status: str
    live: bool
    provider: str
    description: str
    data_flow: list[str]
    safeguards: list[str]
    endpoints: list[str]
    next_steps: list[str]

    def to_dict(self):
        return asdict(self)


def coming_soon_capability(id: str, name: str, provider: str, description: str, data_flow: list[str], safeguards: list[str], endpoints: list[str], next_steps: list[str]) -> IntegrationCapability:
    return IntegrationCapability(
        id=id,
        name=name,
        status='coming_soon',
        live=False,
        provider=provider,
        description=description,
        data_flow=data_flow,
        safeguards=safeguards,
        endpoints=endpoints,
        next_steps=next_steps,
    )
