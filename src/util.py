import re

import flag


def find_flags(flag_string):
    reformat_flag_string = flag.dflagize(re.sub(r':.*:', '', flag_string))
    all_flags = re.findall(r':(.*):', reformat_flag_string)
    return all_flags
