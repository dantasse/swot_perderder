#!/usr/bin/env python

# Every so often (TBD), takes a food, messes its name up, grabs an image of
# that food, and makes a meme with the misspelled word, posts it to Twitter.

import argparse, random
from collections import defaultdict

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--foods_file', default='foods.txt')
    parser.add_argument('--pronouncing_dict_file',
        default='cmu_pronouncing_dict/cmudict-0.7b.txt')
    args = parser.parse_args()

    foods = [line.strip() for line in open(args.foods_file)]
    pronounce = defaultdict(list) # word -> list of pronunciations, each a list of syllables.
    for line in open(args.pronouncing_dict_file):
        if line.startswith(';'):
            continue
        word = line.split('  ')[0]
        syllables = line.split('  ')[1].split(' ')
        pronounce[word] = syllables

    food = random.sample(foods, 1)[0]
    print food
    print pronounce[food.upper()]
