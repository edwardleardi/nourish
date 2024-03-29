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

import abc
import datetime

import pytest

from nourish.schema import BaseSchemata, SchemataManager


class TestBaseSchemata:
    "Test BaseSchemata ABC."

    def test_abstract(self):
        "Test BaseSchemata is an abstract class."

        assert BaseSchemata.__bases__ == (abc.ABC,)

    def test_retrieved_url_or_path(self, schemata_file_relative_dir):
        "Test whether retrieved_url_or_path gives the correct value."

        url_or_path = schemata_file_relative_dir / 'datasets.yaml'
        assert BaseSchemata(url_or_path).retrieved_url_or_path == url_or_path


class TestSchemata:
    "Test the functionality of the schemata classes."

    def test_loading_schemata(self, loaded_schemata_manager):
        "Test basic functioning of loading and parsing the schemata files."

        assert loaded_schemata_manager.dataset_schemata \
            .export_schema()['datasets']['gmb']['1.0.2']['published'] == datetime.date(2019, 12, 19)
        assert loaded_schemata_manager.license_schemata \
            .export_schema()['licenses']['cdla_sharing']['commercial_use'] is True
        assert loaded_schemata_manager.format_schemata \
            .export_schema('formats', 'csv', 'name') == 'Comma-Separated Values'
        assert loaded_schemata_manager.dataset_schemata.export_schema()['datasets']['gmb']['1.0.2']['homepage'] == \
            loaded_schemata_manager.dataset_schemata.export_schema('datasets', 'gmb', '1.0.2', 'homepage')


class TestSchemataManager:
    "Test the functionality of the SchemataManager class."

    def test_schemata_manager_value(self):
        "Test SchemataManager to make sure it raises an exception when it recieves a non-Schemata object"

        with pytest.raises(TypeError) as e:
            SchemataManager(datasets='apple',
                            formats='1',
                            licenses='3.3')
        assert str(e.value) == 'schemata must be a BaseSchemata (or subclass of BaseSchemata) instance.'

    def test_update_schemata(self, loaded_schemata_manager):
        "Test update_schemata method to make sure it raises an exception when an invalid schemata is updated."

        datasets = loaded_schemata_manager.dataset_schemata
        with pytest.raises(KeyError) as e:
            loaded_schemata_manager.update_schemata('invalid_datasets_name', datasets)
        assert str(e.value) == "\'name must be one of datasets, formats, or licenses.\'"
