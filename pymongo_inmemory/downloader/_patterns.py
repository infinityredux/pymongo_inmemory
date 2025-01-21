PATTERNS = {
    "windows32-x86_64": "https://fastdl.mongodb.org/win32/mongodb-win32-x86_64-{}.zip",
    "windows-2008plus-ssl": "https://fastdl.mongodb.org/win32/mongodb-win32-x86_64-2008plus-ssl-{}.zip",  # noqa E501
    "windows-2012plus": "https://fastdl.mongodb.org/win32/mongodb-win32-x86_64-2012plus-{}.zip",  # noqa E501
    "windows-x86_64": "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-{}.zip",
    "sunos5": "https://fastdl.mongodb.org/sunos5/mongodb-sunos5-x86_64-{}.tgz",
    "osx": "https://fastdl.mongodb.org/osx/mongodb-osx-x86_64-{}.tgz",
    "osx-ssl": "https://fastdl.mongodb.org/osx/mongodb-osx-ssl-x86_64-{}.tgz",
    "macos": "https://fastdl.mongodb.org/osx/mongodb-macos-x86_64-{}.tgz",
    "macos-arm": "https://fastdl.mongodb.org/osx/mongodb-macos-arm64-{}.tgz",
    "linux": "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-{}.tgz",
    "ubuntu-arm-22": "https://fastdl.mongodb.org/linux/mongodb-linux-aarch64-ubuntu2204-{}.tgz",  # noqa E501
    "ubuntu22": "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu2204-{}.tgz",  # noqa E501
    "ubuntu-arm-20": "https://fastdl.mongodb.org/linux/mongodb-linux-aarch64-ubuntu2004-{}.tgz",  # noqa E501
    "ubuntu20": "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu2004-{}.tgz",  # noqa E501
    "ubuntu18": "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1804-{}.tgz",  # noqa E501
    "ubuntu16": "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1604-{}.tgz",  # noqa E501
    "ubuntu14": "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1404-{}.tgz",  # noqa E501
    "ubuntu12": "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1204-{}.tgz",  # noqa E501
    "suse15": "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-suse15-{}.tgz",
    "suse12": "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-suse12-{}.tgz",
    "suse11": "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-suse11-{}.tgz",
    "rhel9": "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-rhel90-{}.tgz",
    "rhel-arm-9": "https://fastdl.mongodb.org/linux/mongodb-linux-aarch64-rhel90-{}.tgz",
    "rhel8": "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-rhel80-{}.tgz",
    "rhel-arm-8": "https://fastdl.mongodb.org/linux/mongodb-linux-aarch64-rhel82-{}.tgz",
    "rhel7": "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-rhel70-{}.tgz",
    "rhel6": "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-rhel62-{}.tgz",
    "rhel5": "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-rhel55-{}.tgz",
    "debian11": "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-debian11-{}.tgz",
    "amazon2023": "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-amazon2023-{}.tgz",  # noqa E501
    "amazon2023-arm": "https://fastdl.mongodb.org/linux/mongodb-linux-aarch64-amazon2023-{}.tgz",  # noqa E501
    "amazon2": "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-amazon2-{}.tgz",
    "amazon1": "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-amazon-{}.tgz",
}


PATCH_RANGE = {
    # 5.0.30 released on 2024-10-24 
    "5.0": list(range(31)),
    "5.0-debian11": list(range(8, 31)),

    # 6.0.19 released on 2024-10-24, 6.0.20 currently "upcoming"
    # According to original comments:
    #   Version 6.0.5 is not suitable for production
    "6.0": list(range(5)) + list(range(6, 21)),
    "6.0-rhel9": list(range(4, 21)),
    "6.0-rhel-arm-9": list(range(7, 21)),

    # 7.0.16 released on 2024-12-20
    "7.0": list(range(0, 17)),
    # 12 errors
    # 13 gives 404 on download
    
    # 8.0.4 released on 2024-12-09
    "8.0": list(range(5)),
}


WARNING_RANGE = {
    # Version 5.x is now end of life
    # As per: https://www.mongodb.com/docs/v5.0/release-notes/5.0/
    "5.0": PATCH_RANGE["5.0"],
    "5.0-debian11": PATCH_RANGE["5.0-debian11"],

    # Version 6.0.14 and below have known critical issues
    # As per: https://www.mongodb.com/docs/manual/release-notes/6.0/
    "6.0": list(range(0, 15)),

    # Versions of 7.0.7 and below have known critical issues
    # As per: https://www.mongodb.com/docs/manual/release-notes/7.0/
    "7.0": list(range(0, 8)), 
}


