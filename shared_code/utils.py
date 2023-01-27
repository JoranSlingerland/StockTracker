"""General utility functions"""

def get_unique_items(items, key_to_filter):
    """Get unique items from list of dictionaries by key"""
    output_list = []
    for item in items:
        output_list.append(item[key_to_filter])
    return list(dict.fromkeys(output_list))
