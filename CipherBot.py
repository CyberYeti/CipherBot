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
    alphOnly = ""
    for char in text.lower():
        if char in ALPHABET:
            i = ALPHABET.index(char)
            encrypted += ALPHABET[i+(shift-26)]
            alphOnly += char
        else:
            encrypted += char
    return (alphOnly, encrypted, shift)
    
#endregion

#region Discord Bot Commands
async def AnswerCommand(message, args):
    await message.channel.send(f"You have submitted the answer \"{args}\"")

async def CaesarCipher(message, args):
    quote = NextQuote()
    plaintext = quote['q']
    alphOnly,encrypted,shift = EncryptCaesar(plaintext)
    author = quote['a']
    await message.channel.send(f"**Decrypt this quote from {author} encrypted with the caesar cipher a shift of {shift}.**\n{encrypted}")

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
CMDS = {
    "help": HelpCommand,
    "quote": RandQuote,
    "caesar": CaesarCipher,
    "answer": AnswerCommand
}


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
        for cmd in CMDS:
            if cmd == commandText: #If the message only contains the commands
                command = cmd
                break
            elif commandText.startswith(f"{cmd} "): #If the command contains args, the command and the args should be seperated by a space
                command = cmd
                args = commandText[len(command)+1:]
                break

        if command != "": #If the command is one the bot recognizes 
            await CMDS[command](message,args)
        else: #If the bot doesn't reconize the command
            await channel.send(f"Unknown command called. Please type c.help for a list of commands.")

client.run(TOKEN)
#endregion