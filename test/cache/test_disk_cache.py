# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0
#
# Portions derived from  https://github.com/microsoft/autogen are under the MIT License.
# SPDX-License-Identifier: MIT
# !/usr/bin/env python3 -m pytest

import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from autogen.cache.disk_cache import DiskCache

ROOT = Path(__file__).resolve().parents[2]


def test_autogen_import_does_not_require_diskcache():
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; sys.modules['diskcache'] = None; import autogen; from autogen import ConversableAgent",
        ],
        check=False,
    )
    assert completed.returncode == 0


def test_disk_cache_requires_optional_extra(monkeypatch):
    monkeypatch.setattr("autogen.cache.disk_cache.diskcache", None)
    with pytest.raises(ImportError, match="ag2\\[diskcache\\]"):
        DiskCache("test")


def test_features_and_ci_that_use_disk_cache_install_the_extra():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'long-context = ["llmlingua<0.3", "diskcache"]' in pyproject

    pr_checks = (ROOT / ".github" / "workflows" / "pr-checks.yml").read_text(encoding="utf-8")
    assert ".[test,cosmosdb,interop,redis,websockets,docs,diskcache]" in pr_checks


def test_transitive_optional_sdks_stay_on_supported_major_versions():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert '"mcp>=1.11.0,<2"' in pyproject
    assert '"mistralai>=1.0.1,<2"' in pyproject


class TestDiskCache:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.seed = "test_seed"

    @patch("autogen.cache.disk_cache.diskcache.Cache", return_value=MagicMock())
    def test_init(self, mock_cache):
        cache = DiskCache(self.seed)
        assert isinstance(cache.cache, MagicMock)
        mock_cache.assert_called_with(self.seed)

    @patch("autogen.cache.disk_cache.diskcache.Cache", return_value=MagicMock())
    def test_get(self, mock_cache):
        key = "key"
        value = "value"
        cache = DiskCache(self.seed)
        cache.cache.get.return_value = value
        assert cache.get(key) == value
        cache.cache.get.assert_called_with(key, None)

        cache.cache.get.return_value = None
        assert cache.get(key, None) is None

    @patch("autogen.cache.disk_cache.diskcache.Cache", return_value=MagicMock())
    def test_set(self, mock_cache):
        key = "key"
        value = "value"
        cache = DiskCache(self.seed)
        cache.set(key, value)
        cache.cache.set.assert_called_with(key, value)

    @patch("autogen.cache.disk_cache.diskcache.Cache", return_value=MagicMock())
    def test_context_manager(self, mock_cache):
        with DiskCache(self.seed) as cache:
            assert isinstance(cache, DiskCache)
            mock_cache_instance = cache.cache
        mock_cache_instance.close.assert_called()

    @patch("autogen.cache.disk_cache.diskcache.Cache", return_value=MagicMock())
    def test_close(self, mock_cache):
        cache = DiskCache(self.seed)
        cache.close()
        cache.cache.close.assert_called()


if __name__ == "__main__":
    unittest.main()
