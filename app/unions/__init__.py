"""
Module includes classes for merging database and cache repositories
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.container import Container


class BaseUnion:
    def __init__(self, container: type['Container']):
        self.container = container
