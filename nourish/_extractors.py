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

"Dataset unarchiving and uncompressing functionality."


from abc import ABC, abstractmethod
import bz2
import gzip
import json
import lzma
import mimetypes
import pathlib
import shutil
import tarfile
from typing import Dict, Union
import zipfile


class Extractor(ABC):
    """Abstract class that provides functionality to extract dataset downloads.
    """

    @abstractmethod
    def extract(self, path: pathlib.Path, data_dir: pathlib.Path, file_list_file: pathlib.Path) -> None:
        """Extracts dataset download by unarchiving and/or uncompressing the files. This must be overridden when inherited.

        :param path: Path to the dataset to extract.
        :param data_dir: Path to the data dir to extract data files to.
        :file_list_file: Path to the file that stores the list of files in the downloaded dataset.
        """
        pass

    @abstractmethod
    def verify_extraction(self, data_dir: pathlib.Path, contents: dict) -> bool:
        """Verifies file extraction. This must be overridden when inherited.

        :param data_dir: Path to the data dir containing the extracted files.
        :contents: Dict obtained from ``file_list_file`` with metadata of files in the downloaded dataset.
        :return: ``True`` if the dataset was extracted properly and ``False`` otherwise.
        """
        pass


class _TarExtractor(Extractor):
    """Extractor that handles tarballs. Capable of handling files like: ``.tar``, ``.tar.gz``, ``.tar.bz2``,
    and ``.tar.xz``.
    """

    def extract(self, path: pathlib.Path, data_dir: pathlib.Path, file_list_file: pathlib.Path) -> None:
        """Attempt to extract the tar archive. Save metadata about the list of files in the downloaded dataset in
        ``file_list_file``.

        :param path: Path to the tar archive.
        :param data_dir: Path to the data dir to extract data files to.
        :file_list_file: Path to the file that stores the list of files in the downloaded dataset.
        :raises tarfile.ReadError: The tar archive was unable to be read.
        """
        try:
            mytar = tarfile.open(path)
        except tarfile.ReadError as e:
            raise tarfile.ReadError(f'Failed to unarchive tar file "{path}"\ncaused by:\n{e}')
        with mytar:
            FileListFileContents = Dict[str, Dict[str, int]]
            contents: FileListFileContents = {}
            metadata: Dict[str, Union[str, FileListFileContents]] = {}

            metadata['type'] = 'application/x-tar'
            for member in mytar.getmembers():
                contents[member.name] = {'type': int(member.type)}
                if member.isreg():  # For regular files, we also save its size
                    contents[member.name]['size'] = member.size
            metadata['contents'] = contents

            with open(file_list_file, mode='w') as f:
                # We do not specify 'utf-8' here to match the default encoding used by the OS, which also likely
                # uses this encoding for accessing the filesystem.
                json.dump(metadata, f, indent=2)
            mytar.extractall(path=data_dir)

    def verify_extraction(self, data_dir: pathlib.Path, contents: Dict[str, Dict[str, int]]) -> bool:
        """Verify the files were extracted properly using the metadata saved in ``file_list_file``.

        :param data_dir: Path to the data dir containing the extracted files.
        :contents: Dict obtained from ``file_list_file`` with metadata of files in the downloaded dataset.
        :return: ``True`` if the dataset was extracted properly and ``False`` otherwise.
        """
        for name, info in contents.items():
            path = data_dir / name
            if not path.exists():
                # At least one file in the file list is missing
                return False
            # We don't have pathlib type code that matches tarfile type code. We instead do an incomplete list of
            # type comparison. We don't do uncommon types such as FIFO, character device, etc. here.
            if info['type'] == int(tarfile.REGTYPE):  # Regular file
                if not path.is_file():
                    return False
                if path.stat().st_size != info['size']:
                    return False
            elif info['type'] == int(tarfile.DIRTYPE) and not path.is_dir():  # Directory type
                return False
            elif info['type'] == int(tarfile.SYMTYPE) and not path.is_symlink():  # Symbolic link type
                return False
            else:
                # We just let go any file types that we don't understand.
                pass
        return True


