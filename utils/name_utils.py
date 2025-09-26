def capitalize_full_name(string):
    words = string.split()
    capitalized_words = [word.capitalize() for word in words]
    result = " ".join(capitalized_words)
    return result
