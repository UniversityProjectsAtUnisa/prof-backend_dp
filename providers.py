from typing import List, Optional
from asgi_babel import re
from frozendict import frozendict

service = frozendict()

PROVIDERS = frozendict(
    {"wikipedia": service.copy(), "scholarpedia": service.copy()})


def is_valid_provider(requested_provider: Optional[str]) -> List[str]:
    return requested_provider in PROVIDERS