class _ZipExtractor(Extractor):
    """Extractor that handles zip archives. Capable of handling files like: ``.zip``.
    """

    def extract(self, path: pathlib.Path, data_dir: pathlib.Path, file_list_file: pathlib.Path) -> None:
        """Attempt to extract the zip archive. Save metadata about the list of files in the downloaded dataset in
        ``file_list_file``.

        :param path: Path to the zip archive.
        :param data_dir: Path to the data dir to extract data files to.
        :file_list_file: Path to the file that stores the list of files in the downloaded dataset.
        :raises zipfile.BadZipFile: The zip archive was unable to be read.
        """
        try:
            myzip = zipfile.ZipFile(path)
        except zipfile.BadZipFile as e:
            raise zipfile.BadZipFile(f'Failed to unarchive zip file "{path}"\ncaused by:\n{e}')
        with myzip:
            FileListFileContents = Dict[str, Dict[str, Union[bool, int]]]
            contents: FileListFileContents = {}
            metadata: Dict[str, Union[str, FileListFileContents]] = {}

            metadata['type'] = 'application/zip'
            for member in myzip.infolist():
                contents[member.filename] = {'isdir': member.is_dir()}
                if not member.is_dir():
                    contents[member.filename]['size'] = member.file_size
            metadata['contents'] = contents

            with open(file_list_file, mode='w') as f:
                json.dump(metadata, f, indent=2)
            myzip.extractall(path=data_dir)

    def verify_extraction(self, data_dir: pathlib.Path, contents: Dict[str, Dict[str, Union[bool, int]]]) -> bool:
        """Verify the files were extracted properly using the metadata saved in ``file_list_file``.

        :param data_dir: Path to the data dir containing the extracted files.
        :contents: Dict obtained from ``file_list_file`` with metadata of files in the downloaded dataset.
        :return: ``True`` if the dataset was extracted properly and ``False`` otherwise.
        """
        for name, info in contents.items():
            path = data_dir / name
            if not path.exists():
                # At least one file in the file list is missing
                return False
            # Ignore checking symlinks
            if not path.is_symlink():
                if path.is_dir() != info['isdir']:
                    return False
                if not info['isdir'] and (path.stat().st_size != info['size']):
                    return False
        return True


# gzip.BadGzipFile wasn't added until Python 3.8, so we use our own exception
class _BadGzipFile(Exception):
    "Not a gzip file."
    pass


class _GzipExtractor(Extractor):
    """Extractor that handles gzip compressed files. Capable of handling files like: ``.gz``, ``.txt.gz``, and
    ``.csv.gz``.
    """

    def extract(self, path: pathlib.Path, data_dir: pathlib.Path, file_list_file: pathlib.Path) -> None:
        """Attempt to extract the gzip compressed file. Save metadata about the file in the downloaded dataset in
        ``file_list_file``.

        :param path: Path to the gzip file.
        :param data_dir: Path to the data dir to extract the data file to.
        :file_list_file: Path to the file that stores metadata of the file in the downloaded dataset.
        :raises _BadGzipFile: The gzip file was unable to be read.
        :raises OSError: The extracted file is empty.
        """
        try:
            mygzip = gzip.open(path)
            extracted_file_name = path.stem
            with mygzip, open(data_dir / extracted_file_name, 'wb') as f_out:
                shutil.copyfileobj(mygzip, f_out)
        except OSError as e:
            raise _BadGzipFile(f'Failed to uncompress gzip file "{path}"\ncaused by:\n{e}')
        extracted_fp = data_dir / extracted_file_name

        FileListFileContents = Dict[str, Union[int, str]]
        contents: FileListFileContents = {}
        metadata: Dict[str, Union[str, FileListFileContents]] = {}

        metadata['type'] = 'gzip'
        contents['filename'] = extracted_file_name
        contents['size'] = extracted_fp.stat().st_size
        if contents['size'] == 0:
            raise OSError(f'The extracted file {extracted_file_name} is empty.')
        metadata['contents'] = contents

        with open(file_list_file, mode='w') as f:
            json.dump(metadata, f, indent=2)

    def verify_extraction(self, data_dir: pathlib.Path, contents: dict) -> bool:
        """Verify the file was extracted properly using the metadata saved in ``file_list_file``.

        :param data_dir: Path to the data dir containing the extracted file.
        :contents: Dict obtained from ``file_list_file`` with metadata of the file in the downloaded dataset.
        :return: ``True`` if the dataset was extracted properly and ``False`` otherwise.
        """
        path = data_dir / contents['filename']
        if not path.exists():
            # File is missing
            return False
        if path.stat().st_size != contents['size']:
            return False
        return True


