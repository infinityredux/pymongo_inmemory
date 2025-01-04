import hashlib
import logging
import os
import platform
from configparser import ConfigParser
from typing import Any, Optional, Type, TypeVar

from ._utils import mkdir_if_not_exist, make_semver
from .downloader._urls import best_url

DEFAULT_CONF = {}
CACHE_FOLDER = os.path.join(os.path.dirname(__file__), "..", ".cache")

logger = logging.getLogger("PYMONGOIM_UTILS")
CoerceType = TypeVar("CoerceType", str, int, float, bool)


class OperatingSystemNotFound(ValueError):
    pass


def _coercion(
        constructor: Type[CoerceType],
        value: Any,
) -> CoerceType:
    if constructor == bool:
        return value == "True"
    else:
        return constructor(value)


def _check_environment_vars(
        option: str,
        fallback: Optional[CoerceType] = None,
) -> Optional[CoerceType]:
    """ Check if `option` is defined in environment variables. """
    return os.environ.get("PYMONGOIM__{}".format(str(option).upper()), default=fallback)


def _check_cfg(
        option: str,
        filename: str,
        fallback: Optional[CoerceType] = None,
) -> Optional[CoerceType]:
    """ Check if `option` is defined in `filename` ini file in the root folder. """
    parser = ConfigParser()
    parser.read(filename)
    return parser.get("pymongo_inmemory", option, fallback=fallback, raw=True)


def conf(
        option: str,
        fallback: Optional[CoerceType] = None,
        optional: bool = True,
        coerce_with: Type[CoerceType] = str
) -> Optional[CoerceType]:
    """
    Retrieve asked `option` if possible. There are number of places that are
    checked. In the order of precedence:
    1. Environment variables
    2. setup.cfg in the root folder
    3. pymongo_inmemory.ini in the root folder
    4. `DEFAULT_CONF`

    Root folder is where the Python interpreter is invoked.

    Environment variables should be prefixed with `PYMONGOIM__`. For instance,
    `PYMONGOIM__DOWNLOAD_FOLDER`.
    """
    value = _check_environment_vars(
        option,
        fallback=_check_cfg(
            option,
            "setup.cfg",
            fallback=_check_cfg(
                option,
                "pymongo_inmemory.ini",
                fallback=DEFAULT_CONF.get(option, fallback),
            ),
        ),
    )

    if value is None:
        if not optional:
            raise ValueError(
                (
                    "Can't determine the value of {} "
                    "and it is not an optional parameter."
                ).format(option)
            )
    else:
        try:
            value = _coercion(coerce_with, value)
        except ValueError:
            value = None
        except Exception:
            raise ValueError(
                "Can't coerce the value of {} to type {}".format(
                    option, coerce_with.__qualname__
                )
            )

    logger.debug("Value for {}=={}".format(option, value))

    return value


class Context:
    def __init__(
            self,
            os_name: str | None = None,
            version=None,
            os_ver=None,
            ignore_cache: bool = False,
    ) -> None:
        self.mongo_version: str | None = conf("mongo_version", version)
        self.mongod_port: int | None = conf("mongod_port", None, coerce_with=int)
        self.mongod_data_folder: str | None = conf("mongod_data_folder", None)
        self.dbname: str = conf("dbname", "pim_test")
        self.mongo_client_host: str | None = conf("mongo_client_host", None)
        self.operating_system: str = self._collect_operating_system_name(os_name)
        self.os_version: str | None = conf("os_version", os_ver)
        self.ignore_cache: bool = conf("ignore_cache", ignore_cache, coerce_with=bool)
        self.use_local_mongod: bool = conf("use_local_mongod", False, coerce_with=bool)
        self.replica_set: str | None = conf("replica_set", None)

        # Handle allowing override via download url, but if present it does mean
        # we cannot guarantee the version number. Overriding this default also
        # means the user will need to specify either version or storage engine
        # (since this will depend on the version.)
        temp_url, temp_version = best_url(
            self.operating_system,
            version=self.mongo_version,
            os_ver=self.os_version,
        )
        self.download_url = conf("download_url", temp_url)
        self.downloaded_version = temp_version if self.download_url == temp_url else self.mongo_version
        self.storage_engine = self._select_storage_engine()

        url_hash = hashlib.sha256(bytes(self.download_url, "utf-8")).hexdigest()
        download_root_folder = conf("download_folder", "download")
        extract_root_folder = conf("extract_folder", "extract")
        self.download_folder = mkdir_if_not_exist(CACHE_FOLDER, download_root_folder, url_hash)
        self.extract_folder = mkdir_if_not_exist(CACHE_FOLDER, extract_root_folder, url_hash)

    def __str__(self):
        return (
            f"Mongo Version {self.mongo_version}\n"
            f"MongoD Port {self.mongod_port}\n"
            f"MongoD Data Folder {self.mongod_data_folder}\n"
            f"Database Name {self.dbname}\n"
            f"Replica Set {self.replica_set}\n"
            f"OS Name {self.operating_system}\n"
            f"OS Version {self.os_version}\n"
            f"Download URL {self.download_url}\n"
            f"Download Version {self.downloaded_version}\n"
            f"Ignore Cache {self.ignore_cache}\n"
            f"Use Local MongoD {self.use_local_mongod}\n"
            f"Download Folder {self.download_folder}\n"
            f"Extract Folder {self.extract_folder}\n"
            f"Storage engine {self.storage_engine}\n"
        )

    @staticmethod
    def _collect_operating_system_name(os_name: str | None = None) -> str:
        os_name = conf("operating_system", os_name)
        if os_name is None:
            # Fix for using platform.system() returning 'linux'
            platform_uname = platform.uname().version.lower()
            is_ubuntu = 'ubuntu' in platform_uname
            is_debian = 'debian' in platform_uname
            if is_ubuntu:
                system = 'ubuntu'
            elif is_debian:
                system = 'debian'
            else:
                system = platform.system()

            _mapping = {
                "Darwin": "osx",
                'debian': 'debian',
                "Linux": "linux",
                'ubuntu': 'ubuntu',
                "Windows": "windows",
            }
            os_name = _mapping.get(system, None)
            if os_name is None:
                raise OperatingSystemNotFound("Can't determine operating system.")
        return os_name

    def _select_storage_engine(self) -> str:
        if self.downloaded_version is None:
            storage_engine_fallback = None
        else:
            major, minor, patch = make_semver(self.downloaded_version)
            storage_engine_fallback = "wiredTiger" if major > 6 else "ephemeralForTest"
        result = conf("storage_engine", storage_engine_fallback)
        if result is None:
            ValueError("Download version could not be determined and no storage engine was specified.")
        return result