# An index of URL patterns and patch ranges. First with OS and second with MongoDB
# version, because we are limited by the OS we are running on first, MongoDB
# version second.
URLS = {
    "amazon": {
        "1": {
            5: {
                0: {
                    "patches": PATCH_RANGE["5.0"],
                    "url": PATTERNS["amazon1"],
                }
            },
        },
        "2": {
            5: {
                0: {
                    "patches": PATCH_RANGE["5.0"],
                    "url": PATTERNS["amazon2"],
                },
            },
            6: {
                0: {
                    "patches": PATCH_RANGE["6.0"],
                    "url": PATTERNS["amazon2"],
                },
            },
            7: {
                0: {
                    "patches": PATCH_RANGE["7.0"],
                    "url": PATTERNS["amazon2"],
                },
            },
        },
        "2023": {
            7: {
                0: {
                    "patches": PATCH_RANGE["7.0"],
                    "url": PATTERNS["amazon2023"],
                },
            },
        },
        "2023-arm": {
            7: {
                0: {
                    "patches": PATCH_RANGE["7.0"],
                    "url": PATTERNS["amazon2023-arm"],
                },
            },
        },
    },
    "debian": {
        "11": {
            5: {
                0: {
                    "patches": PATCH_RANGE["5.0-debian11"],
                    "url": PATTERNS["debian11"],
                },
            },
            6: {
                0: {
                    "patches": PATCH_RANGE["6.0"],
                    "url": PATTERNS["debian11"],
                },
            },
            7: {
                0: {
                    "patches": PATCH_RANGE["7.0"],
                    "url": PATTERNS["debian11"],
                },
            },
        },
    },
    "rhel": {
        "6": {
        },
        "7": {
            5: {
                0: {
                    "patches": PATCH_RANGE["5.0"],
                    "url": PATTERNS["rhel7"],
                },
            },
            6: {
                0: {
                    "patches": PATCH_RANGE["6.0"],
                    "url": PATTERNS["rhel7"],
                },
            },
            7: {
                0: {
                    "patches": PATCH_RANGE["7.0"],
                    "url": PATTERNS["rhel7"],
                },
            },
        },
        "8": {
            5: {
                0: {
                    "patches": PATCH_RANGE["5.0"],
                    "url": PATTERNS["rhel8"],
                },
            },
            6: {
                0: {
                    "patches": PATCH_RANGE["6.0"],
                    "url": PATTERNS["rhel8"],
                },
            },
            7: {
                0: {
                    "patches": PATCH_RANGE["7.0"],
                    "url": PATTERNS["rhel8"],
                },
            },
        },
        "9": {
            6: {
                0: {
                    "patches": PATCH_RANGE["6.0-rhel9"],
                    "url": PATTERNS["rhel9"],
                },
            },
            7: {
                0: {
                    "patches": PATCH_RANGE["7.0"],
                    "url": PATTERNS["rhel9"],
                },
            },
        },
    },
    "rhel-arm": {
        "8": {
            5: {
                0: {
                    "patches": PATCH_RANGE["5.0"],
                    "url": PATTERNS["rhel-arm-8"],
                },
            },
            6: {
                0: {
                    "patches": PATCH_RANGE["6.0"],
                    "url": PATTERNS["rhel-arm-8"],
                },
            },
            7: {
                0: {
                    "patches": PATCH_RANGE["7.0"],
                    "url": PATTERNS["rhel-arm-8"],
                },
            },
        },
        "9": {
            6: {
                0: {
                    "patches": PATCH_RANGE["6.0-rhel-arm-9"],
                    "url": PATTERNS["rhel-arm-9"],
                },
            },
            7: {
                0: {
                    "patches": PATCH_RANGE["7.0"],
                    "url": PATTERNS["rhel-arm-9"],
                },
            },
        },
    },
    "suse": {
        "11": {
        },
        "12": {
            5: {
                0: {
                    "patches": PATCH_RANGE["5.0"],
                    "url": PATTERNS["suse12"],
                },
            },
            6: {
                0: {
                    "patches": PATCH_RANGE["6.0"],
                    "url": PATTERNS["suse12"],
                },
            },
            7: {
                0: {
                    "patches": PATCH_RANGE["7.0"],
                    "url": PATTERNS["suse12"],
                },
            },
        },
        "15": {
            5: {
                0: {
                    "patches": PATCH_RANGE["5.0"],
                    "url": PATTERNS["suse15"],
                },
            },
            6: {
                0: {
                    "patches": PATCH_RANGE["6.0"],
                    "url": PATTERNS["suse15"],
                },
            },
            7: {
                0: {
                    "patches": PATCH_RANGE["7.0"],
                    "url": PATTERNS["suse15"],
                },
            },
        },
    },
    "ubuntu": {
        "14": {
        },
        "16": {
        },
        "18": {
            5: {
                0: {
                    "patches": PATCH_RANGE["5.0"],
                    "url": PATTERNS["ubuntu18"],
                },
            },
            6: {
                0: {
                    "patches": PATCH_RANGE["6.0"],
                    "url": PATTERNS["ubuntu18"],
                },
            },
        },
        "20": {
            5: {
                0: {
                    "patches": PATCH_RANGE["5.0"],
                    "url": PATTERNS["ubuntu20"],
                },
            },
            6: {
                0: {
                    "patches": PATCH_RANGE["6.0"],
                    "url": PATTERNS["ubuntu20"],
                },
            },
            7: {
                0: {
                    "patches": PATCH_RANGE["7.0"],
                    "url": PATTERNS["ubuntu20"],
                },
            },
        },
        "22": {
            6: {
                0: {
                    "patches": PATCH_RANGE["6.0"],
                    "url": PATTERNS["ubuntu22"],
                },
            },
            7: {
                0: {
                    "patches": PATCH_RANGE["7.0"],
                    "url": PATTERNS["ubuntu22"],
                },
            },
        },
    },
    "ubuntu-arm": {
        "20": {
            5: {
                0: {
                    "patches": PATCH_RANGE["5.0"],
                    "url": PATTERNS["ubuntu-arm-20"],
                },
            },
            6: {
                0: {
                    "patches": PATCH_RANGE["6.0"],
                    "url": PATTERNS["ubuntu-arm-20"],
                },
            },
            7: {
                0: {
                    "patches": PATCH_RANGE["7.0"],
                    "url": PATTERNS["ubuntu-arm-20"],
                },
            },
        },
        "22": {
            6: {
                0: {
                    "patches": PATCH_RANGE["6.0"],
                    "url": PATTERNS["ubuntu-arm-22"],
                },
            },
            7: {
                0: {
                    "patches": PATCH_RANGE["7.0"],
                    "url": PATTERNS["ubuntu-arm-22"],
                },
            },
        },
    },
    "linux": {
        "generic": {
        },
    },
    "osx": {
        "generic": {
            5: {
                0: {
                    "patches": PATCH_RANGE["5.0"],
                    "url": PATTERNS["macos"],
                },
            },
            6: {
                0: {
                    "patches": PATCH_RANGE["6.0"],
                    "url": PATTERNS["macos"],
                },
            },
            7: {
                0: {
                    "patches": PATCH_RANGE["7.0"],
                    "url": PATTERNS["macos"],
                },
            },
            8: {
                0: {
                    "patches": PATCH_RANGE["8.0"],
                    "url": PATTERNS["macos"],
                },
            },
        },
    },
    "macos": {
        "arm": {
            6: {
                0: {
                    "patches": PATCH_RANGE["6.0"],
                    "url": PATTERNS["macos-arm"],
                },
            },
            7: {
                0: {
                    "patches": PATCH_RANGE["7.0"],
                    "url": PATTERNS["macos-arm"],
                },
            },
            8: {
                0: {
                    "patches": PATCH_RANGE["8.0"],
                    "url": PATTERNS["macos-arm"],
                },
            },
        },
    },
    "windows": {
        "generic": {
            5: {
                0: {"patches": PATCH_RANGE["5.0"], "url": PATTERNS["windows-x86_64"]},
            },
            6: {
                0: {"patches": PATCH_RANGE["6.0"], "url": PATTERNS["windows-x86_64"]},
            },
            7: {
                0: {"patches": PATCH_RANGE["7.0"], "url": PATTERNS["windows-x86_64"]},
            },
        },
    },
}
