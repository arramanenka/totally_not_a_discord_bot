import os
import re
import shutil
from pathlib import Path
from random import choice, shuffle, sample

from discord.utils import get


class PickAPersonGame:

    def __init__(self) -> None:
        super().__init__()
        self.queue_of_confessions = []
        self.participants = set()
        self.current_confession = None
        self.joking_reveal_start = [
            'It was me, Dio!', 'It\'sa me, Mario.', 'No clue who it was.',
            'Well, of course I know who it was. It was me.', 'Idk.', 'It was Sam.'
        ]
        self.current_confession_index = -1
        self.people_per_confession_guess_amount = 0
        self.start_channel = None

    async def start(self, start_message):
        self.start_channel = start_message.channel
        confessions = PickAPersonGame.read_confessions()
        for person, confessions in confessions.items():
            await self.on_new_confessions(person, confessions)
        confession_amount = len(self.queue_of_confessions)
        shuffle(self.queue_of_confessions)
        await start_message.channel.send(f'Hehe, starting up new pick-a-person game. '
                                         f'{confession_amount} confessions were made.\n'
                                         f'To reveal who was a person, that confessed, write \'game_reveal\'.\n '
                                         f'To move to the next confession, write \'game_next\'.\n'
                                         f'To move to the previous confession, write \'game_prev\'.\n'
                                         f'To get current confession question again, \'game_current\'')

    async def on_new_confessions(self, person, confessions, notify=False):
        member = get(self.start_channel.members, id=int(person))
        if member is None:
            return
        person_name = member.nick
        self.participants.add(person_name)
        for confession in confessions:
            self.queue_of_confessions.append((confession, person_name))
        people_amount = len(self.participants)
        if people_amount == 1:
            self.people_per_confession_guess_amount = 1
        elif people_amount > 3:
            self.people_per_confession_guess_amount = 3
        else:
            self.people_per_confession_guess_amount = people_amount
        if notify:
            await self.start_channel.send('Someone new made a confession')

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
        possible_people = set()
        possible_people.add(self.current_confession[1])
        while len(possible_people) != self.people_per_confession_guess_amount:
            possible_people.add(sample(self.participants, 1)[0])
        await channel.send(
            f'Someone told me: {self.current_confession[0]}\n'
            f'It can be any of {sample(self.participants, len(self.participants))}')

    @staticmethod
    async def process_direct(message, game_object=None):
        if message.content.startswith('Forgive me daddy, for I have sinned:'):
            confession = message.content.replace('Forgive me daddy, for I have sinned:', '').strip()
            print(f'{message.author} made a confession.')
            directory = Path('pick-a-person')
            if not directory.is_dir():
                directory.mkdir()
            with open(f'pick-a-person/{message.author.id}.txt', mode='a+', encoding='utf-8') as file:
                file.write(f'\"{confession}\"\n')
            if game_object is not None:
                await game_object.on_new_confessions(message.author.id, [confession], True)
            await message.channel.send("I forgive you.")
        elif message.content.startswith('what have I done?'):
            if not Path(f'pick-a-person/{message.author.id}.txt').is_file():
                await message.channel.send('Your soul is clear of sins.')
                return
            with open(f'pick-a-person/{message.author.id}.txt', mode='r+', encoding='utf-8') as file:
                lines = file.readlines()
            if lines:
                await message.channel.send(''.join(lines))
            else:
                await message.channel.send('Your soul is clear of sins.')
        elif message.content.startswith('only God can judge me, not you'):
            Path(f'pick-a-person/{message.author.id}.txt').unlink()
            await message.channel.send('That is true. I release your sins')
        elif message.content.startswith('help'):
            await message.channel.send('If you want to play pick-a-person, you can either '
                                       'make a confession, by \'Forgive me daddy, for I have sinned: [your message]\''
                                       '\nOr get your current confessions with \'what have I done?\'\n'
                                       'You can also make me forget your sins with \'only God can judge me, not you\'.'
                                       '\nHowever, you should note, that I might not forget it,'
                                       ' if pick-a-person is running')

    @staticmethod
    def read_confessions():
        result = dict()
        your_path = 'pick-a-person'
        for file in os.listdir(your_path):
            with open(os.path.join(your_path, file), 'r') as f:
                person_id = re.sub(r'.*pick-a-person.', '', f.name).strip().replace('.txt', '')
                for x in f:
                    result.setdefault(person_id, []).append(x)
        return result

    @staticmethod
    def delete_all_confessions():
        shutil.rmtree('pick-a-person')
        pass
