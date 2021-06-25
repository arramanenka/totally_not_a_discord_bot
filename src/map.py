import os

from datawrapper import Datawrapper
from io import StringIO
import pandas as pd
import pycountry

from src.util import find_flags


class MapGenerator:

    def __init__(self) -> None:
        super().__init__()
        # TODO: decouple implementation from datawrapper
        self.data_wrapper = Datawrapper(access_token=os.getenv('DATAWRAPPER_TOKEN'))

    @staticmethod
    async def save_guild_member_map(guild, use_iso=True):
        flag_dict = {}
        await guild.chunk()
        for m in guild.members:
            if not m.bot:
                flags = find_flags(m.nick)
                added_flags = []
                for flag in set(flags):
                    country = pycountry.countries.get(alpha_2=flag)
                    if country is None:
                        if flag == 'EA':
                            country = pycountry.countries.get(alpha_2='ES')
                        elif flag == 'CP':
                            country = pycountry.countries.get(alpha_2='FR')
                        else:
                            print(f'{flag} not found :(')
                            continue
                    elif country.alpha_3 == 'PRI':
                        country = pycountry.countries.get(alpha_2='US')
                    country_name = country.alpha_3
                    if country_name not in added_flags:
                        added_flags.append(country_name)
                        flag_dict.setdefault(country_name, 0)
                        flag_dict[country_name] = flag_dict[country_name] + 1
        results = []
        for key in sorted(flag_dict, key=flag_dict.get):
            result = f'\n{key if use_iso else pycountry.countries.get(alpha_3=key).name},{flag_dict[key]}'
            results.append(result)
        output = ''.join(results)
        with open(f'{guild.id}.csv', mode='w+', encoding='utf-8') as csv_file:
            csv_file.write('ISO-Code,count')
            csv_file.write(output)
        return output

    def update_datawrapper_map(self, guild_member_map):
        self.data_wrapper.add_data('ovAEX', data=pd.read_csv(StringIO(f'ISO-Code,count\n{guild_member_map}')))
        self.data_wrapper.publish_chart('ovAEX')
        self.data_wrapper.export_chart('ovAEX', filepath='ovAEX.png', width=666)
