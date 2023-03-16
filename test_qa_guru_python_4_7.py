import hashlib
import io
import os
import zipfile

import requests


def download_file(url):
    response = requests.get(url)
    response.raise_for_status()
    return io.BytesIO(response.content)


def get_filename_from_url(url):
    return url.split("/")[-1]


def calculate_checksum(file):
    file.seek(0)
    file_hash = hashlib.md5()
    for chunk in iter(lambda: file.read(4096), b""):
        file_hash.update(chunk)
    return file_hash.hexdigest()


def test_files():
    urls = [
        "https://github.com/qa-guru/qa_guru_python_4_7/raw/master/file_example_XLSX_10.xlsx",
        "https://github.com/qa-guru/qa_guru_python_4_7/raw/master/docs-pytest-org-en-latest.pdf",
        "https://github.com/qa-guru/qa_guru_python_4_7/raw/master/username.csv",
    ]

    files = [(download_file(url), get_filename_from_url(url)) for url in urls]
    with zipfile.ZipFile("resources/archive.zip", mode="w") as archive:
        for file, filename in files:
            archive.writestr(filename, file.getvalue())

    assert os.path.exists("resources/archive.zip"), "The archive was not created"

    with zipfile.ZipFile("resources/archive.zip", mode="r") as archive:
        for file, filename in files:
            file_checksum = calculate_checksum(file)
            with archive.open(filename, "r") as archived_file:
                archived_file_checksum = calculate_checksum(archived_file)
                assert file_checksum == archived_file_checksum, f"Checksum mismatch for {filename}"
