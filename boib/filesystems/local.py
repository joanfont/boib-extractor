import aiofiles
from aiofiles import os as aios
import os

from boib.filesystems import Filesystem


class LocalFilesystem(Filesystem):

    def __init__(self, base_dir: str):
        self.__base_dir = base_dir
    
    async def write(self, path: str, bytes: bytes):
        full_path =  os.path.join(self.__base_dir, path)
        await aios.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        async with aiofiles.open(full_path, 'wb') as f:
            await f.write(bytes)
