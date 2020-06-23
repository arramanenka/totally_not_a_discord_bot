import re

import flag


def find_flags(flag_string):
    if flag_string is None:
        return []
    reformat_flag_string = flag.dflagize(re.sub(r':.*:', '', flag_string))
    return re.findall(r':(\w+):', reformat_flag_string)


def check_presence(item, key, dictionary):
    if dictionary is None:
        return False
    if key not in dictionary:
        return False
    return item in dictionary[key]
