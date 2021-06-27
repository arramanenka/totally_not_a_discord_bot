from io import StringIO
from random import choice

import pandas as pd
import plotly.graph_objects as go
import pycountry
from plotly.graph_objs.layout import Title

from src.util import insert_flags_from_nick


class MapGenerator:

    def __init__(self) -> None:
        super().__init__()
        self.good_colors = ['teal', 'tealgrn', 'temps', 'algae', 'peach', 'darkmint']

    @staticmethod
    async def save_guild_member_map(guild, use_iso=True):
        flag_dict = {}
        await guild.chunk()
        for m in guild.members:
            if not m.bot:
                insert_flags_from_nick(flag_dict, m.nick)
        results = []
        for key in sorted(flag_dict, key=flag_dict.get):
            result = f'\n{key if use_iso else pycountry.countries.get(alpha_3=key).name},{flag_dict[key]}'
            results.append(result)
        output = ''.join(results)
        with open(f'{guild.id}.csv', mode='w+', encoding='utf-8') as csv_file:
            csv_file.write('ISO-Code,count')
            csv_file.write(output)
        return output

    def save_map_as_png(self, guild_member_map, file_name, title):
        df = pd.read_csv(StringIO(f'ISO-Code,count\n{guild_member_map}'))

        fig = go.Figure(
            data=go.Choropleth(
                locations=df['ISO-Code'],
                z=df['count'].astype(float),
                colorscale=choice(self.good_colors),
                autocolorscale=False,
                marker_line_color='white'
            ),
            layout=go.Layout(geo={
                'bgcolor': '#fffaf0',
                'landcolor': '#fffaf0'
            },
                title=Title(text=title, xanchor='center', x=0.5, yanchor='top', y=0.9,
                            font={"size": 40, "color": "Black"}),
                font={"size": 40, "color": "Grey"},
                titlefont={"size": 40, "color": "Grey"},
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            ))
        fig.write_image(file_name, width=3840, height=2160)
