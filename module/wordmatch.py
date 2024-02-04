from thefuzz import process
from thefuzz import fuzz
import sys
try:
    import ocr
except:
    from module import ocr

with open('config/anime-list.txt') as file:
    user_animes = [line.strip() for line in file.readlines()]

with open('config/character-list.txt') as file:
    user_character = [line.strip() for line in file.readlines()]

def fuzzy(cards: list[str], user_list: list[str]):
    for card in cards:
        best_match = process.extractOne(card, user_list, scorer=fuzz.partial_token_sort_ratio)
        print(best_match)
        if best_match[1] >= 90:
            card_index = cards.index(card)
            break
        else:
            card_index = -1
    return card_index

if __name__ == '__main__':
    cards = ocr.get_card('anime', sys.argv[1])
    print(fuzzy(cards, user_animes))