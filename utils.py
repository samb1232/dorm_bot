def capitalize_full_name(string):
    words = string.split()
    capitalized_words = [word.capitalize() for word in words]
    result = " ".join(capitalized_words)
    return result


def get_extension_from_file_name(file_name: str):
    file_name_split = file_name.lower().split(".")
    if len(file_name_split) < 1:
        raise ValueError("File does not have extension")
    else:
        return file_name_split[-1]

