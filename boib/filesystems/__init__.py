from abc import ABC, abstractmethod


class Filesystem:

    @abstractmethod
    async def write(self, path: str, bytes: bytes):
        pass
