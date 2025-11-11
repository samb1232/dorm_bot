import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
from utils.file_utils import get_extension_from_file_name


class TestGetExtensionFromFileName:
    """Test suite for get_extension_from_file_name function"""

    def test_get_extension_simple_pdf(self):
        """Test getting extension from simple PDF filename"""
        assert get_extension_from_file_name("document.pdf") == "pdf"

    def test_get_extension_simple_jpg(self):
        """Test getting extension from JPG filename"""
        assert get_extension_from_file_name("photo.jpg") == "jpg"

    def test_get_extension_simple_png(self):
        """Test getting extension from PNG filename"""
        assert get_extension_from_file_name("image.png") == "png"

    def test_get_extension_jpeg(self):
        """Test getting extension from JPEG filename"""
        assert get_extension_from_file_name("picture.jpeg") == "jpeg"

    def test_get_extension_uppercase(self):
        """Test that uppercase extensions are converted to lowercase"""
        assert get_extension_from_file_name("FILE.PDF") == "pdf"
        assert get_extension_from_file_name("IMAGE.PNG") == "png"
        assert get_extension_from_file_name("PHOTO.JPG") == "jpg"

    def test_get_extension_mixed_case(self):
        """Test getting extension with mixed case"""
        assert get_extension_from_file_name("Document.PdF") == "pdf"
        assert get_extension_from_file_name("Image.JpG") == "jpg"

    def test_get_extension_multiple_dots(self):
        """Test getting extension from filename with multiple dots"""
        assert get_extension_from_file_name("my.file.name.pdf") == "pdf"
        assert get_extension_from_file_name("archive.tar.gz") == "gz"

    def test_get_extension_with_path(self):
        """Test getting extension from filename with path"""
        assert get_extension_from_file_name("/path/to/file.pdf") == "pdf"
        assert get_extension_from_file_name("../relative/path/document.txt") == "txt"

    def test_get_extension_common_document_formats(self):
        """Test common document format extensions"""
        assert get_extension_from_file_name("document.doc") == "doc"
        assert get_extension_from_file_name("document.docx") == "docx"
        assert get_extension_from_file_name("spreadsheet.xls") == "xls"
        assert get_extension_from_file_name("spreadsheet.xlsx") == "xlsx"
        assert get_extension_from_file_name("presentation.ppt") == "ppt"
        assert get_extension_from_file_name("presentation.pptx") == "pptx"

    def test_get_extension_archive_formats(self):
        """Test archive format extensions"""
        assert get_extension_from_file_name("archive.zip") == "zip"
        assert get_extension_from_file_name("archive.rar") == "rar"
        assert get_extension_from_file_name("archive.7z") == "7z"

    def test_get_extension_text_file(self):
        """Test getting extension from text file"""
        assert get_extension_from_file_name("readme.txt") == "txt"

    def test_get_extension_no_extension(self):
        """Test filename without extension (edge case)"""
        # This should return the filename itself as there's no dot
        result = get_extension_from_file_name("filename")
        assert result == "filename"

    def test_get_extension_dot_at_start(self):
        """Test filename starting with dot (hidden file)"""
        assert get_extension_from_file_name(".gitignore") == "gitignore"
        assert get_extension_from_file_name(".env.local") == "local"

    def test_get_extension_only_dot(self):
        """Test filename with only a dot"""
        result = get_extension_from_file_name(".")
        assert result == ""

    def test_get_extension_ends_with_dot(self):
        """Test filename ending with dot"""
        result = get_extension_from_file_name("filename.")
        assert result == ""

    def test_get_extension_long_extension(self):
        """Test filename with unusually long extension"""
        assert get_extension_from_file_name("file.verylongextension") == "verylongextension"

    def test_get_extension_numbers_in_extension(self):
        """Test extension with numbers"""
        assert get_extension_from_file_name("backup.bak2") == "bak2"

    def test_get_extension_special_characters_in_name(self):
        """Test filename with special characters"""
        assert get_extension_from_file_name("чек_оплата.pdf") == "pdf"
        assert get_extension_from_file_name("файл-123.jpg") == "jpg"

    def test_get_extension_spaces_in_name(self):
        """Test filename with spaces"""
        assert get_extension_from_file_name("my file name.pdf") == "pdf"
        assert get_extension_from_file_name("document with spaces.docx") == "docx"

    def test_get_extension_cyrillic_filename(self):
        """Test Cyrillic filename with extension"""
        assert get_extension_from_file_name("документ.pdf") == "pdf"
        assert get_extension_from_file_name("фото.jpg") == "jpg"

    def test_get_extension_check_receipt_format(self):
        """Test format used in payment_functions for check receipts"""
        # Based on actual usage: "5А_иван_иванов_unique123.pdf"
        assert get_extension_from_file_name("5А_иван_иванов_unique123.pdf") == "pdf"
        assert get_extension_from_file_name("5Б_петр_петров_unique456.jpg") == "jpg"

    def test_get_extension_single_char_extension(self):
        """Test single character extension"""
        assert get_extension_from_file_name("file.c") == "c"
        assert get_extension_from_file_name("script.r") == "r"

    def test_get_extension_empty_string_raises_error(self):
        """Test that empty string raises ValueError or returns empty"""
        # The function checks len < 1, which would be True for empty list after split
        # But "".split(".") returns [""], which has length 1
        result = get_extension_from_file_name("")
        assert result == ""
