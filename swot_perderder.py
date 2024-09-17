#!/usr/bin/env python

# Every so often (TBD), takes a food, messes its name up, grabs an image of
# that food, and makes a meme with the misspelled word, posts it to Twitter.

import random, PIL, math
from io import BytesIO
from configparser import ConfigParser
from PIL import Image, ImageFont, ImageDraw
from collections import defaultdict
from twython import Twython
import twython.exceptions
import boto3
import os

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
    'EY':['A', 'A', 'EY'],
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
def misspell(pronounce_dict, food):
    fud = []
    for foodword in food.split(' '):
        letters = ''
        for phone in pronounce_dict[foodword.upper()]:
            if phone.endswith('0') and not phone.startswith('ER') and random.random() < .25:
                continue # skip 25% of unstressed vowels, funnier that way.
                # but don't skip ERs, they are important. and usually funny.
            letters += get_letter(phone)
        fud.append(letters)
    return ' '.join(fud)

# Given a correctly-spelled word and a made-up spelling, returns a meme image.
def make_image(food, fud, s3_client=None):
    foodlower= food.lower().replace(' ', '_')
    if s3_client:
        possible_files = [f['Key'] for f in s3_client.list_objects_v2(Bucket='swot-perderder', Prefix='images/'+foodlower)['Contents']]
    else:
        possible_files = [filename for filename in os.listdir('images/') if filename.startswith(foodlower)]
    
    filename = random.sample(possible_files, 1)[0]


    # A lot of this cribbed from https://github.com/danieldiekmeier/memegenerator
    if s3_client:
        obj = s3_client.get_object(Bucket='swot-perderder', Key = filename)
        img = Image.open(obj['Body'])
    else:
        img = Image.open(f"images/{filename}")

    # find biggest font size that works
    fontSize = int(math.floor(img.size[1]/5))
    font = ImageFont.truetype('Impact.ttf', fontSize)
    fudSize = font.getsize(fud)
    while fudSize[0] > img.size[0]-20:
        fontSize = fontSize - 1
        font = ImageFont.truetype('Impact.ttf', fontSize)
        fudSize = font.getsize(fud)

    fudPositionX = (img.size[0]/2) - (fudSize[0]/2)
    
    # We want the text to be visible when you first see it in the twitter
    # stream. That means, if the image is taller than 2:1, you have to make
    # sure to position the text within the center 2:1 rectangle.
    # ... though this doesn't even work, b/c different clients display it differently. TODO fix.
    height = img.size[1]
    width = img.size[0]
    if height > width/2:
        innerBoxTop = height/2 + .5 * width/2
        fudPositionY = innerBoxTop - fudSize[1]*1.1
    else:
        fudPositionY = img.size[1] - fudSize[1]*1.2
    fudPosition = (fudPositionX, fudPositionY)

    draw = ImageDraw.Draw(img)
    
    # draw outlines - this is kind of slow, there may be a better way
    outlineRange = int(math.floor(fontSize/15))
    for x in range(-outlineRange, outlineRange+1, 2):
        for y in range(-outlineRange, outlineRange+1, 2):
            draw.text((fudPosition[0]+x, fudPosition[1]+y), fud, (0,0,0), font=font)

    draw.text(fudPosition, fud, (255,255,255), font=font)

    # half ass watermark :P TODO make this better
    watermarkFontSize = int(math.floor(fontSize / 5))
    watermarkFont = ImageFont.truetype('Impact.ttf', watermarkFontSize)
    draw.text((5, 5), "@swot_perderder", fill=(200, 200, 200), font=watermarkFont)

    return img

def post_tweet(image, fud, twitter_client):
    image_io = BytesIO()
    
    image.save(image_io, format='JPEG')
    # If you do not seek(0), the image will be at the end of the file and unable to be read
    image_io.seek(0)
    # TODO update this to use upload_media and then a separate post instead.
    twitter_client.update_status_with_media(media=image_io, status='')

def load_pronouncing_dict(pronouncing_dict_file):
    pronounce = defaultdict(list) # word -> list of pronunciations, each a list of phones.
    for line in open(pronouncing_dict_file):
        if line.startswith(';'):
            continue
        word = line.split('  ')[0]
        pronounce[word] = line.split('  ')[1].strip().split(' ')
    return pronounce

def quick_pronounce(word):
    pronounce_temp = load_pronouncing_dict("cmu_pronouncing_dict/cmudict-0.7b.txt")
    print(misspell(pronounce_temp, word))

def do_a_meme(food, fud, s3_client, twitter_client):
    image = make_image(food, fud, s3_client)
    print("Posting %s as %s" % (food, fud))
    try:
        post_tweet(image, fud, twitter_client)
    except twython.exceptions.TwythonError:
        print("Error once, trying again.")
        try:
            post_tweet(image, fud, twitter_client)
        except:
            print("Error twice, giving up for now.")
    return '<html><head></head><body>Posted a tweet: '+fud+'</body></html>'

# Just drops |event| and |context| for now.
def handler(event, context):
    s3_client = boto3.client('s3')
    config = ConfigParser()
    config.read('config.txt')
    POST_URL = 'https://api.twitter.com/1.1/statuses/update.json'
    OAUTH_KEYS = {'consumer_key': config.get('twitter', 'consumer_key'),
                  'consumer_secret': config.get('twitter', 'consumer_secret'),
                  'access_token_key': config.get('twitter', 'access_token_key'),
                  'access_token_secret': config.get('twitter', 'access_token_secret')}

    twitter = Twython(OAUTH_KEYS['consumer_key'], OAUTH_KEYS['consumer_secret'],
        OAUTH_KEYS['access_token_key'], OAUTH_KEYS['access_token_secret'])

    # Parse food list and pronunciation dictionary
    foods = [line.strip() for line in open('foods.txt')]
    pronounce = load_pronouncing_dict('cmu_pronouncing_dict/cmudict-0.7b.txt')

    not_pronounced_words = [w for w in foods if w.split()[0].upper() not in pronounce]
    if len(not_pronounced_words) > 0:
        print('Warning! These words are unpronounced: ' + str(not_pronounced_words))

    food = random.sample(foods, 1)[0]
    fud = misspell(pronounce, food)
    do_a_meme(food, fud, s3_client, twitter)

if __name__ == '__main__':
    handler(None, None)
