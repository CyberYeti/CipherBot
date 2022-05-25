import json, time, requests, threading, random, string
import discord

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
    'caesar': []
}
quoteParams = {
    'caesar': (100,125)
}

minQuotes = 25
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

#region Cipher Methods
ALPHABET = 'abcdefghijklmnopqrstuvwxyz'

def AlphabetOnly(text):
    res = [char for char in text.lower() if char in ALPHABET]
    return ''.join(res)

def EncryptCaesar(text):
    shift = random.randint(1,25)
    encrypted = ""
    for char in text.lower():
        if char in ALPHABET:
            i = ALPHABET.index(char)
            encrypted += ALPHABET[i+(shift-26)]
        else:
            encrypted += char
    return (encrypted, shift)
    
#endregion

async def EditCipherEmbed(message, outcome):
    prevMessage = activeCiphers[str(message.author)]['msg']
    prevEmbed = prevMessage.embeds[0]
    if outcome == 'f':
        prevEmbed.set_footer(text="Given Up Cipher")
        prevEmbed.color = GIVEUP_COLOR
    elif outcome == 's':
        prevEmbed.set_footer(text="Solved Cipher")
        prevEmbed.color = SOLVED_COLOR
    await prevMessage.edit(embed=prevEmbed)

#region Discord Bot Commands
SOLVED_COLOR = 0x15f705
ACTIVE_COLOR = 0x00bbff
GIVEUP_COLOR = 0xf70b05

async def AnswerCommand(message, args):
    if str(message.author) in activeCiphers:
        inputtedAns = args.translate(str.maketrans("", "", string.whitespace))
        if inputtedAns == "":
            await message.channel.send(f"Enter an answer to be checked")
            return

        info = activeCiphers[str(message.author)]
        if AlphabetOnly(inputtedAns) == AlphabetOnly(info['ans']):
            await message.channel.send(f"You got it correct!")
            await info['msg'].edit(content=info['msg'].content+"\nCipher Solved")
            await EditCipherEmbed(message, 's')
            del activeCiphers[str(message.author)]
            return
        else:
            await message.channel.send(f"You got it wrong")
            return
    else:
        await message.channel.send(f"You don't have an active cipher")

async def CaesarCipher(message, args):
    quote = NextQuote('caesar')
    plaintext = quote['q']
    encrypted,shift = EncryptCaesar(plaintext)
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

async def RandQuote(message, args):
    quote = NextQuote()
    await message.channel.send(f"{quote['q']} -{quote['a']}")

async def HelpCommand(message, args):
    text = "The available commands are:"
    for key in CMDS:
        text += f"\nc.{key}"
    await message.channel.send(text)

#endregion

#region Discord Bot
client = discord.Client()

CMD_HEADER = "c."
CMD_NAMES = {
    "help": ["help", "h"],
    "quote": ["quote", "q"],
    "caesar": ["caesar", "c"],
    "answer": ["answer", "a", "ans"]
}
CMDS = {
    "help": HelpCommand,
    "quote": RandQuote,
    "caesar": CaesarCipher,
    "answer": AnswerCommand
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