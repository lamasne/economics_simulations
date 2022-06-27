import abc
from abc import ABC, abstractmethod


class EA(ABC):
    # @abc.abstractproperty
    # def money(self):
    #     pass

    @abstractmethod
    def work(self):
        pass

    @abstractmethod
    def buy(self):
        pass

    @abstractmethod
    def sell(self):
        pass
