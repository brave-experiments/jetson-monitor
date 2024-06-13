from abc import ABC, abstractmethod

class JetsonDispatcher(ABC):

    @abstractmethod
    def get_temps(self, subsystems):
        pass

    @abstractmethod
    def get_power_figs(self, subsystems):
        pass