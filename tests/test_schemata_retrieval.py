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

import pytest

from nourish import export_schemata_manager, init, load_schemata_manager
from nourish.schema import BaseSchemata
from nourish.exceptions import InsecureConnectionError
from nourish._schemata_retrieval import retrieve_schemata_file


class TestSchemataRetrieval:
    "Test schemata retrieval."

    # We set tls_verification to False in this test. We don't test raising this warning because it is not within the
    # project's scope to guarantee that this warning will raise, and this warning raises only once, which means that
    # whether the warning will be raised depends on the order in which the tests are being executed.
    @pytest.mark.filterwarnings('ignore:Unverified HTTPS request .*:urllib3.exceptions.InsecureRequestWarning')
    @pytest.mark.parametrize('location_type',
                             ('absolute_dir',
                              'relative_dir',
                              'file_url',
                              'http_url',
                              'https_url'))
    def test_custom_schemata_insecure(self, location_type, schemata_file_relative_dir, request):
        "Test retrieving user-specified schemata files, with insecure connections allowed."

        # We use '/' instead of os.path.sep because URLs only accept / not \ as separators, but Windows path accepts
        # both. This is not an issue for the purpose of this test.
        base = str(request.getfixturevalue('schemata_file_' + location_type)) + '/'

        assert retrieve_schemata_file(base + 'datasets.yaml', tls_verification=False) == \
            (schemata_file_relative_dir / 'datasets.yaml').read_text(encoding='utf-8')
        assert retrieve_schemata_file(base + 'formats.yaml', encoding='ascii', tls_verification=False) == \
            (schemata_file_relative_dir / 'formats.yaml').read_text(encoding='ascii')
        with pytest.raises(UnicodeDecodeError) as e:
            retrieve_schemata_file(base + 'licenses.yaml', encoding='ascii', tls_verification=False)
        # We usually don't assert the position info because we don't want to rewrite this test every time the yaml
        # file changes in length.
        assert "'ascii' codec can't decode byte 0xe2" in str(e.value)
        with pytest.raises(UnicodeDecodeError) as e:
            retrieve_schemata_file(base + 'formats-utf-16le-bom.yaml', tls_verification=False)
        # Test "position 0" here because it should fail at the beginning of the decoding
        assert "'utf-8' codec can't decode byte 0xff in position 0" in str(e.value)
        with pytest.raises(UnicodeDecodeError) as e:
            retrieve_schemata_file(base + 'formats-utf-16be.yaml', encoding='utf-8', tls_verification=False)
        assert "'utf-8' codec can't decode byte 0x90" in str(e.value)

    def test_invalid_schemata(self):
        "Test retrieving user-specified invalid schemata files."

        with pytest.raises(ValueError) as e:
            retrieve_schemata_file(url_or_path='ftp://ftp/is/unsupported')

        assert str(e.value) == 'Unknown scheme in "ftp://ftp/is/unsupported": "ftp"'


class TestSecureSchemataRetrieval:
    "Common tests that mainly concern securely retrieving schemata files."

    @pytest.fixture(params=('http_url', 'https_url'))
    def remote_dataset_schemata_url(self, request) -> str:
        "http/https url to datasets.yaml."
        return str(request.getfixturevalue('schemata_file_' + request.param)) + '/datasets.yaml'

    @pytest.fixture(params=('absolute_dir', 'relative_dir', 'file_url', 'https_url'))
    def dataset_schemata_url_or_path(self, request) -> str:
        "Every kind of URL or path (other than http URL) to datasets.yaml."
        # We use '/' instead of os.path.sep because URLs only accept / not \ as separators, but Windows path accepts
        # both. This is not an issue for the purpose of this test.
        return str(request.getfixturevalue('schemata_file_' + request.param)) + '/datasets.yaml'

    @pytest.mark.parametrize('caller', (retrieve_schemata_file, BaseSchemata))
    def test_insecure_connections_fail(self, remote_dataset_schemata_url, untrust_self_signed_cert, caller):
        "Test insecure connections that should fail."
        with pytest.raises(InsecureConnectionError) as e:
            caller(remote_dataset_schemata_url, tls_verification=True)
        assert remote_dataset_schemata_url in str(e.value)

    def test_secure_connections_succeed_retrieve_schemata_file(self,
                                                               dataset_schemata_url_or_path,
                                                               schemata_file_relative_dir):
        "Test secure connections that should succeed for ``retrieve_schemata_file``."
        assert retrieve_schemata_file(dataset_schemata_url_or_path, tls_verification=True) == \
            (schemata_file_relative_dir / 'datasets.yaml').read_text(encoding='utf-8')

    def test_secure_connections_succeed_schemata(self,
                                                 dataset_schemata_url_or_path,
                                                 schemata_file_relative_dir):
        "Test secure connections that should succeed for ``BaseSchemata()``."
        assert BaseSchemata(dataset_schemata_url_or_path, tls_verification=True).retrieved_url_or_path == \
               dataset_schemata_url_or_path

    def test_insecure_connections_load_schemata_manager(self, remote_dataset_schemata_url, untrust_self_signed_cert):
        "Test insecure connections that should fail when ``tls_verification=True`` for ``load_schemata_manager``."
        init(update_only=True, DATASET_SCHEMATA_URL=remote_dataset_schemata_url)
        with pytest.raises(InsecureConnectionError) as e:
            load_schemata_manager(force_reload=True, tls_verification=True)
        assert remote_dataset_schemata_url in str(e.value)

        # Insecure load succeeds, no exception raised
        load_schemata_manager(force_reload=True, tls_verification=False)
        assert export_schemata_manager().dataset_schemata.retrieved_url_or_path == remote_dataset_schemata_url

    def test_secure_connections_succeed_load_schemata_manager(self, dataset_schemata_url_or_path):
        "Test secure connections that should succeed for :func:`nourish.load_schemata_manager`."
        # We use '/' instead of os.path.sep because URLs only accept / not \ as separators, but Windows path accepts
        # both. This is not an issue for the purpose of this test.
        init(update_only=True, DATASET_SCHEMATA_URL=dataset_schemata_url_or_path)
        load_schemata_manager(force_reload=True, tls_verification=True)
        assert export_schemata_manager().dataset_schemata.retrieved_url_or_path == dataset_schemata_url_or_path

    @pytest.mark.parametrize('caller', (retrieve_schemata_file, BaseSchemata.__init__, load_schemata_manager))
    def test_default_tls_verification(self, caller):
        "Ensure that ``tls_verification=True`` by default."
        assert caller.__kwdefaults__['tls_verification'] is True
