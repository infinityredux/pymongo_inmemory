import pymongo

from .mongod import Mongod
from .context import Context


class MongoClient(pymongo.MongoClient):
    def __init__(
            self,
            host: str | None = None,
            port: int | None = None,
            *,
            port_offset: int = 0,
            **kwargs
    ):
        self._pim_context: Context = Context(port_offset=port_offset)
        if port is not None:
            self._pim_context.mongod_port = port
        if host is not None:
            self._pim_context.mongo_client_host = host
        self._mongod = Mongod(self._pim_context)
        self._mongod.start()
        super().__init__(self._mongod.connection_string, **kwargs)

    def close(self):
        super().close()
        self._mongod.stop()

    def pim_mongodump(self, *args, **kwargs):
        return self._mongod.mongodump(*args, **kwargs)


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    m = MongoClient("mongodb://127.0.0.1/something", 27017)
    m.close()
