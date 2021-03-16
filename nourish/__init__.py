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

"Nourish package and high level functions."


from . import dataset, exceptions, loaders, schema
from ._high_level import (describe_dataset,
                          export_schemata_manager,
                          get_config,
                          get_dataset_metadata,
                          init,
                          list_all_datasets,
                          load_dataset,
                          load_schemata_manager)
from ._version import version as __version__

__all__ = (
           # modules & subpackages
           'dataset',
           'exceptions',
           'loaders',
           'schema',
           # high-level functions
           'describe_dataset',
           'export_schemata_manager',
           'get_config',
           'get_dataset_metadata',
           'init',
           'list_all_datasets',
           'load_dataset',
           'load_schemata_manager',
           # _version
           '__version__'
)
