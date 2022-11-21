import json, time, requests, threading, random, string
import discord
import CipherMethods as cm

#region Get Token
f = __file__.split("\\")
f = f[:len(f)-1]
directoryPath = "\\".join(f)

with open(f'{directoryPath}\\Info.json', 'r') as f:
    data = json.load(f)

TOKEN = data['Token']
#endregion

#region Quote Getter
def GetQuote(min, max):
    #response = requests.get("https://zenquotes.io/api/random")
    response = requests.get(f"https://api.quotable.io/random?minLength={min}&maxLength={max}")
    jsonData = json.loads(response.text)
    quoteData = {'q': jsonData['content'], 'a': jsonData['author']}
    return quoteData

quotes = {
    'caesar': [],
    'affine': [],
    'aristocrat': [],
    'patristocrat': [],
    'morse': [],
    'railfence': [],
    'morbit': [],
    'binary': []
}
quoteParams = {
    'caesar': (100,125),
    'affine': (50,100),
    'aristocrat': (80,130),
    'patristocrat': (80,150),
    'morse': (20,50),
    'railfence': (20,50),
    'morbit': (20,50),
    'binary': (20,50)
}

minQuotes = 10
def RefillQuotes():
    while True:
        for quoteList,params in zip(quotes.values(), quoteParams.values()):
            if len(quoteList) < minQuotes:
                quoteList.append(GetQuote(params[0], params[1]))
            else:
                time.sleep(1)

quoteRefillThread = threading.Thread(target=RefillQuotes)
quoteRefillThread.start()

def NextQuote(cipher):
    if cipher in quotes:
        return quotes[cipher].pop()
    else:
        print("Invalid Cipher Name")
#endregion

async def EditCipherEmbed(message, outcome):
    prevMessage = activeCiphers[str(message.author)]['msg']
    prevEmbed = prevMessage.embeds[0]
    prevEmbed.description += f"\n\n**The answer was:**\n{activeCiphers[str(message.author)]['ans']}"
    if outcome == 'f':
        prevEmbed.set_footer(text="Failed Cipher")
        prevEmbed.color = GIVEUP_COLOR
    elif outcome == 's':
        prevEmbed.set_footer(text="Solved Cipher")
        prevEmbed.color = SOLVED_COLOR
    await prevMessage.edit(embed=prevEmbed)

#region Discord Bot Commands
SOLVED_COLOR = 0x15f705
ACTIVE_COLOR = 0x00bbff
GIVEUP_COLOR = 0xf70b05

ALPHABET = [*'abcdefghijklmnopqrstuvwxyz']

async def AnswerCommand(message, args):
    if str(message.author) in activeCiphers:
        inputtedAns = args.translate(str.maketrans("", "", string.whitespace))
        if inputtedAns == "":
            await message.channel.send(f"Enter an answer to be checked")
            return

        info = activeCiphers[str(message.author)]
        if cm.AlphabetOnly(inputtedAns) == cm.AlphabetOnly(info['ans']): #Correct Answer
            cipherType = info['cipher']
            secondsTaken = time.time() - info['time']
            if secondsTaken > (60*60):
                await message.channel.send(f"You got it correct!\nIt took you over an hour to solve this {cipherType} cipher.")
            else:
                secTaken = round((secondsTaken % 60) * 100) / 100
                minTaken = int((secondsTaken - secondsTaken % 60)/60)

                timeTaken = f"{minTaken} min {secTaken} sec" if minTaken != 0 else f"{secTaken} sec"

                await message.channel.send(f"You got it correct!\nIt took you {timeTaken} to solve this {cipherType} cipher.")
            await EditCipherEmbed(message, 's')
            del activeCiphers[str(message.author)]
            return
        else: # Wrong Answer
            await message.channel.send(f"You got it wrong")
            return
    else:
        await message.channel.send(f"You don't have an active cipher")

async def PatristocratCipher(message, args):
    quote = NextQuote('patristocrat')
    plaintext = quote['q']
    encrypted,key = cm.EncryptPatristocrat(plaintext)
    author = quote['a']

    if str(message.author) in activeCiphers:
        await EditCipherEmbed(message, 'f')

    embedMsg = discord.Embed(title=f"{str(message.author)}'s Cipher", color=ACTIVE_COLOR)
    embedMsg.set_footer(text="Active Cipher")
    embedMsg.description = f"**Decrypt this quote by {author} encrypted using the patristocrat cipher.**\n{encrypted}"

    activeCiphers[str(message.author)] = {'ans': plaintext}
    msg = await message.channel.send(embed=embedMsg)
    activeCiphers[str(message.author)]['msg'] = msg
    activeCiphers[str(message.author)]['cipher'] = "Patristocrat Cipher"
    activeCiphers[str(message.author)]['time'] = time.time()

