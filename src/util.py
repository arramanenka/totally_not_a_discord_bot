import re

import flag
import pycountry


def insert_flags_from_nick(flag_dict, nick):
    flags = find_flags(nick)
    added_flags = []
    for user_flag in set(flags):
        country = pycountry.countries.get(alpha_2=user_flag)
        if country is None:
            if user_flag == 'EA':
                country = pycountry.countries.get(alpha_2='ES')
            elif user_flag == 'CP':
                country = pycountry.countries.get(alpha_2='FR')
            else:
                print(f'{user_flag} not found :(')
                continue
        elif country.alpha_3 == 'PRI':
            country = pycountry.countries.get(alpha_2='US')
        country_name = country.alpha_3
        if country_name not in added_flags:
            added_flags.append(country_name)
            flag_dict.setdefault(country_name, 0)
            flag_dict[country_name] = flag_dict[country_name] + 1


def find_flags(flag_string):
    if flag_string is None:
        return []
    reformat_flag_string = flag.dflagize(re.sub(r':.*:', '', flag_string))
    return re.findall(r':(\w+):', reformat_flag_string)


def check_presence(item, key, dictionary):
    if dictionary is None or key not in dictionary:
        return False
    return item in dictionary[key]
