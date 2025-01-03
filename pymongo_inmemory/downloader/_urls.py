from collections import namedtuple
import logging
from typing import Generator

from .._utils import make_semver
from ._patterns import URLS


logger = logging.getLogger("PYMONGOIM_DOWNLOAD_URL")

ExpandedURL = namedtuple(
    "ExpandedURL", ["os_name", "os_version", "version", "url", "major_minor"]
)


class OperatingSystemNameNotFound(ValueError):
    pass


class OperatingSystemVersionNotFound(ValueError):
    pass


def best_url(
        os_name,
        version: str | None = None,
        os_ver: str | None = None,
        url_tree: dict[str, dict] | None = None,
):
    if url_tree is None:
        url_tree = URLS

    try:
        os_branch = url_tree[str(os_name).lower()]
    except KeyError:
        raise OperatingSystemNameNotFound(
            f"Can't find a MongoDB for this OS: {os_name}"
        )

    if os_ver is None:
        os_ver = max(os_branch.keys())
    else:
        os_ver = str(os_ver).lower()

    os_ver = str(os_ver)
    if os_ver not in os_branch.keys():
        raise OperatingSystemVersionNotFound(
            f"Can't find a MongoDB for OS {os_name} version {os_ver}, "
            f"available OS versions: {os_branch.keys()}"
        )

    version_branch = os_branch[os_ver]

    major, minor, patch = make_semver(version)
    if major not in version_branch.keys():
        major = max(version_branch.keys())
        minor = max(version_branch[major].keys())
        patch = max(version_branch[major][minor]["patches"])
    elif minor not in version_branch[major].keys():
        minor = max(version_branch[major].keys())
        patch = max(version_branch[major][minor]["patches"])
    elif patch not in version_branch[major][minor]["patches"]:
        patch = max(version_branch[major][minor]["patches"])

    found_version = f"{major}.{minor}.{patch}"
    logger.info(f"Requested MongoDB version {version}, found version: {found_version}")
    return version_branch[major][minor]["url"].format(found_version), found_version


def expand_url_tree(tree) -> Generator[ExpandedURL, None, None]:
    for os_name, os_leaf in tree.items():
        for os_version, version_leaf in os_leaf.items():
            for major, major_leaf in version_leaf.items():
                for minor, minor_leaf in major_leaf.items():
                    for patch in minor_leaf["patches"]:
                        version = "{}.{}.{}".format(major, minor, patch)
                        major_minor = "{}.{}".format(major, minor)
                        yield ExpandedURL(
                            os_name,
                            os_version,
                            version,
                            minor_leaf["url"].format(version),
                            major_minor,
                        )
