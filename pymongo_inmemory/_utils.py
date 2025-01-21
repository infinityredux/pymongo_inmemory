from collections import namedtuple
import logging
import re
import socket
import os
from os import path

logger = logging.getLogger("PYMONGOIM_UTILS")

SemVer = namedtuple("SemVer", ["major", "minor", "patch"])


def find_open_port(sq):
    for port in sq:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
            if 0 != soc.connect_ex(("localhost", port)):
                return port


def make_semver(version: str | None = None) -> SemVer:
    if version is None:
        return SemVer(None, None, None)

    parts = [int(x) for x in version.split(".")]
    if len(parts) >= 3:
        major, minor, patch = parts[:3]
    elif len(parts) == 2:
        major, minor = parts
        patch = None
    elif len(parts) == 1:
        major = parts[0]
        minor = patch = None
    else:
        major = minor = patch = None

    return SemVer(major, minor, patch)


def compare_semver_greater(base: SemVer, compare: SemVer) -> bool:
    try:
        if compare.major is None or base.major > compare.major:
            return False
        elif base.major < compare.major:
            return True

        if compare.minor is None or base.minor > compare.minor:
            return False
        elif base.minor < compare.minor:
            return True

        if compare.patch is None or base.patch > compare.patch:
            return False
        elif base.patch < compare.patch:
            return True
    except TypeError:
        # TypeError: can't compare NoneType to int
        # Will only happy if the base value is None and compare is not
        return True
    # If we get here, then the base version and compare version are equal
    return False


def mkdir_if_not_exist(*folders):
    current_path = path.join(folders[0])
    if not path.isdir(current_path):
        os.mkdir(current_path)
    for x in folders[1:]:
        current_path = path.join(current_path, x)
        if not path.isdir(current_path):
            os.mkdir(current_path)
    return current_path


def extract_server_config_from_connection_string(connection_string: str) -> dict:
    # Regex to extract the server config from the connection string
    pattern = r"mongodb://(?:(?P<username>[^:@]+)(?::(?P<password>[^@]+))?@)?(?P<host>[^:/]+)(?::(?P<port>\d+))?(?:/(?P<database>[^?]+)?)?(?:\?(?P<options>.+))?"
    match = re.match(pattern, connection_string)
    
    if not match:
        raise ValueError("Could not parse connection string")
        
    # Extract matched groups
    config = {
        "username": match.group("username"),
        "password": match.group("password"), 
        "host": match.group("host"),
        "port": int(match.group("port")) if match.group("port") else None,
        "database": match.group("database"),
        "replica_set": None,
        "options": {}
    }

    # Parse options if present
    if match.group("options"):
        options = match.group("options").split("&")
        for opt in options:
            key, value = opt.split("=")
            if key == "replicaSet":
                config["replica_set"] = value
            else:
                config["options"][key] = value

    return config
