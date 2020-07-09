import os
from pathlib import Path
from random import choice


class PickAPersonGame:

    def __init__(self) -> None:
        super().__init__()
        self.queue_of_confessions = []

        confessions = PickAPersonGame.read_confessions()
        for person, confessions in confessions.items():
            for confession in confessions:
                self.queue_of_confessions.append((confession, person))

        self.participants = [key for key in confessions]
        self.current_confession = None
        self.joking_reveal_start = [
            'It was me, Dio!', 'It\'sa me, Mario.', 'No clue who it was.',
            'Well, of course I know who it was. It was me.', 'Idk.', 'It was Sam.'
        ]
        self.current_confession_index = -1

    async def start(self, start_message):
        length = len(self.queue_of_confessions)
        if length == 0:
            await start_message.channel.send(f'Could not start pick-a-person cuz there are no confessions :(')
            return False
        else:
            await start_message.channel.send(f'Hehe, starting up new pick-a-person game. '
                                             f'{length} confessions were made. '
                                             f'To reveal who was a person, that confessed, write \'game_reveal\'. '
                                             f'To move to the next confession, write \'game_next\'. '
                                             f'To move to the previous confession, write \'game_prev\'.\n'
                                             f'To get current confession question again, \'game_current\'')
            return True

    async def process_game_request(self, message, actual_message):
        if actual_message.startswith('game_reveal'):
            await message.channel.send(f'{choice(self.joking_reveal_start)} Jk, it was {self.current_confession[1]}')
        elif actual_message.startswith('game_next'):
            await self.next_confession(message)
        elif actual_message.startswith('game_prev'):
            await self.prev_confession(message)
        elif actual_message.startswith('game_current'):
            await self.print_confession(message.channel)

    async def prev_confession(self, message):
        if self.current_confession_index > 0:
            self.current_confession_index -= 1
            self.current_confession = self.queue_of_confessions[self.current_confession_index]
            await self.print_confession(message.channel)
        else:
            await message.channel.send('Can\'t go before zero :(')

    async def next_confession(self, message):
        if len(self.queue_of_confessions) - 1 > self.current_confession_index:
            self.current_confession_index += 1
            self.current_confession = self.queue_of_confessions[self.current_confession_index]
            await self.print_confession(message.channel)
        else:
            await message.channel.send('I guess that is it! queue is empty.')

    async def print_confession(self, channel):
        await channel.send(f'Someone told me: {self.current_confession[0]}')

    @staticmethod
    async def process_direct(message):
        if message.content.startswith('Forgive me father, for I have sinned:'):
            confession = message.content.replace('Forgive me father, for I have sinned:', '').strip()
            print(f'{message.author} made a confession: {confession}')
            directory = Path('/pick-a-person')
            if not directory.is_dir():
                directory.mkdir()
            with open(f'/pick-a-person/{message.author.id}.txt', mode='a+', encoding='utf-8') as file:
                file.write(f'\"{confession}\"\n')
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
                                       '\nOr get your current confessions with \'what have I done?\'\n'
                                       'You can also make me forget your sins with \'only God can judge me, not you\'.'
                                       '\nHowever, you should note, that I might not forget it,'
                                       ' if pick-a-person is running')

    @staticmethod
    def read_confessions():
        result = dict()
        your_path = '/pick-a-person'
        for file in os.listdir(your_path):
            with open(os.path.join(your_path, file), 'r') as f:
                person_id = f.name.replace('.txt', '')
                for x in f:
                    result.setdefault(person_id, []).append(x)
        return result
