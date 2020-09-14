from abc import ABC, abstractmethod

class RoutingMessage(ABC):

    def __init__(self, fmt):
        self.fmt = fmt

    @abstractmethod
    def serialize(self, data: dict) -> bytearray:
        '''
        Implement this for a conversion from dictionary to bytearray
        :param data: Dictionary with keys and corresponding values
        :return: Bytearray
        '''
        pass

    @abstractmethod
    def deserialize(self, data: bytearray) -> dict:
        '''
        Implement this to convert a bytearray back to dictionary
        :param data:
        :return:
        '''
        pass

    @abstractmethod
    def length(self) -> int:
        '''
        Returns the (assumed) length of the message.
        :return: Length (int)
        '''
        pass