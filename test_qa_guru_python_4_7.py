import csv
import zipfile
from pathlib import Path

import openpyxl
import pytest
import requests
from PyPDF2 import PdfReader

file_links = {
    'xlsx': 'https://github.com/qa-guru/qa_guru_python_4_7/raw/master/file_example_XLSX_10.xlsx',
    'pdf': 'https://github.com/qa-guru/qa_guru_python_4_7/raw/master/docs-pytest-org-en-latest.pdf',
    'csv': 'https://github.com/qa-guru/qa_guru_python_4_7/raw/master/username.csv'
}

resources_path = Path("resources")
resources_path.mkdir(exist_ok=True)


@pytest.fixture(scope="module")
def download_and_zip_files():
    zip_path = resources_path / "archive.zip"
    with zipfile.ZipFile(zip_path, mode='w') as archive:
        for file_type, url in file_links.items():
            response = requests.get(url)
            local_file = resources_path / f"{file_type}.{file_type}"
            local_file.write_bytes(response.content)
            archive.writestr(local_file.name, response.content)

    return zip_path


def test_files_content(download_and_zip_files):
    with zipfile.ZipFile(download_and_zip_files) as archive:
        for file_type, _ in file_links.items():
            file_name = f"{file_type}.{file_type}"
            original_file = resources_path / file_name
            zipped_file = archive.open(file_name)

            if file_type == "pdf":
                original_pdf = PdfReader(original_file)
                zipped_pdf = PdfReader(zipped_file)
                assert len(original_pdf.pages) == len(zipped_pdf.pages)

            elif file_type == "xlsx":
                original_wb = openpyxl.load_workbook(original_file)
                zipped_wb = openpyxl.load_workbook(zipped_file)
                assert original_wb.active['A1'].value == zipped_wb.active['A1'].value

            elif file_type == "csv":
                original_csv = list(csv.reader(open(original_file, 'r', encoding='utf-8')))
                zipped_csv = list(csv.reader(zipped_file.read().decode('utf-8').splitlines()))
                assert original_csv == zipped_csv
