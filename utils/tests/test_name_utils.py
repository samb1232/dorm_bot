import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from utils.name_utils import capitalize_full_name


class TestCapitalizeFullName:

    def test_capitalize_single_word(self):
        assert capitalize_full_name("иван") == "Иван"

    def test_capitalize_two_words(self):
        assert capitalize_full_name("иван иванов") == "Иван Иванов"

    def test_capitalize_three_words(self):
        assert capitalize_full_name("иван иванов иванович") == "Иван Иванов Иванович"

    def test_capitalize_already_capitalized(self):
        assert capitalize_full_name("Иван Иванов") == "Иван Иванов"

    def test_capitalize_mixed_case(self):
        assert capitalize_full_name("иВаН ИвАнОв") == "Иван Иванов"

    def test_capitalize_uppercase(self):
        assert capitalize_full_name("ИВАН ИВАНОВ") == "Иван Иванов"

    def test_capitalize_empty_string(self):
        assert capitalize_full_name("") == ""

    def test_capitalize_with_extra_spaces(self):
        assert capitalize_full_name("иван  иванов") == "Иван Иванов"

    def test_capitalize_with_leading_trailing_spaces(self):
        result = capitalize_full_name(" иван иванов ")
        assert result == "Иван Иванов"

    def test_capitalize_single_character_words(self):
        assert capitalize_full_name("а б в") == "А Б В"

    def test_capitalize_with_hyphenated_name(self):
        assert capitalize_full_name("иван-петр") == "Иван-петр"

    def test_capitalize_latin_characters(self):
        assert capitalize_full_name("john smith") == "John Smith"

    def test_capitalize_numbers(self):
        assert capitalize_full_name("test123 name456") == "Test123 Name456"

    def test_capitalize_long_name(self):
        long_name = "иван петр алексей дмитрий сергей"
        expected = "Иван Петр Алексей Дмитрий Сергей"
        assert capitalize_full_name(long_name) == expected

    def test_capitalize_cyrillic_yo_character(self):
        assert capitalize_full_name("фёдор") == "Фёдор"
        assert capitalize_full_name("алёна семёнова") == "Алёна Семёнова"
