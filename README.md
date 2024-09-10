# "Swot Perderder" generator

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
Then I used [this](https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example-deployment-pkg.html#with-s3-example-deployment-pkg-python) to install python on an AWS amazon linux machine in order to compile Pillow. (I think I had to compile pillow because it uses native code or something? There's a bit [here](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html#python-package-create-package-with-dependency) about "if your deployment package contains native libraries you can use SAM Build" so maybe I'd look into that too.

If I need to edit this code, I should:

- spin up an EC2 machine
- use the link above to install python on it
- make a `~/.aws/credentials` file on it. I can get that from my old computer or lastpass (aws_credentials.txt). It looks like this:

```
    [default]
    aws_access_key_id = (access key)
    aws_secret_access_key = (secret key)
```
- read [this tutorial](https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html) a bunch to remember how to do everything. Also [this](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html).
- make sure I've still got the `adminuser` role [here](https://console.aws.amazon.com/iam/home?#/users)
- make a deployment package as [here](https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example-deployment-pkg.html) or use `make_archive.sh`
- use the `lambda_commands.txt` to run update-function-code ([relevant docs, sort of](http://boto3.readthedocs.io/en/latest/reference/services/lambda.html#Lambda.Client.update_function_code))

How does Lambda know I'm authorized to access S3? Because of the role that I created the function under. And I think I can do that because I had the ~/.aws/credentials file on my AWS machine.

When is it running? See [triggers](https://us-west-2.console.aws.amazon.com/lambda/home?region=us-west-2#/functions/swot_perderder?tab=triggers).
