import ctypes
from multiprocessing.pool import ThreadPool


class UnitSync:

    def __init__(self, libunitsync_path):
        self.so = ctypes.CDLL(libunitsync_path)
        self.init = self.so.Init(0, 0)
        self.write_dir = self.so.GetWritableDataDirectory()

    def startHeshThread(self, map_path, mod_hesh):
        self.pool = ThreadPool(processes=1)
        self.async_result = self.pool.apply_async(
            self.getHesh, (map_path, mod_hesh))

    def getResult(self):
        return self.async_result.get()

    def getHesh(self, map_path, mod_hesh):
        unit_sync = {
            'mapHesh': self.so.GetMapChecksumFromName(map_path.encode()),
            'modHesh': self.so.GetPrimaryModChecksumFromName(mod_hesh.encode()),
        }
        return unit_sync