class _BadBzip2File(Exception):
    "Not a bzip2 file."
    pass


class _Bzip2Extractor(Extractor):
    """Extractor that handles bzip2 compressed files. Capable of handling files like: ``.bz2``, ``.txt.bz2``, and
    ``.csv.bz2``.
    """

    def extract(self, path: pathlib.Path, data_dir: pathlib.Path, file_list_file: pathlib.Path) -> None:
        """Attempt to extract the bzip2 compressed file. Save metadata about the file in the downloaded dataset in
        ``file_list_file``.

        :param path: Path to the bzip2 file.
        :param data_dir: Path to the data dir to extract the data file to.
        :file_list_file: Path to the file that stores metadata of the file in the downloaded dataset.
        :raises _BadBzip2File: The bzip2 file was unable to be read.
        :raises OSError: The extracted file is empty.
        """
        try:
            mybzip2 = bz2.open(path)
            extracted_file_name = path.stem
            with mybzip2, open(data_dir / extracted_file_name, 'wb') as f_out:
                shutil.copyfileobj(mybzip2, f_out)
        except OSError as e:
            raise _BadBzip2File(f'Failed to uncompress bzip2 file "{path}"\ncaused by:\n{e}')
        extracted_fp = data_dir / extracted_file_name

        FileListFileContents = Dict[str, Union[int, str]]
        contents: FileListFileContents = {}
        metadata: Dict[str, Union[str, FileListFileContents]] = {}

        metadata['type'] = 'bzip2'
        contents['filename'] = extracted_file_name
        contents['size'] = extracted_fp.stat().st_size
        if contents['size'] == 0:
            raise OSError(f'The extracted file {extracted_file_name} is empty.')
        metadata['contents'] = contents

        with open(file_list_file, mode='w') as f:
            json.dump(metadata, f, indent=2)

    def verify_extraction(self, data_dir: pathlib.Path, contents: dict) -> bool:
        """Verify the file was extracted properly using the metadata saved in ``file_list_file``.

        :param data_dir: Path to the data dir containing the extracted file.
        :contents: Dict obtained from ``file_list_file`` with metadata of the file in the downloaded dataset.
        :return: ``True`` if the dataset was extracted properly and ``False`` otherwise.
        """
        path = data_dir / contents['filename']
        if not path.exists():
            # File is missing
            return False
        if path.stat().st_size != contents['size']:
            return False
        return True


