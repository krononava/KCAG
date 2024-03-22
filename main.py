import discord
import asyncio
import random
import time
from module import ocr
from module import command
from module import formatter
from module import wordmatch
from module import config


# random words used to generate random messages
words_list = ['a', 'aa', 'aaa', 'aaron', 'ab', 'abandoned', 'abc', 'aberdeen', 'abilities', 'ability', 'able', 'aboriginal', 'abortion', 'about', 'above', 'abraham', 'abroad', 'abs', 'absence', 'absent', 'absolute', 'absolutely', 'absorption', 'abstract', 'abstracts', 'abu', 'abuse', 'ac', 'academic', 'academics', 'academy', 'acc', 'accent', 'accept', 'acceptable', 'acceptance', 'accepted', 'accepting', 'accepts', 'access', 'accessed',  'act', 'acting', 'action', 'actions', 'activated', 'activation', 'active', 'actively', 'activists', 'activities', 'activity', 'actor', 'actors', 'actress', 'acts', 'actual', 'actually', 'acute', 'ad', 'ada', 'adam', 'adams', 'xbox', 'xerox', 'xhtml', 'xi', 'xl', 'xml', 'xnxx', 'xp', 'xx', 'xxx', 'y', 'ya', 'yacht', 'yahoo', 'yale', 'yamaha', 'yang', 'yard', 'yards', 'yarn', 'ye', 'yea', 'yeah', 'year', 'yearly', 'years', 'yeast', 'yellow', 'yemen', 'yen', 'yes', 'yesterday', 'yet', 'yield', 'yields', 'yn', 'yo', 'yoga', 'york', 'yorkshire', 'you', 'young', 'younger', 'your', 'yours', 'yourself', 'youth', 'yr', 'yrs', 'yu', 'yugoslavia', 'yukon', 'z', 'za', 'zambia', 'zdnet', 'zealand', 'zen', 'zero', 'zimbabwe', 'zinc', 'zip', 'zoloft', 'zone', 'zones', 'zoning', 'zoo', 'zoom', 'zoophilia', 'zope', 'zshops', 'zu', 'zum', 'zus'] 

config.init_files()

with open('config/anime-list.txt') as file:
    user_animes = [line.strip() for line in file.readlines()]

with open('config/character-list.txt') as file:
    user_characters = [line.strip() for line in file.readlines()]

with open('config/account-token.txt') as file:
    user_tokens = [line.strip() for line in file.readlines()]

with open('config/grab-channel.txt') as file:
    grab_channel_id = int(file.read())

with open('config/spam-channel.txt') as file:
    spam_channel_id = int(file.read())

async def message_spam(spam_channel):
    while True: 
        sentence = " ".join([random.choice(words_list) for number_of_words in range(random.randint(2, 4))])
        await spam_channel.send(sentence)
        await asyncio.sleep(random.randint(5, 6))

async def drop_scheduler(accs):
    num_of_acc = len(user_tokens)
    drop_cooldown = 30 # minutes
    waitsec_per_acc = (drop_cooldown * 60) / num_of_acc
    await asyncio.sleep(10)
    while True:
        for acc in accs:
            await acc.send_drop()
            await asyncio.sleep(waitsec_per_acc)

class Main(discord.Client):

    async def on_connect(self):
        print('Logged on as', self.user)
        self._can_grab = False    
        self.grab_channel = self.get_channel(grab_channel_id)
        self.spam_channel = self.get_channel(spam_channel_id)

        await self.grab_channel.send("kcd")

        task_spam = asyncio.create_task(message_spam(self.spam_channel))
        await task_spam


    async def send_drop(self):
        await self.grab_channel.send('kd')

    async def on_message(self, message):

        # determine the grab cooldown
        if str(message.author) == 'Karuta#1280' and message.channel.id == grab_channel_id:     

            for embed in message.embeds:
                # read only the reply for cooldown message eg."k!cd"
                if "Showing cooldowns" in embed.description:
                    start_index = embed.description.find("`")

                    # check if there is a cooldown time in the message
                    if start_index != -1:
                        end_index = embed.description.find("`", start_index + 2)
                        cooldown_string = embed.description[start_index + 1:end_index]
                        space_index = cooldown_string.find(" ")
                        duration = int(cooldown_string[:space_index])

                        # wait for the specified cooldown time before allowing account to collect card
                        if cooldown_string[space_index + 1] == "m":
                            await asyncio.sleep((duration * 60) + 60)
                        elif cooldown_string[space_index + 1] == "s":
                            await asyncio.sleep(duration)

                    self._can_grab = True


            if message.content == 'I\'m dropping 3 cards since this server is currently active!':
                if self._can_grab == True:
                    characters = ocr.get_card("character", message.attachments[0].url)
                    animes = ocr.get_card("anime", message.attachments[0].url)
                    response = formatter.get_textblock(characters)
                    await self.grab_channel.send(response)
                    response = formatter.get_textblock(animes)
                    await self.grab_channel.send(response)

                    card_index = wordmatch.fuzzy(characters, user_characters)

                    if card_index == -1:
                        card_index = wordmatch.fuzzy(animes, user_animes)

                    if card_index != -1:
                        print("\nSpecified anime found.")

                        card_choice = card_index + 1
                        if card_choice == 1:
                            await message.add_reaction('1️⃣')

                        elif card_choice == 2:
                            await message.add_reaction('2️⃣')

                        elif card_choice == 3:
                            await message.add_reaction('3️⃣')

                        print(f"{card_choice} Card Claimed ", time.strftime("%I:%M %p") )

                        self._can_grab = False
                        print("Going into cooldown.")
                        await asyncio.sleep(600)
                        print("Cooldown is off.")
                        self._can_grab = True
            
            if 'took the' in message.content and self._can_grab == True and self.user.mentioned_in(message):
                self._can_grab = False
                print("Going into cooldown.")
                await self.grab_channel.send('Manually grabbed card, going into cooldown.')
                await asyncio.sleep(600)
                print("Cooldown is off.")
                self._can_grab = True

        if message.author.id == self.user.id and message.channel.id == grab_channel_id:
            response = command.parser(message.content)
            if response != None:
                response = formatter.get_textblock(response)
                await self.grab_channel.send(response)


class SpamBot(discord.Client):

    async def on_connect(self):
        print('Logged on as', self.user)
        self.spam_channel = self.get_channel(spam_channel_id)

        # fake activity to generate card drop
        task_spam = asyncio.create_task(message_spam(self.spam_channel))
        # task_drop = asyncio.create_task(auto_drop(self.grab_channel))
        await task_spam
        # await task_drop

    async def send_drop(self):
        await self.grab_channel.send('kd')


# Discount accounts instance creation
num_of_acc = len(user_tokens)
accounts = []
for i in range(num_of_acc):
    if i == 0: 
        acc_obj = Main()
    else:
        acc_obj = SpamBot()
    accounts.append(acc_obj)


task_list = []
loop = asyncio.get_event_loop()
for i in range(num_of_acc):
    account = accounts[i]
    token = user_tokens[i]
    task = loop.create_task(account.start(token, reconnect = True))
    task_list.append(task)

drop_task = loop.create_task(drop_scheduler(accounts))
task_list.append(drop_task)
gathered = asyncio.gather(*task_list)
loop.run_until_complete(gathered)