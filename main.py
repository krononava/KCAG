import discord
import asyncio
import random
import time
from module import ocr
from module import command
from module import formatter
from multiprocessing import Process, Queue
from aiohttp import client_exceptions


def target(queue):
    # random words used to generate random messages
    words_list = ['a', 'aa', 'aaa', 'aaron', 'ab', 'abandoned', 'abc', 'aberdeen', 'abilities', 'ability', 'able', 'aboriginal', 'abortion', 'about', 'above', 'abraham', 'abroad', 'abs', 'absence', 'absent', 'absolute', 'absolutely', 'absorption', 'abstract', 'abstracts', 'abu', 'abuse', 'ac', 'academic', 'academics', 'academy', 'acc', 'accent', 'accept', 'acceptable', 'acceptance', 'accepted', 'accepting', 'accepts', 'access', 'accessed',  'act', 'acting', 'action', 'actions', 'activated', 'activation', 'active', 'actively', 'activists', 'activities', 'activity', 'actor', 'actors', 'actress', 'acts', 'actual', 'actually', 'acute', 'ad', 'ada', 'adam', 'adams', 'xbox', 'xerox', 'xhtml', 'xi', 'xl', 'xml', 'xnxx', 'xp', 'xx', 'xxx', 'y', 'ya', 'yacht', 'yahoo', 'yale', 'yamaha', 'yang', 'yard', 'yards', 'yarn', 'ye', 'yea', 'yeah', 'year', 'yearly', 'years', 'yeast', 'yellow', 'yemen', 'yen', 'yes', 'yesterday', 'yet', 'yield', 'yields', 'yn', 'yo', 'yoga', 'york', 'yorkshire', 'you', 'young', 'younger', 'your', 'yours', 'yourself', 'youth', 'yr', 'yrs', 'yu', 'yugoslavia', 'yukon', 'z', 'za', 'zambia', 'zdnet', 'zealand', 'zen', 'zero', 'zimbabwe', 'zinc', 'zip', 'zoloft', 'zone', 'zones', 'zoning', 'zoo', 'zoom', 'zoophilia', 'zope', 'zshops', 'zu', 'zum', 'zus'] 

    with open('config/anime-list.txt') as file:
        animes = [line.strip() for line in file.readlines()]

    with open('config/account-token.txt') as file:
        tokens = [line.strip() for line in file.readlines()]

    with open('config/grab-channel.txt') as file:
        grab_channel_id = int(file.read())

    with open('config/spam-channel.txt') as file:
        spam_channel_id = int(file.read())

    try:
        class Main(discord.Client):

            async def on_connect(self):
                print('Logged on as', self.user)
                self._can_grab = False    
                self.grab_channel = self.get_channel(grab_channel_id)
                self.spam_channel = self.get_channel(spam_channel_id)

                await self.grab_channel.send("kcd")

                # fake activity to generate card drop
                while True: 
                    sentence = " ".join([random.choice(words_list) for number_of_words in range(random.randint(2, 4))])
                    await self.spam_channel.send(sentence)
                    await asyncio.sleep(random.randint(5, 6))


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
                            cards = ocr.get_card("anime", message.attachments[0].url)
                            response = formatter.get_textblock(cards)
                            await self.grab_channel.send(response)

                            card_index = -1 # Default to card not found

                            for anime in cards:
                                if anime in animes:
                                    card_index = cards.index(anime)
                                    break

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
                    
                    if 'took the' in message.content and self._can_grab == True:
                        self._can_grab = False
                        print("Going into cooldown.")
                        await self.grab_channel.send('Manually grabbed card, going into cooldown.')
                        await asyncio.sleep(600)
                        print("Cooldown is off.")
                        self._can_grab = True

                if message.author.id == self.user.id:
                    response = command.parser(message.content)
                    if response != None:
                        response = formatter.get_textblock(response)
                        await self.grab_channel.send(response)


            # restart script when connection error
            async def on_error(self, on_connect):
                queue.put("Restart Script") 


        class SpamBot(discord.Client):

            async def on_connect(self):
                print('Logged on as', self.user)
                self.spam_channel = self.get_channel(spam_channel_id)

                # fake activity to generate card drop
                while True: 
                    sentence = " ".join([random.choice(words_list) for number_of_words in range(random.randint(2, 4))])
                    await self.spam_channel.send(sentence)
                    await asyncio.sleep(random.randint(5, 6))

            # restart script when connection error
            async def on_error(self, on_connect):
                queue.put("Restart Script") 


        # Discount accounts instance creation
        main_acc_index = 0
        num_of_acc = len(tokens)
        accounts = []
        for i in range(num_of_acc):
            if i == main_acc_index: 
                acc_obj = Main(guild_subscription_options=discord.GuildSubscriptionOptions.off())
            else:
                acc_obj = SpamBot(guild_subscription_options=discord.GuildSubscriptionOptions.off())
            accounts.append(acc_obj)


        task_list = []
        loop = asyncio.get_event_loop()
        for i in range(num_of_acc):
            account = accounts[i]
            token = tokens[i]
            task = loop.create_task(account.start(token))
            task_list.append(task)


        gathered = asyncio.gather(*task_list)
        loop.run_until_complete(gathered)

    except Exception as e:
        queue.put(e)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ConnectionError(Exception):
    "Raised when user has been disconnected from discord"
    pass


if __name__ == '__main__':
    while True:
        try:
            queue = Queue()
            process = Process(target=target, daemon=True, args=(queue,))
            process.start()
            print(f"\n{bcolors.WARNING}Process Started{bcolors.ENDC}\n")
            while True:
                exception = queue.get()
                if exception is not None:
                    print(exception)
                time.sleep(1)

        except:
            process.kill()
            time.sleep(1)