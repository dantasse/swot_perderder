#!/usr/bin/env python

# Every so often (TBD), takes a food, messes its name up, grabs an image of
# that food, and makes a meme with the misspelled word, posts it to Twitter.

import argparse, random
from collections import defaultdict

# Lookup table to translate phones to letters.
phone_lookup = {
    'AA':['AH', 'AW', 'AR', 'ER', 'OH'],
    'AE':['A', 'AA', 'EH', 'AH'],
    'AH':['AH', 'EH', 'OH', 'UH', 'AR'],
    'AO':['AW', 'OH', 'UH'],
    'AW':['OW', 'OO', 'AW'],
    'AY':['I', 'IE', 'AY'],
    'B': ['B', 'P', 'D'],
    'CH':['CH', 'SH', 'K'],
    'D': ['D', 'T', 'TH'],
    'DH':['DH', 'TH'],
    'EH':['E', 'UH', 'ER', 'EH', 'I', 'O'],
    'ER':['ER', 'AR', 'OR'],
    'EY':['A', 'AE', 'EY'],
    'F': ['F', 'V'],
    'G': ['G', 'G', 'GH'],
    'HH':['H', 'H', 'CH'],
    'IH':['I', 'A', 'UH'],
    'IY':['I', 'EE', 'AY'],
    'JH':['J', 'G', 'Z'],
    'K': ['K', 'C'],
    'L': ['L', 'L', 'LL'],
    'M': ['M', 'N'],
    'N': ['N', 'M'],
    'NG':['NG', 'N', 'NN'],
    'OW':['O', 'OH', 'OW', 'YO'],
    'OY':['OY', 'OI', 'UI'],
    'P': ['P', 'B'],
    'R': ['R'],
    'S': ['S', 'S', 'SH', 'Z', 'Z'],
    'SH':['SH', 'CH'],
    'T': ['T', 'D', 'TH'],
    'TH':['TH', 'T', 'D'],
    'UH':['OO', 'UH', 'OU'],
    'UW':['OO', 'U', 'UE'],
    'V': ['V', 'B', 'F'],
    'W': ['W', 'V'],
    'Y': ['Y', 'EEY'],
    'Z': ['Z', 'ZH', 'TH'],
    'ZH':['ZH', 'SH', 'CH'],
}

# Given a phone (like "IY2" or "HH") returns letters that might somehow
# represent it in a word, in a goofy sort of way.
def get_letter(phone):
    phone = phone.strip('012') # Ignore stresses, at least for now.
    possible_letters = phone_lookup[phone][:] # Slice to copy.
    # Copy early letters to make them more likely.
    for i in range(len(possible_letters)):
        possible_letters.extend(possible_letters[0:i])
    return random.sample(possible_letters, 1)[0]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--foods_file', default='foods.txt')
    parser.add_argument('--pronouncing_dict_file',
        default='cmu_pronouncing_dict/cmudict-0.7b.txt')
    args = parser.parse_args()

    # Parse food list and pronunciation dictionary
    foods = [line.strip() for line in open(args.foods_file)]
    pronounce = defaultdict(list) # word -> list of pronunciations, each a list of phones.
    for line in open(args.pronouncing_dict_file):
        if line.startswith(';'):
            continue
        word = line.split('  ')[0]
        pronounce[word] = line.split('  ')[1].strip().split(' ')

    not_pronounced_words = [w for w in foods if w.split()[0].upper() not in pronounce]
    print 'unpronounced: ' + str(not_pronounced_words)

    # TODO connect to twitter to post
    # TODO pick out images, store locally I guess
    # TODO programmatically generate memes
    # TODO watermark memes
    for food in random.sample(foods, 10):
        print food
        for foodword in food.split(' '):
            letters = ''
            for phone in pronounce[foodword.upper()]:
                letters += get_letter(phone)
            print letters
