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

"Schemata parsing and loading functionality."


from abc import ABC
from copy import deepcopy
from typing import Any, Dict, Union

import yaml

from . import typing as typing_
from ._schema_retrieval import retrieve_schemata_file


SchemaDict = Dict[str, Any]


class BaseSchemata(ABC):
    """Abstract class that provides functionality to load and export the contents of a schemata file.

    :param url_or_path: URL or path to a schema file.
    :param tls_verification: When set to ``True``, verify the remote link is https and whether the TLS certificate is
        valid. When set to a path to a file, use this file as a CA bundle file. When set to ``False``, allow http links
        and do not verify any TLS certificates. Ignored if ``url_or_path`` is a local path.
    :raises ValueError: An error occurred when parsing ``url_or_path`` as either a URL or path.
    :raises InsecureConnectionError: The connection is insecure. See ``tls_verification`` for more details.
    """

    def __init__(self, url_or_path: Union[typing_.PathLike, str], *,
                 tls_verification: Union[bool, typing_.PathLike] = True) -> None:
        """Constructor method.
        """
        self._schemata: SchemaDict = self._load_retrieved_schemata(
                                            retrieve_schemata_file(url_or_path, tls_verification=tls_verification))

        # The URL or path from which the schema was retrieved
        self._retrieved_url_or_path: Union[typing_.PathLike, str] = url_or_path

    def _load_retrieved_schemata(self, schema: str) -> SchemaDict:
        """Safely loads retrieved schemata file.

        :param schema: Retrieved schemata object.
        :return: Nested dictionary representation of a schema.
        """
        return yaml.safe_load(schema)

    def export_schema(self, *keys: str) -> SchemaDict:
        """Returns a copy of a loaded schema. Should be used for debug purposes only.

        :param keys: The sequence of keys that leads to the portion of the schema to be exported.
        :return: Copy of the schema dictionary.

        Example:

        >>> schema = DatasetSchemata('./tests/schemata/datasets.yaml')
        >>> schema.export_schema('datasets', 'noaa_jfk', '1.1.4')
        {'name': 'NOAA Weather Data – JFK Airport'...}
        """
        schema: SchemaDict = self._schemata
        for k in keys:
            schema = schema[k]
        return deepcopy(schema)

    @property
    def retrieved_url_or_path(self) -> Union[typing_.PathLike, str]:
        """The URL or path from which the schemata was retrieved.

        Example:

        >>> schema = DatasetSchemata('./tests/schemata/datasets.yaml')
        >>> schema.retrieved_url_or_path
        './tests/schemata/datasets.yaml'
        """
        return self._retrieved_url_or_path


class DatasetSchemata(BaseSchemata):
    """Dataset schema class that inherits functionality from :class:`BaseSchemata`.
    """

    # We have this class here because we reserve the potential to put specific dataset schema code here
    pass


class FormatSchemata(BaseSchemata):
    """Format schema class that inherits functionality from :class:`BaseSchemata`.
    """

    # We have this class here because we reserve the potential to put specific format schema code here
    pass


class LicenseSchemata(BaseSchemata):
    """License schema class that inherits functionality from :class:`BaseSchemata`.
    """

    # We have this class here because we reserve the potential to put specific license schema code here
    pass


class SchemataManager():
    """Stores the loaded schemata in :attr:`schemata`.

    :param kwargs: Schemata name and BaseSchemata instance key-value pairs.

    Example:

    >>> dataset_schema = DatasetSchemata('./tests/schemata/datasets.yaml')
    >>> schema_manager = SchemataManager(datasets=dataset_schema)
    >>> licenses_schema = LicenseSchemata('./tests/schemata/licenses.yaml')
    >>> schema_manager.add_schemata('licenses', licenses_schema)
    >>> schema_manager.schemata
    {'datasets':..., 'licenses':...}
    """

    def __init__(self, **kwargs: BaseSchemata) -> None:
        """Constructor method
        """
        self.schemata: Dict[str, BaseSchemata] = {}
        for name, val in kwargs.items():
            self.add_schemata(name, val)

    def add_schemata(self, name: str, val: BaseSchemata) -> None:
        """Store schema instance in a dictionary. If a schema with the same name as ``name`` is already stored, it is
        overridden.

        :param name: Schemata name.
        :param val: BaseSchemata instance.
        """
        if not isinstance(val, BaseSchemata):
            raise TypeError('val must be a BaseSchemata instance.')
        self.schemata[name] = val