async def AristocratCipher(message, args):
    quote = NextQuote('aristocrat')
    plaintext = quote['q']
    encrypted,key = cm.EncryptAristocrat(plaintext)
    author = quote['a']

    if str(message.author) in activeCiphers:
        await EditCipherEmbed(message, 'f')

    embedMsg = discord.Embed(title=f"{str(message.author)}'s Cipher", color=ACTIVE_COLOR)
    embedMsg.set_footer(text="Active Cipher")
    embedMsg.description = f"**Decrypt this quote by {author} encrypted using the aristocrat cipher.**\n{encrypted}"

    activeCiphers[str(message.author)] = {'ans': plaintext}
    msg = await message.channel.send(embed=embedMsg)
    activeCiphers[str(message.author)]['msg'] = msg
    activeCiphers[str(message.author)]['cipher'] = "Aristocrat"
    activeCiphers[str(message.author)]['time'] = time.time()

async def CaesarCipher(message, args):
    quote = NextQuote('caesar')
    plaintext = quote['q']
    encrypted,shift = cm.EncryptCaesar(plaintext)
    author = quote['a']

    if str(message.author) in activeCiphers:
        await EditCipherEmbed(message, 'f')

    embedMsg = discord.Embed(title=f"{str(message.author)}'s Cipher", color=ACTIVE_COLOR)
    embedMsg.set_footer(text="Active Cipher")

    problemType = random.randint(0,1)
    if problemType == 0: #encrypt problem
        embedMsg.description = f"**Decrypt this quote by {author} encrypted using the caesar cipher with an unknown shift.**\n{encrypted}"
        activeCiphers[str(message.author)] = {'ans': plaintext}
    elif problemType == 1: #decrypt problem
        embedMsg.description = f"**Encrypt this quote by {author} using the caesar cipher with an shift of {shift}.**\n{plaintext}"
        activeCiphers[str(message.author)] = {'ans': encrypted}
    msg = await message.channel.send(embed=embedMsg)
    activeCiphers[str(message.author)]['msg'] = msg
    activeCiphers[str(message.author)]['cipher'] = "Caesar"
    activeCiphers[str(message.author)]['time'] = time.time()

async def AffineCipher(message, args):
    quote = NextQuote('affine')
    plaintext = quote['q']
    encrypted,multiplier,shift = cm.EncryptAffine(plaintext)
    author = quote['a']

    if str(message.author) in activeCiphers:
        await EditCipherEmbed(message, 'f')

    embedMsg = discord.Embed(title=f"{str(message.author)}'s Cipher", color=ACTIVE_COLOR)
    embedMsg.set_footer(text="Active Cipher")

    problemType = random.randint(0,2)
    if problemType == 0: #encrypt problem
        embedMsg.description = f"**Decrypt this quote by {author} encrypted using the affine cipher with the key ({multiplier},{shift}).**\n{encrypted}"
        activeCiphers[str(message.author)] = {'ans': plaintext}
    elif problemType == 1: #decrypt problem
        embedMsg.description = f"**Encrypt this quote by {author} using the affine using the key ({multiplier},{shift}).**\n{plaintext}"
        activeCiphers[str(message.author)] = {'ans': encrypted}
    elif problemType == 2: #decrypt using given cipher plain pairs
        lettersInPlain = []
        for letter in plaintext:
            if letter in ALPHABET and letter not in lettersInPlain:
                lettersInPlain.append(letter)
        selectedLetters = random.sample(lettersInPlain, 2)

        embedMsg.description = f"**Decrypt this quote by {author} encrypted using the affine cipher. Ciphertext \'{ALPHABET[((ALPHABET.index(selectedLetters[0])*multiplier)+shift) % 26]}\' decodes to \'{selectedLetters[0]}\' and ciphertext \'{ALPHABET[((ALPHABET.index(selectedLetters[1])*multiplier)+shift) % 26]}\' decodes to \'{selectedLetters[1]}\'.**\n{encrypted}"
        activeCiphers[str(message.author)] = {'ans': plaintext}
    msg = await message.channel.send(embed=embedMsg)
    activeCiphers[str(message.author)]['msg'] = msg
    activeCiphers[str(message.author)]['cipher'] = "Affine"
    activeCiphers[str(message.author)]['time'] = time.time()

