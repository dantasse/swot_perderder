#!/usr/bin/env python

# Every so often (TBD), takes a food, messes its name up, grabs an image of
# that food, and makes a meme with the misspelled word, posts it to Twitter.

import argparse, random, ConfigParser, os, PIL
from PIL import Image, ImageFont, ImageDraw
from collections import defaultdict
import oauth2 as oauth

config = ConfigParser.ConfigParser()
config.read('config.txt')
POST_URL = 'https://api.twitter.com/1.1/statuses/update.json'
OAUTH_KEYS = {'consumer_key': config.get('twitter', 'consumer_key'),
              'consumer_secret': config.get('twitter', 'consumer_secret'),
              'access_token_key': config.get('twitter', 'access_token_key'),
              'access_token_secret': config.get('twitter', 'access_token_secret')}

IMPACT = "Impact.ttf"
BASKERVILLE = "Baskerville.ttc"

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

# Returns a misspelled (but sort of pronounced the same) version of the food.
def misspell(food):
    fud = []
    for foodword in food.split(' '):
        letters = ''
        for phone in pronounce[foodword.upper()]:
            if phone.endswith('0') and not phone.startswith('ER') and random.random() < .25:
                continue # skip 25% of unstressed vowels, funnier that way.
                # but don't skip ERs, they are important. and usually funny.
            letters += get_letter(phone)
        fud.append(letters)
    return ' '.join(fud)

# Given a correctly-spelled word and a made-up spelling, returns a meme image.
def make_image(food, fud):
    foodlower = food.lower().replace(' ', '_')
    possible_files = [f for f in os.listdir('images') if '_'.join(f.split('_')[:-1]) == foodlower]

    # A lot of this cribbed from https://github.com/danieldiekmeier/memegenerator
    img = Image.open('images' + os.sep + random.sample(possible_files, 1)[0]).convert('RGBA')
    imageSize = img.size

    # find biggest font size that works
    fontSize = imageSize[1]/5
    font = ImageFont.truetype(IMPACT, fontSize)
    fudSize = font.getsize(fud)
    while fudSize[0] > imageSize[0]-20:
        fontSize = fontSize - 1
        font = ImageFont.truetype(IMPACT, fontSize)
        fudSize = font.getsize(fud)

    fudPositionX = (imageSize[0]/2) - (fudSize[0]/2)
    # nah, forget it, let's try it with just text always on the bottom.
    # if random.random() < .5:
    #     fudPositionY = 0
    # else:
    fudPositionY = imageSize[1] - fudSize[1]*1.2
    fudPosition = (fudPositionX, fudPositionY)

    draw = ImageDraw.Draw(img)
    
    # draw outlines - this is kind of slow, there may be a better way
    outlineRange = fontSize/15
    for x in range(-outlineRange, outlineRange+1, 2):
        for y in range(-outlineRange, outlineRange+1, 2):
            draw.text((fudPosition[0]+x, fudPosition[1]+y), fud, (0,0,0), font=font)

    draw.text(fudPosition, fud, (255,255,255), font=font)

    # half ass watermark :P TODO make this better
    watermarkFontSize = fontSize / 5
    watermarkFont = ImageFont.truetype(IMPACT, watermarkFontSize)
    draw.text((5, 5), "@swot_perderder", fill=(200, 200, 200), font=watermarkFont)

    img.save("temp.png")
    return img

# Sends an actual request to Twitter, with authentication.
# Note! It sends an actual request to Twitter!
def oauth_req(url, http_method="GET", post_body=None, http_headers=None):
    consumer = oauth.Consumer(key=OAUTH_KEYS['consumer_key'], secret=OAUTH_KEYS['consumer_secret'])
    token = oauth.Token(key=OAUTH_KEYS['access_token_key'], secret=OAUTH_KEYS['access_token_secret'])
    client = oauth.Client(consumer, token)
    if http_method == "POST":
        resp, content = client.request(url, method=http_method, body=post_body, headers=http_headers)
    else:
        resp, content = client.request(url, method=http_method, headers=http_headers)
    return (resp, content)

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

    for food in random.sample(foods, 1):
        print food
        fud = misspell(food)
        print fud
        image = make_image(food, fud) # TODO
        # post to twitter # TODO
        # sleep random number of minutes/hours
        # resize all images too
