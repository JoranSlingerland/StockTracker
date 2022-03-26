'''List to string'''
# pylint: disable=logging-fstring-interpolation

import logging

def main(list_to_convert):
    """convert list to string"""
    logging.debug(f"Converting list: {list_to_convert} to string")
    return ", ".join(str(e) for e in list_to_convert)
