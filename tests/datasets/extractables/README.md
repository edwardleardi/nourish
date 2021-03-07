This directory contains test extractable archives and compressed files used to test the extractors found in `_extractors.py`.

* `test-zerobyte.csv.*`: Files used to test compression extractors (e.g. gzip, bzip2, lzma) to make sure they can detect zero-byte data files.
* `test.tar*`: Tarball files used to test `_TarExtractor`. Tarballs contain two files: `test.csv` and `test.txt`.
* `test.zip`: Zip file used to test `_ZipExtractor`. Zip contains two files: `test.csv` and `test.txt`.
* `test.txt.*`: Compressed txt files used to test compression extractors (e.g. gzip, bzip2, lzma).
* `test-csv-bz2.csv.xz`: Bzip2 compressed csv file with purposefully wrong extension meant to test `extract_data_files`.
* `test-csv-gz`: Gzip compressed csv file purposefully missing the extension in the file name to test `extract_data_files`.
* `test-tar-gz`: Gzip compressed tarball purposefully missing the extension in the file name to test `extract_data_files`.
