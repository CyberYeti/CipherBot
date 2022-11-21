import random

ALPHABET = [*'abcdefghijklmnopqrstuvwxyz']

def AlphabetOnly(text):
    res = [char for char in text.lower() if char in ALPHABET]
    return ''.join(res)

def EncryptAristocrat(text):
    def CreateAristoKey():
        key = {}
        scrambled = ALPHABET.copy()
        random.shuffle(scrambled)

        sameKeys = []
        for letter in zip(ALPHABET, scrambled):
            if letter[0] == letter[1]:
                sameKeys.append(letter[0])
            else:
                key[letter[0]] = letter[1]
        
        if len(sameKeys) == 1:
            alphIndex = ALPHABET.index(sameKeys[0])
            if sameKeys[0] != key[ALPHABET[alphIndex-1]]:
                key[sameKeys[0]] = key[ALPHABET[alphIndex-1]]
                key[ALPHABET[alphIndex-1]] = sameKeys[0]
            else:
                key[sameKeys[0]] = key[ALPHABET[alphIndex-2]]
                key[ALPHABET[alphIndex-2]] = sameKeys[0]
        elif len(sameKeys) > 1:
            for i,val in enumerate(sameKeys):
                key[val] = sameKeys[i-1]
        return key
    
    key = CreateAristoKey()
    encrypted = ""
    for char in text.lower():
        if char in key:
            encrypted += key[char]
        else:
            encrypted += char
    return (encrypted, key)

def EncryptPatristocrat(text):
    aristo,key = EncryptAristocrat(text)
    encrypted = ""
    for i,char in enumerate(AlphabetOnly(aristo)):
        if (i+1)%5 == 1:
            encrypted += " "
        encrypted += char
    encrypted = encrypted[1:]
    return (encrypted, key)

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
    
affineMultipliers = [1,3,5,7,9,11,15,17,19,21,23,25]

def EncryptAffine(text):
    multiplier = random.choice(affineMultipliers)
    shift = random.randint(0,25)

    encrypted = ""
    for char in text.lower():
        if char in ALPHABET:
            index = ALPHABET.index(char)
            encrypted += ALPHABET[((index * multiplier) + shift)%26]
        else:
            encrypted += char

    return (encrypted, multiplier, shift)

morseKey = {
    'a':".-",
    'b':"-...",
    'c':"-.-.",
    'd':"-..",
    'e':".",
    'f':"..-.",
    'g':"--.",
    'h':"....",
    'i':"..",
    'j':".---",
    'k':"-.-",
    'l':".-..",
    'm':"--",
    'n':"-.",
    'o':"---",
    'p':".--.",
    'q':"--.-",
    'r':".-.",
    's':"...",
    't':"-",
    'u':"..-",
    'v':"...-",
    'w':".--",
    'x':"-..-",
    'y':"-.--",
    'z':"--.. ",
}
def EncryptMorse(text):
    encrypted = ""
    letter = True
    for char in text.lower(): 
        if char in morseKey:
            encrypted += f"{morseKey[char]}x"
            letter = True
        else:
            if letter:
                encrypted += "x"
            letter = False
    while encrypted[-1] == 'x':
        encrypted = encrypted[:-1]
    return encrypted

def EncryptRailfence(text, numRailsRange=(2, 5)):
    plainTextLetters = AlphabetOnly(text).lower()
    numRails = random.randint(numRailsRange[0], numRailsRange[1])
    offset = random.randint(0,numRails*2-3)
    rails=[]
    for i in range(numRails):
        rails.append("")
    counter = offset
    increment = 1
    if counter > numRails-1:
        increment = -1
        counter = numRails*2-2-counter
    elif counter == numRails-1:
        increment = -1

    for char in plainTextLetters:
        rails[counter] += char
        counter += increment
        if counter == 0 or counter == numRails-1:
            increment *= -1

    encrypted = ""
    for rail in rails:
        encrypted += rail
    return (encrypted, numRails, offset)


morbitPairs = [
    "..",
    ".-",
    ".x",
    "-.",
    "--",
    "-x",
    "x.",
    "x-",
    "xx"
]

def EncryptMorbit(text):
    morse = EncryptMorse(text)
    if len(morse)%2 == 1:
        morse+="x"

    nums = [*"123456789"]
    random.shuffle(nums)

    encrypted = ""
    for i in range(0,len(morse),2):
        pair = morse[i]
        pair += morse[i+1]
        encrypted+=nums[morbitPairs.index(pair)]
        encrypted+=" "
    encrypted = encrypted.removesuffix(" ")
    
    key = {
        "1":morbitPairs[nums.index("1")],
        "2":morbitPairs[nums.index("2")],
        "3":morbitPairs[nums.index("3")],
        "4":morbitPairs[nums.index("4")],
        "5":morbitPairs[nums.index("5")],
        "6":morbitPairs[nums.index("6")],
        "7":morbitPairs[nums.index("7")],
        "8":morbitPairs[nums.index("8")],
        "9":morbitPairs[nums.index("9")],
    }

    return (encrypted, key)

def EncryptBinary(text):
    key = {
        "a": 'aaaaa',
        "b": 'aaaab',
        "c": 'aaaba',
        "d": 'aaabb',
        "e": 'aabaa',
        "f": 'aabab',
        "g": 'aabba',
        "h": 'aabbb',
        "i": 'abaaa',
        "j": 'abaaa',
        "k": 'abaab',
        "l": 'ababa',
        "m": 'ababb',
        "n": 'abbaa',
        "o": 'abbab',
        "p": 'abbba',
        "q": 'abbbb',
        "r": 'baaaa',
        "s": 'baaab',
        "t": 'baabb',
        "u": 'baabb',
        "v": 'baabb',
        "w": 'babaa',
        "x": 'babab',
        "y": 'babba',
        "z": 'babbb'
    }
    encrypted = ""
    for char in AlphabetOnly(text).lower():
        encrypted += key[char]

    return encrypted