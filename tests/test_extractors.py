# Copyright 2021 Edward Leardi. All Rights Reserved.
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

import copy
import hashlib
import json
import tarfile

import pytest

from nourish.dataset import Dataset
from nourish._extractors import Extractor


class TestBaseExtractor:
    "Test Extractor ABC."

    def test_abstract(self):
        "Test Extractor is an abstract class."

        with pytest.raises(TypeError) as e:
            Extractor()
        assert 'abstract class' in str(e.value)

    def test_abstract_methods(self, tmp_path):
        "Extractor.extract() and Extractor.verify_extraction() must be overridden upon Extractor being inherited."

        class MyExtractor(Extractor):
            pass

        # Error out when instantiating MyExtractor because abstract methods not overridden
        with pytest.raises(TypeError) as e:
            MyExtractor()
        assert "Can't instantiate abstract class MyExtractor with abstract method" in str(e.value)

        class MyExtractor(Extractor):
            def extract(self, path, data_dir, file_list_file):
                super().extract(path, data_dir, file_list_file)

            def verify_extraction(self, data_dir, contents):
                super().verify_extraction(data_dir, contents)

        # Shouldn't error out
        MyExtractor().extract(None, None, None)
        MyExtractor().verify_extraction(None, None)


class TestExtractors:
    "Test Extractors functionality."

    @pytest.mark.parametrize('extractable, extractable_type',
                             [
                                 # Tarball containing test.txt and test.csv
                                 ('test.tar', 'application/x-tar'),
                                 # Bzip compressed tarball containing test.txt and test.csv
                                 ('test.tar.bz2', 'application/x-tar'),
                                 # GZip compressed tarball containing test.txt and test.csv
                                 ('test.tar.gz', 'application/x-tar'),
                                 # LZMA compressed tarball containing test.txt and test.csv
                                 ('test.tar.xz', 'application/x-tar'),
                                 # Bzip2 compressed test.txt
                                 ('test.txt.bz2', 'bzip2'),
                                 # GZip compressed test.txt
                                 ('test.txt.gz', 'gzip'),
                                 # LZMA compressed test.txt
                                 ('test.txt.xz', 'xz'),
                                 # Zipped archive containing test.txt and test.csv
                                 ('test.zip', 'application/zip'),
                                 # Gzip compressed tarball missing extension
                                 ('test-tar-gz', 'application/x-tar'),
                                 # Gzip compressed csv missing extension
                                 ('test-csv-gz', 'gzip'),
                                 # Bzip2 compressed csv with wrong extension
                                 ('test-csv-bz2.csv.xz', 'bzip2')
                             ])
    def test_supported_file_extensions(self, dataset_base_url, dataset_dir, extractable,
                                       extractable_type, gmb_schema, tmp_path):
        "Test extract_data_files and verify_data_files to make sure proper extractors are used for various datasets."

        fake_schema = gmb_schema
        fake_schema['download_url'] = dataset_base_url + '/extractables/' + extractable
        fake_schema['sha512sum'] = hashlib.sha512((dataset_dir / 'extractables' / extractable).read_bytes()).hexdigest()
        dataset = Dataset(fake_schema, data_dir=tmp_path, mode=Dataset.InitializationMode.DOWNLOAD_ONLY)
        assert dataset.is_downloaded() is True
        with open(dataset._file_list_file, mode='r') as f:
            file_list = json.load(f)
        assert file_list['type'] == extractable_type

    def test_unsupported_file_extensions(self, tmp_path, gmb_schema, schema_file_https_url, schema_file_relative_dir):
        "Test if Dataset class catches an unsupported filetype (flat files like ``.yaml`` currently unsupported)."

        fake_schema = gmb_schema
        fake_schema['download_url'] = schema_file_https_url + '/datasets.yaml'
        fake_schema['sha512sum'] = hashlib.sha512((schema_file_relative_dir / 'datasets.yaml').read_bytes()).hexdigest()

        with pytest.raises(RuntimeError) as e:
            Dataset(fake_schema, data_dir=tmp_path, mode=Dataset.InitializationMode.DOWNLOAD_ONLY)
        assert str(e.value) == 'Filetype not (yet) supported'

    def test_tar_extractor(self, dataset_base_url, dataset_dir, gmb_schema, tmp_path):
        "Test _TarExtractor to make sure tar datasets are properly extracted and verified."

        fake_schema = gmb_schema
        fake_schema['download_url'] = dataset_base_url + '/extractables/test.tar.gz'
        fake_schema['sha512sum'] = hashlib.sha512((dataset_dir / 'extractables/test.tar.gz').read_bytes()).hexdigest()
        tar_gz_dataset = Dataset(fake_schema, data_dir=tmp_path, mode=Dataset.InitializationMode.DOWNLOAD_ONLY)
        assert tar_gz_dataset.is_downloaded() is True

        # Content of the file list
        with open(tar_gz_dataset._file_list_file, mode='r') as f:
            file_list = json.load(f)

        def test_incorrect_file_list(change: dict):
            "Test a single case that somewhere in the file list things are wrong."

            wrong_file_list = copy.deepcopy(file_list)
            wrong_file_list['contents'].update(change)
            with open(tar_gz_dataset._file_list_file, mode='w') as f:
                json.dump(wrong_file_list, f)
            assert tar_gz_dataset.is_downloaded() is False

        # Can't find a file
        test_incorrect_file_list({'non-existing-file': {'type': int(tarfile.REGTYPE)}})
        # File type incorrect
        test_incorrect_file_list({'.': {'type': int(tarfile.REGTYPE)}})
        test_incorrect_file_list({'./test.csv': {'type': int(tarfile.DIRTYPE)}})
        test_incorrect_file_list({'./test.txt': {'type': int(tarfile.SYMTYPE)}})
        # Size incorrect
        changed = copy.deepcopy(file_list['contents']['./test.csv'])
        changed['size'] += 100
        test_incorrect_file_list({'./test.csv': changed})

    def test_zip_extractor(self, dataset_base_url, dataset_dir, gmb_schema, tmp_path):
        "Test _ZipExtractor to make sure zip datasets are properly extracted and verified."

        fake_schema = gmb_schema
        fake_schema['download_url'] = dataset_base_url + '/extractables/test.zip'
        fake_schema['sha512sum'] = hashlib.sha512((dataset_dir / 'extractables/test.zip').read_bytes()).hexdigest()
        zip_dataset = Dataset(fake_schema, data_dir=tmp_path, mode=Dataset.InitializationMode.DOWNLOAD_ONLY)
        assert zip_dataset.is_downloaded() is True

        # Content of the file list
        with open(zip_dataset._file_list_file, mode='r') as f:
            file_list = json.load(f)

        def test_incorrect_file_list(change: dict):
            "Test a single case that somewhere in the file list things are wrong."

            wrong_file_list = copy.deepcopy(file_list)
            wrong_file_list['contents'].update(change)
            with open(zip_dataset._file_list_file, mode='w') as f:
                json.dump(wrong_file_list, f)
            assert zip_dataset.is_downloaded() is False

        # Can't find a file
        test_incorrect_file_list({'non-existing-file': {'isdir': False}})
        # File type incorrect
        test_incorrect_file_list({'test-dir/test.csv': {'isdir': True}})
        # Size incorrect
        changed = copy.deepcopy(file_list['contents']['test-dir/test.txt'])
        changed['size'] += 100
        test_incorrect_file_list({'test-dir/test.txt': changed})

    @pytest.mark.parametrize('compressed_file',
                             ('test.txt.gz',
                              'test.txt.bz2',
                              'test.txt.xz'))
    def test_compression_extractors(self, compressed_file, dataset_base_url, dataset_dir, gmb_schema, tmp_path):
        "Test compression extractors (gzip, bzip2, and lzma) to make sure datasets are properly extracted and verified."

        fake_schema = gmb_schema
        fake_schema['download_url'] = dataset_base_url + '/extractables/' + compressed_file
        compressed_fp = dataset_dir / ('extractables/' + compressed_file)
        fake_schema['sha512sum'] = hashlib.sha512((compressed_fp).read_bytes()).hexdigest()
        dataset = Dataset(fake_schema, data_dir=tmp_path, mode=Dataset.InitializationMode.DOWNLOAD_ONLY)
        assert dataset.is_downloaded() is True

        # Content of the file list
        with open(dataset._file_list_file, mode='r') as f:
            file_list = json.load(f)

        def test_incorrect_file_list(change: dict):
            "Test a single case that somewhere in the file list things are wrong."

            wrong_file_list = copy.deepcopy(file_list)
            wrong_file_list['contents'].update(change)
            with open(dataset._file_list_file, mode='w') as f:
                json.dump(wrong_file_list, f)
            assert dataset.is_downloaded() is False

        # Can't find the file
        test_incorrect_file_list({'filename': 'non-existing-file'})
        # Size incorrect
        changed = copy.deepcopy(file_list['contents'])
        changed['size'] += 100
        test_incorrect_file_list(changed)

    @pytest.mark.parametrize('zerobyte_file',
                             ('test-zerobyte.csv.gz',
                              'test-zerobyte.csv.bz2',
                              'test-zerobyte.csv.xz'))
    def test_zerobyte_files(self, dataset_base_url, dataset_dir, gmb_schema, tmp_path, zerobyte_file):
        "Test compression extractors to make sure they handle zero-byte files."

        fake_schema = gmb_schema
        fake_schema['download_url'] = dataset_base_url + '/extractables/' + zerobyte_file
        zerobyte_fp = dataset_dir / ('extractables/' + zerobyte_file)
        fake_schema['sha512sum'] = hashlib.sha512((zerobyte_fp).read_bytes()).hexdigest()
        with pytest.raises(OSError) as e:
            Dataset(fake_schema, data_dir=(tmp_path), mode=Dataset.InitializationMode.DOWNLOAD_ONLY)
        assert str(e.value) == ('The extracted file test-zerobyte.csv is empty.')
