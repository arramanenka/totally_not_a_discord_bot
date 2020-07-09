from pathlib import Path


class PickAPersonGame:
    async def process_game_request(self, message, actual_message):
        pass

    @staticmethod
    async def process_direct(message):
        if message.content.startswith('Forgive me father, for I have sinned:'):
            confession = message.content.replace('Forgive me father, for I have sinned:', '').strip()
            print(f'{message.author} made a confession: {confession}')
            directory = Path('/pick-a-person')
            if not directory.is_dir():
                directory.mkdir()
            with open(f'/pick-a-person/{message.author.id}.txt', mode='a+', encoding='utf-8') as file:
                file.write(f'\n\"{confession}\"')
            await message.channel.send("I forgive you.")
        elif message.content.startswith('what have I done?'):
            if not Path(f'/pick-a-person/{message.author.id}.txt').is_file():
                await message.channel.send('Your soul is clear of sins.')
                return
            with open(f'/pick-a-person/{message.author.id}.txt', mode='r+', encoding='utf-8') as file:
                lines = file.readlines()
            if lines:
                await message.channel.send(''.join(lines))
            else:
                await message.channel.send('Your soul is clear of sins.')
            pass
        elif message.content.startswith('only God can judge me, not you'):
            Path(f'/pick-a-person/{message.author.id}.txt').unlink()
            await message.channel.send('That is true. I release your sins')
        elif message.content.startswith('help'):
            await message.channel.send('If you want to play pick-a-person, you can either '
                                       'make a confession, by \'Forgive me father, for I have sinned: [your message]\''
                                       ' or get your current confessions with \'what have I done?\''
                                       ' you can also make me forget your sins with \'only God can judge me, not you\'.'
                                       'However, you should note, that I might not forget it,'
                                       ' if pick-a-person is running')
            pass
