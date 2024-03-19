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
