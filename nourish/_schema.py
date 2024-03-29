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
from ._schemata_retrieval import retrieve_schemata_file


SchemaDict = Dict[str, Any]


class BaseSchemata(ABC):
    """Abstract class that provides functionality to load and export the contents of a schemata file.

    :param url_or_path: URL or path to a schemata file.
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

        # The URL or path from which the schemata was retrieved
        self._retrieved_url_or_path: Union[typing_.PathLike, str] = url_or_path

    def _load_retrieved_schemata(self, schemata: str) -> SchemaDict:
        """Safely loads retrieved schemata file.

        :param schemata: Retrieved schemata object.
        :return: Nested dictionary representation of a schemata.
        """
        return yaml.safe_load(schemata)

    def export_schema(self, *keys: str) -> SchemaDict:
        """Returns a copy of a loaded schemata. Typically used to export a schema contained within the schemata.

        :param keys: The sequence of keys that leads to the portion of the schemata to be exported.
        :return: Copy of the schemata dictionary.

        Example:

        >>> dataset_schemata = DatasetSchemata('./tests/schemata/datasets.yaml')
        >>> jfk_schema = dataset_schemata.export_schema('datasets', 'noaa_jfk', '1.1.4')
        >>> jfk_schema
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

        >>> dataset_schemata = DatasetSchemata('./tests/schemata/datasets.yaml')
        >>> dataset_schemata.retrieved_url_or_path
        './tests/schemata/datasets.yaml'
        """
        return self._retrieved_url_or_path


class DatasetSchemata(BaseSchemata):
    """Dataset schemata class that inherits functionality from :class:`BaseSchemata`.
    """

    # We have this class here because we reserve the potential to put specific dataset schemata code here
    pass


class FormatSchemata(BaseSchemata):
    """Format schemata class that inherits functionality from :class:`BaseSchemata`.
    """

    # We have this class here because we reserve the potential to put specific format schemata code here
    pass


class LicenseSchemata(BaseSchemata):
    """License schemata class that inherits functionality from :class:`BaseSchemata`.
    """

    # We have this class here because we reserve the potential to put specific license schemata code here
    pass


class SchemataManager():
    """Stores and manages loaded schemata.

    :param datasets: :class:`DatasetSchemata` instance.
    :param formats: :class:`FormatSchemata` instance.
    :param licenses: :class:`LicenseSchemata` instance.

    Example:

    >>> datasets = DatasetSchemata('./tests/schemata/datasets.yaml')
    >>> formats = FormatSchemata('./tests/schemata/formats.yaml')
    >>> licenses = LicenseSchemata('./tests/schemata/licenses.yaml')
    >>> schemata_manager = SchemataManager(datasets=datasets, formats=formats, licenses=licenses)
    >>> schemata_manager.schemata
    {'datasets':..., 'formats':..., 'licenses':...}
    """

    def __init__(self, datasets: DatasetSchemata, formats: FormatSchemata, licenses: LicenseSchemata) -> None:
        """Constructor method
        """
        self.schemata: Dict[str, BaseSchemata] = {'datasets': datasets, 'formats': formats, 'licenses': licenses}
        for schemata in self.schemata.values():
            self.check_schemata(schemata)

    @property
    def dataset_schemata(self) -> BaseSchemata:
        "Loaded dataset schemata."
        return self.schemata['datasets']

    @property
    def format_schemata(self) -> BaseSchemata:
        "Loaded format schemata."
        return self.schemata['formats']

    @property
    def license_schemata(self) -> BaseSchemata:
        "Loaded license schemata."
        return self.schemata['licenses']

    def check_schemata(self, schemata: BaseSchemata) -> None:
        """Check the given object to see if it is an instance of the :class:`BaseSchemata` class (or one of its
        subclasses). Raise an error if it is not.

        :param schemata: The object to be tested.
        :raises TypeError: ``schemata`` is not a valid schemata object.
        :return: No return unless the ``schemata`` is invalid, in which case see :class:`TypeError`.
        """
        if not isinstance(schemata, BaseSchemata):
            raise TypeError('schemata must be a BaseSchemata (or subclass of BaseSchemata) instance.')

    def update_schemata(self, name: str, schemata: BaseSchemata) -> None:
        """Update a schemata stored in :attr:`schemata` by overriding it with a new schemata.

        :param name: Name of the schemata to update. One of ``datasets``, ``formats``, or ``licenses``.
        :param schemata: A :class:`BaseSchemata` (or subclass) instance.
        """
        self.check_schemata(schemata)
        if name not in self.schemata.keys():
            raise KeyError('name must be one of datasets, formats, or licenses.')
        self.schemata[name] = schemata
