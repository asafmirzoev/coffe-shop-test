"""
The module contains ‘services’ for processing the business logic of the request
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.container import Container


# Base parent class of services
class BaseService:
    def __init__(self, container: type['Container']):
        self.container = container
