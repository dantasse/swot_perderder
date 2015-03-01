#!/usr/bin/env python

# Every so often (TBD), takes a food, messes its name up, grabs an image of
# that food, and makes a meme with the misspelled word, posts it to Twitter.

import argparse, random
from collections import defaultdict

syllable_lookup = {
    'AA':['AH', 'AW', 'AR', 'ER', 'OH'],
    'AE':['AA', 'EH', 'AH', 'A'],
    'AH':['AH', 'EH', 'OH', 'UH', 'AR'],
    'AO':['AW', 'OH', 'UH'],
    'AW':['OW', 'AYOW', 'OO'],
    'AY':['I', 'IE', 'AY'],
    'B': ['B', 'P'],
    'CH':['CH', 'SH', 'ZH'],
    'D': ['D', 'TH'],
    'DH':['DH', 'TH'],
    'EH':['E', 'ER', 'EH', 'I', 'O'],
    'ER':['ER', 'AR', 'OR'],
    'EY':['A', 'AE', 'EY'],
    'F': ['F', 'V'],
    'G': ['G', 'GH'],
    'HH':['H', 'CH'],
    'IH':['I', 'IH', 'YI'],
    'IY':['I', 'AY', 'YI'],
    'JH':['J', 'G', 'Z'],
    'K': ['K', 'C'],
    'L': ['L', 'LL'],
    'M': ['M', 'N'],
    'N': ['N', 'M'],
    'NG':['NG', 'N', 'NN'],
    'OW':['OH', 'O', 'OW', 'YO'],
    'OY':['OY', 'OI', 'UI'],
    'P': ['P', 'B'],
    'R': ['R', 'RR'],
    'S': ['S', 'SH', 'Z'],
    'SH':['SH', 'CH', 'ZH'],
    'T': ['T', 'TH', 'D'],
    'TH':['TH', 'T', 'D'],
    'UH':['OO', 'UH', 'OU'],
    'UW':['OO', 'U', 'UE'],
    'V': ['V', 'B', 'F'],
    'W': ['W', 'V'],
    'Y': ['Y', 'EEY'],
    'Z': ['Z', 'ZH', 'TH'],
    'ZH':['ZH', 'SH', 'CH'],
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--foods_file', default='foods.txt')
    parser.add_argument('--pronouncing_dict_file',
        default='cmu_pronouncing_dict/cmudict-0.7b.txt')
    args = parser.parse_args()

    # Parse food list and pronunciation dictionary
    foods = [line.strip() for line in open(args.foods_file)]
    pronounce = defaultdict(list) # word -> list of pronunciations, each a list of syllables.
    for line in open(args.pronouncing_dict_file):
        if line.startswith(';'):
            continue
        word = line.split('  ')[0]
        syllables = line.split('  ')[1].strip().split(' ')
        pronounce[word] = syllables

    # TODO connect to twitter to post
    # TODO pick out images, store locally I guess
    # TODO programmatically generate memes
    # TODO watermark memes
    for food in random.sample(foods, 10):
        print food
        for foodword in food.split(' '):
            letters = ''
            for syllable in pronounce[foodword.upper()]:
                syllable = syllable.strip('01234')
                possible_letters = syllable_lookup[syllable][:] # slice to copy
                # copy early letters to make them more likely.
                for i in range(len(possible_letters)):
                    possible_letters.extend(possible_letters[0:i])
                letters += random.sample(possible_letters, 1)[0]
            print letters
