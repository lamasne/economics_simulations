import abc
from abc import ABC, abstractmethod


class EA(ABC):
    # @abc.abstractproperty
    # def money(self):
    #     pass

    @abstractmethod
    def place_order(self):
        pass
