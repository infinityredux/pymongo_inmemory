import hashlib
from platform import uname_result

from pymongo_inmemory import context

import pytest


def test_environment_var_option(monkeypatch):
    monkeypatch.setenv("PYMONGOIM__SOME_VALUE", "42")
    assert context.conf("some_value") == "42"
    assert context.conf("SOME_VALUE") == "42"
    assert context.conf("SOME_OTHER_VALUE") is None


def test_env_folders_overwrite_default_download_folder(monkeypatch):
    monkeypatch.setenv("PYMONGOIM__DOWNLOAD_FOLDER", "test_folder")
    pim_context = context.Context()
    assert "/test_folder/" in pim_context.download_folder


def test_env_folders_overwrite_default_extract_folder(monkeypatch):
    monkeypatch.setenv("PYMONGOIM__EXTRACT_FOLDER", "test_folder")
    pim_context = context.Context()
    assert "/test_folder/" in pim_context.extract_folder


def test_fails_if_os_unknown(monkeypatch):
    def system():
        return "Unknown"

    def conf(*args, **kwargs):
        return

    def uname():
        # noinspection PyArgumentList
        return uname_result('', '', '', '', '')

    monkeypatch.setattr(context.platform, "system", system)
    monkeypatch.setattr(context.platform, "uname", uname)
    monkeypatch.setattr(context, "conf", conf)
    with pytest.raises(context.OperatingSystemNotFound):
        context.Context()


def test_download_url_setting(monkeypatch):
    provided_url = "https://www.mydownloadurl.com"
    expected_hash = hashlib.sha256(bytes(provided_url, "utf-8")).hexdigest()
    monkeypatch.setenv("PYMONGOIM__DOWNLOAD_URL", provided_url)
    pim_context = context.Context()
    assert pim_context.download_url == provided_url
    assert expected_hash in pim_context.download_folder
    assert expected_hash in pim_context.extract_folder


def test_expected_type_coercion(monkeypatch):
    monkeypatch.setenv("PYMONGOIM__MONGOD_PORT", "42")
    monkeypatch.setenv("PYMONGOIM__IGNORE_CACHE", "True")
    monkeypatch.setenv("PYMONGOIM__USE_LOCAL_MONGOD", "True")
    pim_context = context.Context()
    assert pim_context.ignore_cache
    assert pim_context.use_local_mongod
    assert pim_context.mongod_port == 42


def test_type_coercion_invalid_types(monkeypatch):
    monkeypatch.setenv("PYMONGOIM__MONGOD_PORT", "something")
    monkeypatch.setenv("PYMONGOIM__IGNORE_CACHE", "true")
    monkeypatch.setenv("PYMONGOIM__USE_LOCAL_MONGOD", "true")
    pim_context = context.Context()
    assert not pim_context.ignore_cache
    assert not pim_context.use_local_mongod
    assert pim_context.mongod_port is None
