"""General utility functions"""


def get_unique_items(items, key_to_filter):
    """Get unique items from list of dictionaries by key"""
    output_list = []
    for item in items:
        output_list.append(item[key_to_filter])
    return list(dict.fromkeys(output_list))


def get_weighted_average(data: list, weight: list) -> float:
    """Get weighted average"""
    return float(sum(a * b for a, b in zip(data, weight)) / sum(weight))


def add_meta_data_to_stock_data(stock_data, container):
    """Add meta data to stock data"""
    meta_data = list(container.read_all_items())
    for stock in stock_data:
        filtered_meta_data = [x for x in meta_data if x["symbol"] == stock["symbol"]]
        stock["meta"] = filtered_meta_data[0]
    return stock_data