async def MorseCipher(message, args):
    quote = NextQuote('morse')
    plaintext = quote['q']
    encrypted = cm.EncryptMorse(plaintext)
    author = quote['a']

    if str(message.author) in activeCiphers:
        await EditCipherEmbed(message, 'f')

    embedMsg = discord.Embed(title=f"{str(message.author)}'s Cipher", color=ACTIVE_COLOR)
    embedMsg.set_footer(text="Active Cipher")
    embedMsg.description = f"**Decrypt this quote by {author} encrypted using morse code.**\n{encrypted}"

    activeCiphers[str(message.author)] = {'ans': plaintext}
    msg = await message.channel.send(embed=embedMsg)
    activeCiphers[str(message.author)]['msg'] = msg
    activeCiphers[str(message.author)]['cipher'] = "Morse"
    activeCiphers[str(message.author)]['time'] = time.time()

async def RailFenceCipher(message, args):
    quote = NextQuote('railfence')
    plaintext = quote['q']
    author = quote['a']

    plainTextLetters = cm.AlphabetOnly(plaintext).lower()
    # data = EncryptRailfence(plaintext)
    encrypted,rails,offset = cm.EncryptRailfence(plaintext)

    # Create Discord Message
    if str(message.author) in activeCiphers:
        await EditCipherEmbed(message, 'f')

    embedMsg = discord.Embed(title=f"{str(message.author)}'s Cipher", color=ACTIVE_COLOR)
    embedMsg.set_footer(text="Active Cipher")

    num = random.randint(1,2)
    if num == 1: # decode with known rails
        embedMsg.description = f"**Decode this quote by {author} that was encoded using the Railfence cipher with {rails} rails. There may be an offset.**\n"
    elif num == 2: # decode with unknown rails
        wordSeg = ""
        rint = random.randint(0, len(plainTextLetters)-1)
        if rint+5 > len(plainTextLetters)-1:
            wordSeg = plainTextLetters[rint-5:rint]
        else:
            wordSeg = plainTextLetters[rint:rint+5]
        embedMsg.description = f"**Decode this quote by {author} that was encoded using the Railfence cipher with between 2 and 5 rails inclusive. The plaintext contains the string {wordSeg}. There may be an offset.**\n"
    embedMsg.description += encrypted

    activeCiphers[str(message.author)] = {'ans': plaintext}
    msg = await message.channel.send(embed=embedMsg)
    activeCiphers[str(message.author)]['msg'] = msg
    activeCiphers[str(message.author)]['cipher'] = "Railfence"
    activeCiphers[str(message.author)]['time'] = time.time()

async def MorbitCipher(message, args):
    quote = NextQuote('morbit')
    plaintext = quote['q']
    author = quote['a']
    encrypted,key = cm.EncryptMorbit(plaintext)

    embedMsg = discord.Embed(title=f"{str(message.author)}'s Cipher", color=ACTIVE_COLOR)
    embedMsg.set_footer(text="Active Cipher")
    embedMsg.description = f"**Decode this quote by {author} that was encoded using the Morbit cipher. You are told "

    nums = [*"123456789"]
    random.shuffle(nums)
    numHints = random.randint(4,5)
    for i in range(numHints):
        embedMsg.description += f"{nums[i]} = {key[nums[i]]}, "
    embedMsg.description = embedMsg.description.removesuffix(", ")
    embedMsg.description += "**\n"

    embedMsg.description += encrypted

    activeCiphers[str(message.author)] = {'ans': plaintext}
    msg = await message.channel.send(embed=embedMsg)
    activeCiphers[str(message.author)]['msg'] = msg
    activeCiphers[str(message.author)]['cipher'] = "Morbit"
    activeCiphers[str(message.author)]['time'] = time.time()

async def BinaryCipher(message, args):
    quote = NextQuote('binary')
    plaintext = quote['q']
    author = quote['a']
    encrypted = cm.EncryptBinary(plaintext)

    embedMsg = discord.Embed(title=f"{str(message.author)}'s Cipher", color=ACTIVE_COLOR)
    embedMsg.set_footer(text="Active Cipher")
    embedMsg.description = f"**Decode this quote by {author} that was encoded using the Binary cipher.**\n{encrypted}"

    activeCiphers[str(message.author)] = {'ans': plaintext}
    msg = await message.channel.send(embed=embedMsg)
    activeCiphers[str(message.author)]['msg'] = msg
    activeCiphers[str(message.author)]['cipher'] = "Binary"
    activeCiphers[str(message.author)]['time'] = time.time()

