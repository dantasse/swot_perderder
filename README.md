"Swot Perderder" generator - misspelled foods.

Picks a random food, finds a picture of it, overlays text of a misspelled
version of that food, posts it to twitter.

Includes the [CMU Pronouncing Dictionary](http://www.speech.cs.cmu.edu/cgi-bin/cmudict)
(with a few words added. So if you want the original thing, go find theirs, not
mine.)

Twitter cover photo from [Flickr user wikioticslan](https://flic.kr/p/8MKF4C)
under [CC-by-SA license](https://creativecommons.org/licenses/by-sa/2.0/)
(words added by me)

Contains lots of code from [Daniel Diekmeier’s meme generator](https://github.com/danieldiekmeier/memegenerator)

The `scrape_images.py` won't work anymore because it was using an old Google
image search API. Best bet in the future if you want to update this is to use
[Bing](https://msdn.microsoft.com/en-us/library/dn760791(v=bsynd.50).aspx), I
guess.

`make_archive.sh` is a script that turns this directory into an archive that
AWS Lambda can use.
Then I used [this](https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example-deployment-pkg.html#with-s3-example-deployment-pkg-python) to install python on an AWS amazon linux machine in order to compile Pillow.

Also, at one point I tried to reconfigure this as a Flask app that runs on Amazon's Elastic Beanstalk. I think that was dumb; it can just run on an EC2 free micro instance. Any references that are still around to Flask or EB can be ignored for the time being.
