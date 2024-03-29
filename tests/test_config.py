# Copyright 2021 Edward Leardi. All Rights Reserved.
#
# Copyright 2020 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from urllib.parse import urlparse

import pytest
import requests.exceptions

from nourish import init
from nourish._config import Config
from nourish._schemata_retrieval import retrieve_schemata_file


class TestConfig:
    "Test the Config dataclass."

    def test_default_schemata_url_https(self):
        "Test the default schemata URLs are https-schemed."

        assert urlparse(Config.DATASET_SCHEMATA_URL).scheme == 'https'
        assert urlparse(Config.FORMAT_SCHEMATA_URL).scheme == 'https'
        assert urlparse(Config.LICENSE_SCHEMATA_URL).scheme == 'https'

    @pytest.mark.xfail(reason="default remote might be down but it's not this library's issue",
                       raises=requests.exceptions.ConnectionError)
    def test_default_schemata_url_content(self):
        """Test the content of the remote URLs a bit. We only assert them not being None here just in case the server
        returns zero-length files."""

        init(update_only=False)

        # We only assert that we have retrieved some non-empty files in this test. This is because we want to decouple
        # the maintenance of schemata files in production with the library development. These files likely would change
        # more regularly than the library. For this reason, we also verify the default schemata URLs are also valid
        # https links in ``test_default_schemata_url_https``.

        # This test is in `test_config.py` not in `test_schemata_retrieval.py` because this test is more about the
        # content of the default schemata URLs than the retrieving functionality.
        assert len(retrieve_schemata_file(Config.DATASET_SCHEMATA_URL)) > 0
        assert len(retrieve_schemata_file(Config.FORMAT_SCHEMATA_URL)) > 0
        assert len(retrieve_schemata_file(Config.LICENSE_SCHEMATA_URL)) > 0
