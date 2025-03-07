from abc import ABC, abstractmethod

from boib.models import Bulletin

class Downloader(ABC):

    @abstractmethod
    async def download(self, bulletin: Bulletin): 
        pass

