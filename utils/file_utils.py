def get_extension_from_file_name(file_name: str):
    if not file_name:
        return ""
    if file_name == ".":
        return ""
    if "." not in file_name:
        return ""
    if file_name.startswith("."):
        parts = file_name[1:].split(".")
        if len(parts) == 1:
            return ""
        else:
            return parts[-1].lower()
    parts = file_name.lower().split(".")
    if len(parts) == 1:
        return ""
    if file_name.endswith("."):
        return ""
    return parts[-1]
