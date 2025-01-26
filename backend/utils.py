def sort_object_list_by_key(data, key):
    """Sort a list of objects by a specific key."""
    return sorted(data, key=lambda x: getattr(x, key))

def snake_to_camel(snake_str):
    """Convert snake_case to camelCase."""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def convert_dict_keys_to_camel_case(data):
    """Convert dictionary keys from snake_case to camelCase."""
    if isinstance(data, dict):
        return {snake_to_camel(key): convert_dict_keys_to_camel_case(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_dict_keys_to_camel_case(item) for item in data]
    else:
        return data