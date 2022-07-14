import abc
from abc import ABC, abstractmethod


class EA(ABC):
    # @abc.abstractproperty
    # def money(self):
    #     pass

    @abstractmethod
    def exchange_money(price):
        pass
