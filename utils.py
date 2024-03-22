import os


def capitalize_full_name(string):
    """
    Capitalize the first letter of every word in a string.

    Parameters:
    string (str): The input string.

    Returns:
    str: The string with the first letter of every word capitalized.
    """
    words = string.split()
    capitalized_words = [word.capitalize() for word in words]
    result = " ".join(capitalized_words)
    return result


def get_extension_from_file_name(file_name: str):
    # TODO: добавить проверку на правильное имя файла
    file_name_split = file_name.lower().split(".")
    if len(file_name_split) < 1:
        raise ValueError("File does not have extension")
    else:
        return file_name_split[-1]