class _LzmaExtractor(Extractor):
    """Extractor that handles lzma compressed files. Capable of handling files like: ``.xz``, ``.txt.xz``, and
    ``.csv.xz``.
    """

    def extract(self, path: pathlib.Path, data_dir: pathlib.Path, file_list_file: pathlib.Path) -> None:
        """Attempt to extract the lzma compressed file. Save metadata about the file in the downloaded dataset in
        ``file_list_file``.

        :param path: Path to the lzma file.
        :param data_dir: Path to the data dir to extract the data file to.
        :file_list_file: Path to the file that stores metadata of the file in the downloaded dataset.
        :raises lzma.LZMAError: The lzma file was unable to be read.
        :raises OSError: The extracted file is empty.
        """
        try:
            mylzma = lzma.open(path)
            extracted_file_name = path.stem
            with mylzma, open(data_dir / extracted_file_name, 'wb') as f_out:
                shutil.copyfileobj(mylzma, f_out)
        except lzma.LZMAError as e:
            raise lzma.LZMAError(f'Failed to uncompress lzma file "{path}"\ncaused by:\n{e}')
        extracted_fp = data_dir / extracted_file_name

        FileListFileContents = Dict[str, Union[int, str]]
        contents: FileListFileContents = {}
        metadata: Dict[str, Union[str, FileListFileContents]] = {}

        metadata['type'] = 'xz'
        contents['filename'] = extracted_file_name
        contents['size'] = extracted_fp.stat().st_size
        if contents['size'] == 0:
            raise OSError(f'The extracted file {extracted_file_name} is empty.')
        metadata['contents'] = contents

        with open(file_list_file, mode='w') as f:
            json.dump(metadata, f, indent=2)

    def verify_extraction(self, data_dir: pathlib.Path, contents: dict) -> bool:
        """Verify the file was extracted properly using the metadata saved in ``file_list_file``.

        :param data_dir: Path to the data dir containing the extracted file.
        :contents: Dict obtained from ``file_list_file`` with metadata of the file in the downloaded dataset.
        :return: ``True`` if the dataset was extracted properly and ``False`` otherwise.
        """
        path = data_dir / contents['filename']
        if not path.exists():
            # File is missing
            return False
        if path.stat().st_size != contents['size']:
            return False
        return True


# Keys based on ftype returned by mimetypes.guess_type
archives = {
    'application/x-tar': _TarExtractor(),
    'application/zip': _ZipExtractor()
}

# Keys based on fencoding returned by mimetypes.guess_type
compressions = {
    'gzip': _GzipExtractor(),
    'bzip2': _Bzip2Extractor(),
    'xz': _LzmaExtractor()
}

extractor_map = {**archives, **compressions}
read_errors = (tarfile.ReadError, zipfile.BadZipFile, _BadGzipFile, _BadBzip2File, lzma.LZMAError)


# We first run the extractor determined by guess_type
# If that returns an error or guess_type doesn’t know the type try all extractors
# If none of the extractors work raise an error that says file type unsupported
def extract_data_files(path: pathlib.Path, data_dir: pathlib.Path, file_list_file: pathlib.Path) -> None:
    """Choose extractor based on filetype and extract the data files.

    :param path: Path to the dataset to extract.
    :param data_dir: Path to the data dir to extract the data file to.
    :param file_list_file: Path to the file that stores the list of files in the downloaded dataset.
    :raises RuntimeError: Dataset filetype is not (yet) supported.
    """

    # mimetypes.guess_type doesn't accept path-like objects until python 3.8
    ftype, fencoding = mimetypes.guess_type(path.name)

    # 1. Check if mimetypes.guess_type guesses a working extractor
    if any(key in extractor_map.keys() for key in (ftype, fencoding)):
        # Check if file is an archive, otherwise file must be a compressed flat file
        if ftype in archives:
            extractor = archives[ftype]
        elif fencoding in compressions:
            extractor = compressions[fencoding]
        try:
            extractor.extract(path, data_dir, file_list_file)
        except read_errors:
            pass
        else:
            return

    # 2. Otherwise try all extractors and see if one works
    for extractor in extractor_map.values():
        try:
            extractor.extract(path, data_dir, file_list_file)
        except read_errors:
            pass
        else:
            return

    # 3. Otherwise assume unsupported flat file or compression/archive type
    raise RuntimeError('Filetype not (yet) supported')


def verify_data_files(data_dir: pathlib.Path, file_list_file: pathlib.Path) -> bool:
    """Verify the files were extracted properly using the metadata saved in ``file_list_file``.

    :param data_dir: Path to the data dir containing the extracted files.
    :param file_list_file: Path to the file containing the list of files in the downloaded dataset.
    :return: ``True`` if the dataset was extracted properly and ``False`` otherwise.
    """

    with open(file_list_file, mode='r') as f:
        metadata = json.load(f)
    extractor = extractor_map[metadata['type']]
    return extractor.verify_extraction(data_dir, metadata['contents'])