async def HelpCommand(message, args):
    def GeneralCMD():
        embedMsg = discord.Embed(title=f"Available Commands", color=ACTIVE_COLOR)
        embedMsg.set_footer(text="Type c.help [command] for more info")

        description = ""
        for gName,group in CMD_GROUPING.items():
            description += f"\n\n**{gName}**"
            for key in group:
                description += f"\n{key}"

        embedMsg.description = description
        return embedMsg
    def SpecificCMD():
        if args not in CMD_INFO:
            embedMsg = discord.Embed(title=f"Unknown Command", color=GIVEUP_COLOR)
            embedMsg.description = f"Sorry, the command '{args}' was not recognised"
            return embedMsg

        embedMsg = discord.Embed(title=f"{args} Command", color=ACTIVE_COLOR)

        description = f"**Info:**\n{CMD_INFO[args]}\n\n**Alternative Names:**"
        for name in CMD_NAMES[args]:
            description += f"\n{name}"

        embedMsg.description = description
        return embedMsg

    embedMsg = discord.Embed(title=f"Blank", color=ACTIVE_COLOR)
    if args == "":
        embedMsg = GeneralCMD()
    else:
        embedMsg = SpecificCMD()

    await message.channel.send(embed=embedMsg)

#endregion

#region Discord Bot
client = discord.Client()

CMD_HEADER = "c."

# Grouping to make the Help Command More Organized
CMD_GROUPING = {
    "General": ["help", "answer"],
    "Text Ciphers": ["aristocrat", "patristocrat"],
    "Math Ciphers": ["caesar", "affine"],
    "Wierd Ciphers": ["morse", "railfence", "morbit", "binary"]
}

# Any avalible command names for a specific command
CMD_NAMES = {
    "help": ["help", "h"],
    "caesar": ["caesar"],
    "answer": ["answer", "a", "ans"],
    "affine": ["affine"],
    "aristocrat": ["aristocrat", "aristo"],
    "patristocrat": ["patristocrat", "patristo"],
    "morse": ["morse"],
    "railfence": ["railfence", "rail"],
    "morbit": ["morbit"],
    "binary": ["binary", "bin"]
}

# Connect command to function 
CMDS = {
    "help": HelpCommand,
    "caesar": CaesarCipher,
    "answer": AnswerCommand,
    "affine": AffineCipher,
    "aristocrat": AristocratCipher,
    "patristocrat": PatristocratCipher,
    "morse": MorseCipher,
    "railfence": RailFenceCipher,
    "morbit": MorbitCipher,
    "binary": BinaryCipher
}

CMD_INFO ={
    "help": "Gives a list of commands and more information on specific commands.\nCommand List: c.help\nSpecific Info: c.help [command]",
    "caesar": "Generates a Caesar cipher problem for you to solve.",
    "answer": "A command used to submit an answer and check if you answered it correctly.\nSubmit Answer: c.answer [answer]",
    "affine": "Generates an Affine cipher problem for you to solve.",
    "aristocrat": "Generates an Aristocrat cipher problem for you to solve.",
    "patristocrat": "Generates a Patristocrat cipher problem for you to solve.",
    "morse": "Generates a Morse code problem for you to solve.",
    "railfence": "Generates a RailFence cipher problem for you to solve.",
    "morbit": "Generates a Morbit cipher problem for you to solve.",
    "binary": "Generates a Binary cipher problem for you to solve. (Uses A and B)"
}

activeCiphers = {}


@client.event
async def on_ready():
    print(f"{client.user} is now online")

@client.event
async def on_message(message):
    #Do not react to this Bot's messages
    if message.author == client.user: return
    
    #Get some information about the message
    content = message.content
    author = str(message.author)
    channel = message.channel

    #Check if the message is a bot command or a random message
    if content.startswith(CMD_HEADER):
        #Check if the command is a valid command
        commandText = content[len(CMD_HEADER):]
        command = ""
        args = ""
        for cmd, names in CMD_NAMES.items():
            for name in names:
                if name == commandText.lower(): #If the message only contains the commands
                    command = cmd
                    break
                elif commandText.lower().startswith(f"{name} "): #If the command contains args, the command and the args should be seperated by a space
                    command = cmd
                    args = commandText[len(name)+1:]
                    break

        if command != "": #If the command is one the bot recognizes 
            await CMDS[command](message,args)
        else: #If the bot doesn't reconize the command
            await channel.send(f"Unknown command called. Please type c.help for a list of commands.")

client.run(TOKEN)
#endregion