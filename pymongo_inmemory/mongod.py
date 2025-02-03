"""MongoDB daemon process wrapper

This module can be used for spinning up an ephemeral MongoDB instance:
::
    python -m python_inmemory.mongod
"""
import atexit
import logging
import os
import signal
import subprocess
import time
import threading
from tempfile import TemporaryDirectory

import pymongo

from ._utils import extract_server_config_from_connection_string, find_open_port
from .downloader import download
from .context import Context

logger = logging.getLogger("PYMONGOIM_MONGOD")
# Holds references to open Popen objects which spawn MongoDB daemons.
_popen_objs = []


@atexit.register
def cleanup():
    logger.info("Cleaning created processes.")
    for o in _popen_objs:
        if o.poll() is None:
            logger.debug("Found {}".format(o.pid))
            o.terminate()


def clean_before_kill(signum, stack):
    logger.warning("Received kill signal.")
    cleanup()
    exit()


# as per https://docs.python.org/3.6/library/signal.html#signals-and-threads
# only the main thread is allowed to set a new signal handler.
# This means that if this module is imported by a thread other than the
# main one it will raise an error.
if threading.current_thread() is threading.main_thread():
    signal.signal(signal.SIGTERM, clean_before_kill)


class MongodConfig:
    def __init__(self, pim_context: Context):
        self._context = pim_context
        self.local_address = "127.0.0.1"
        self.engine = pim_context.storage_engine

    @property
    def port(self) -> str | None:
        set_port = self._context.mongod_port
        offset = self._context.mongod_port_offset
        if set_port is None:
            return str(find_open_port(range(27017, 28000)) + offset)
        else:
            return str(set_port + offset)

    @property
    def replica_set(self) -> str | None:
        return self._context.replica_set

    @property
    def direct_connection_string(self) -> str | None:
        host = self.local_address
        if self._context.mongo_client_host is not None:
            if self._context.mongo_client_host.startswith("mongodb://"):
                return self._context.mongo_client_host
            else:
                host = self._context.mongo_client_host

        port = self.port  # Make sure it only runs once
        if host is not None and port is not None:
            url = f"mongodb://{host}:{port}"
            if self._context.dbname is not None:
                url += f"/{self._context.dbname}"
            return url

    @property
    def connection_string(self) -> str | None:
        direct = self.direct_connection_string
        if direct is None or self._context.replica_set is None:
            return direct
        return f"{direct}?replicaSet={self._context.replica_set}"


