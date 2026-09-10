import random

# List of random Filipino street vendor / referee lines
DIALOGUES = [
    "Sige na, Pusta na! Saan banda ang bola?",
    "Mabilis ang kamay, pero mas mabilis ang mata!",
    "Tingnan mong mabuti, baka malagpasan ka...",
    "Saan ang taya mo, boss? Kaliwa, gitna, o kanan?",
    "Huli man daw at magaling, naihahabol din!"
]

WIN_DIALOGUES = [
    "Aba, magaling! Tama ka!",
    "Nakita mo 'yun ah! Panalo!",
    "Ang swerte mo naman! Ikaw na!",
    "Nadali mo! Panalo ka!",
    "Wow, ang talas ng mata mo!"
]

LOSE_DIALOGUES = [
    "Naku, wala dyan! Bawi ka next time.",
    "Sayang, hindi 'yan ang tama.",
    "Bilis ng kamay ko 'no? Talo ka ngayon.",
    "Wala, bokya! Subok ulit!",
    "Mali! Try again!"
]

def get_random_dialogue():
    return random.choice(DIALOGUES)

def get_win_dialogue():
    return random.choice(WIN_DIALOGUES)

def get_lose_dialogue():
    return random.choice(LOSE_DIALOGUES)