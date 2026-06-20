"""adapters/registry.py — picks the right adapter for a URL."""
import logging
from typing import Optional
from adapters.base.base_adapter import BaseAdapter
from adapters.greenhouse.greenhouse_adapter import GreenhouseAdapter
from adapters.lever.lever_adapter import LeverAdapter
from adapters.workday.workday_adapter import WorkdayAdapter
from adapters.ashby.ashby_adapter import AshbyAdapter

log = logging.getLogger(__name__)

_ADAPTERS = [GreenhouseAdapter(), LeverAdapter(), WorkdayAdapter(), AshbyAdapter()]


def get_adapter(url: str) -> Optional[BaseAdapter]:
    for adapter in _ADAPTERS:
        if adapter.matches(url):
            return adapter
    return None
