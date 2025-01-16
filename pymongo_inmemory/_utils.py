from collections import namedtuple
import logging
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
