from abc import ABC, abstractmethod

class RoutingMessage(ABC):

    def __init__(self, fmt):
        self.fmt = fmt

    @abstractmethod
    def serialize(self, data: dict) -> bytearray:
        pass

    @abstractmethod
    def deserialize(self, data: bytearray) -> dict:
        pass

    @abstractmethod
    def length(self) -> int:
        pass