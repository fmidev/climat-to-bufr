"""
This module separates keys and values.
"""
from eccodes import CODES_MISSING_DOUBLE

def get_keys(row_with_key_value_pairs):
    """
    This funktion gets the keys and sets them in a array
    Input "row_with_key_value_pairs" is one observation,
    which includes key/value pairs.
    """
    number_of_pairs = len(row_with_key_value_pairs)
    keys = []
    for i in range(0, number_of_pairs):
        key_value = row_with_key_value_pairs[i]
        key = key_value[0]
        keys.append(key)

    return keys

def get_values(row_with_key_value_pairs):
    """
    This funktion gets the values and sets them in an array.
    Input "row_with_key_value_pairs" is one observation,
    which includes key/value pairs.
    """
    number_of_pairs = len(row_with_key_value_pairs)
    values = []
    for i in range(0, number_of_pairs):
        key_value = row_with_key_value_pairs[i]
        value = key_value[1]
        if value == '/':
            value = str(CODES_MISSING_DOUBLE)
        values.append(value)

    return values

def are_all_the_rows_similar(rows):
    """
    This function checks if all the rows are the same.
    """
    number_of_rows = len(rows)
    answer = True
    for i in range(0, number_of_rows - 1):
        row_a = rows[i]
        row_b = rows[i+1]
        if row_a != row_b:
            answer = False

    return answer

def longest_row(rows):
    """
    This functions check the longest row from rows.
    """
    number_of_rows = len(rows)
    longest = 0
    for i in range(0, number_of_rows - 1):
        l_a = len(rows[i])
        l_b = len(rows[i+1])
        if l_b > l_a:
            longest = i + 1
    return longest
  