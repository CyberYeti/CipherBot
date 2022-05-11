import json, time, requests, threading, random
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
def GetQuote():
    #response = requests.get("https://zenquotes.io/api/random")
    response = requests.get("https://api.quotable.io/random")
    jsonData = json.loads(response.text)
    quoteData = {'q': jsonData['content'], 'a': jsonData['author']}
    return quoteData

quotes = []
minQuotes = 100
def RefillQuotes():
    while True:
        if len(quotes) < 100:
            quotes.append(GetQuote())
        else:
            time.sleep(1)

quoteRefillThread = threading.Thread(target=RefillQuotes)
quoteRefillThread.start()

def NextQuote():
    return quotes.pop()
#endregion

#region Cipher Methods
ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
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

#region Discord Bot Commands
async def CaesarCipher(message):
    quote = NextQuote()
    plaintext = quote['q']
    encrypted,shift = EncryptCaesar(plaintext)
    author = quote['a']
    await message.channel.send(f"**Decrypt this quote from {author} encrypted with the caesar cipher a shift of {shift}.**\n{encrypted}")

async def RandQuote(message):
    quote = NextQuote()
    await message.channel.send(f"{quote['q']} -{quote['a']}")

async def HelpCommand(message):
    text = "The available commands are:"
    for key in CMDS:
        text += f"\nc.{key}"
    await message.channel.send(text)

#endregion

#region Discord Bot
client = discord.Client()

CMD_HEADER = "c."
CMDS = {
    "help": HelpCommand,
    "quote": RandQuote,
    "caesar": CaesarCipher
}

@client.event
async def on_ready():
    print(f"{client.user} is now online")

@client.event
async def on_message(message):
    if message.author == client.user: return
    
    content = message.content
    author = str(message.author)
    channel = message.channel

    if content.startswith(CMD_HEADER):
        command = content[len(CMD_HEADER):]
        if command in CMDS:
            await CMDS[command](message)
        else:
            await channel.send(f"Unknown command called. Please type c.help for a list of commands.")

client.run(TOKEN)
#endregion