class Mongod:
    """Wrapper for MongoDB daemon instance. Can be used with context managers.
    During construction it calls `download` function of `downloader` to get the
    defined MongoDB version.

    Daemon is managed by `subprocess.Popen`. all Popen objects are registered
    with `atexit` module to ensure clean up.
    """

    def __init__(self, context: Context | None):
        if context is None:
            context = Context()
        logger.info("Running MongoD in the following context")
        logger.info(context)

        logger.info("Checking binary")
        if context.use_local_mongod:
            logger.warning("Using local mongod instance")
            self._bin_folder = ""
        else:
            self._bin_folder = download(context)

        self.config: MongodConfig = MongodConfig(context)
        self.connection_string: str | None = self.config.connection_string

        self._proc = None
        self._connection_string: str | None = None
        self._temp_data_folder = TemporaryDirectory(prefix="pymongoim")
        self._using_tmp_folder = context.mongod_data_folder is None
        self._client = pymongo.MongoClient(self.connection_string)

        self.data_folder: str = self._temp_data_folder.name if self._using_tmp_folder else context.mongod_data_folder
        self.log_path = os.path.join(self.data_folder, "mongod.log")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

    def start(self):
        self._check_lock()

        logger.info("Starting mongod with {cs}...".format(cs=self.connection_string))
        boot_command: list[str] = [
            os.path.join(self._bin_folder, "mongod"),
            "--dbpath",
            self.data_folder,
            "--logpath",
            self.log_path,
            "--port",
            self.config.port,
            "--bind_ip",
            self.config.local_address,
        ]
        if self.config.engine is not None:
            boot_command.append("--storageEngine")
            boot_command.append(self.config.engine)
        if self.config.replica_set is not None:
            boot_command.append("--replSet")
            boot_command.append(self.config.replica_set)

        logger.debug(boot_command)
        self._proc = subprocess.Popen(boot_command)
        _popen_objs.append(self._proc)

        # time.sleep(0.5)
        if self._proc.poll() is not None:
            raise RuntimeError(f"MongoDB process failed to start. Exit code: {self._proc.returncode}")

        max_retries = 20
        retry_interval = 0.5
        direct = self.config.direct_connection_string
        for attempt in range(max_retries):
            if self._proc.poll() is not None:
                raise RuntimeError(f"MongoDB process terminated unexpectedly. Exit code: {self._proc.returncode}")
            
            temp_client = pymongo.MongoClient(
                direct,
                serverSelectionTimeoutMS=500,
                connectTimeoutMS=500,
                directConnection=True
            )
            try:
                temp_client.admin.command('ping')
                logger.info("Server is available")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Server failed to start after {max_retries} attempts: {e}")
                    self.stop()
                    raise
                logger.info(f"Server not yet available (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_interval)
            finally:
                temp_client.close()

        if self.config.replica_set is not None:
            logger.info("Initializing replica set...")
            temp_client = pymongo.MongoClient(
                direct,
                serverSelectionTimeoutMS=2000,
                connectTimeoutMS=2000,
                directConnection=True
            )

            deconstructed = extract_server_config_from_connection_string(direct)
            try:
                config = {
                    '_id': self.config.replica_set,
                    'members': [{
                        '_id': 0,
                        'host': f"{deconstructed['host']}:{deconstructed['port']}",
                        'priority': 1
                    }]
                }
                temp_client.admin.command('replSetInitiate', config)
            except Exception as e:
                logger.error(f"Failed to configure replica set: {e}")
                self.stop()
                raise


        logger.info("Started mongod.")
        logger.info("Connect with: {cs}".format(cs=self.connection_string))

    def stop(self):
        logger.info("Sending kill signal to mongod.")
        self._proc.terminate()
        while self._proc.poll() is None:
            logger.debug("Waiting for MongoD shutdown.")
            time.sleep(1)
        self._clean_up()

    @property
    def is_locked(self):
        return os.path.exists(os.path.join(self.data_folder, "mongod.lock"))

    @property
    def is_healthy(self):
        db = self._client["admin"]
        status = db.command("serverStatus")
        try:
            logger.debug("Getting status")
            uptime = int(status["uptime"])
        except subprocess.CalledProcessError:
            logger.debug("Status: Not running")
            return False
        else:
            if uptime > 0:
                version = status["version"]
                logger.debug(
                    "Status: MongoDB {} running for {} secs".format(version, uptime)
                )
                return True
            else:
                logger.debug("Status: Just started.")
                return False

    def mongodump(self, database, collection):
        dump_command = [
            os.path.join(self._bin_folder, "mongodump"),
            "--host",
            self.config.local_address,
            "--port",
            self.config.port,
            "--out",
            "-",
            "--db",
            database,
            "--collection",
            collection,
        ]
        proc = subprocess.run(dump_command, stdout=subprocess.PIPE)
        return proc.stdout

    def logs(self):
        with open(self.log_path, "r") as logfile:
            return logfile.readlines()

    def _clean_up(self):
        if self._using_tmp_folder:
            self._temp_data_folder.cleanup()

    def _check_lock(self):
        while self.is_locked:
            if self._using_tmp_folder:
                raise RuntimeError(
                    (
                        "There is a lock file in the provided data folder. "
                        "Make sure that no other MongoDB is running."
                    )
                )
            logger.warning(
                (
                    "Lock file found, possibly another mock server is running. "
                    "Changing the data folder."
                )
            )
            self._temp_data_folder = TemporaryDirectory(prefix="pymongoim")


if __name__ == "__main__":
    # This part is used for integrity tests too.
    logging.basicConfig(level=logging.INFO)
    main_context = Context()
    with Mongod(main_context) as md:
        try:
            while True:
                pass
        except KeyboardInterrupt:
            pass
