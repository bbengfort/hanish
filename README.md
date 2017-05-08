# Hanish

**A [slackbot](https://api.slack.com/slack-apps) that makes small talk about the weather, [powered by Dark Sky](https://darksky.net/poweredby/).**

[![Build Status](https://travis-ci.org/bbengfort/hanish.svg?branch=master)](https://travis-ci.org/bbengfort/hanish)
[![Coverage Status](https://coveralls.io/repos/github/bbengfort/hanish/badge.svg?branch=master)](https://coveralls.io/github/bbengfort/hanish?branch=master)
[![Stories in Ready](https://badge.waffle.io/bbengfort/hanish.png?label=ready&title=Ready)](https://waffle.io/bbengfort/hanish)

## Getting Started

These steps detail the simplest method of deploying the Hanish chatbot either on a server or for development. The Hanish weather chatbot relies on two APIs, the [Slack API](https://api.slack.com/bot-users) for user interaction and the [Dark Sky API](https://darksky.net/dev/) for weather information. Before getting started, please login to these services and obtain the necessary credentials.

Credentials in hand, first clone the repository, then change your working directory to it:

    $ git clone https://github.com/bbengfort/hanish.git
    $ cd hanish

Create a virtual environment and install the dependencies. Note that Hanish is dependent on Python 2.7 because one of the primary dependencies, [slackclient](https://pypi.python.org/pypi/slackclient), is not currently Python 3 compatible. However, as soon as this dependency becomes Python 3 compatible, so too will the Hanish application.

    $ virtualenv -p python2.7 venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt

Add the following environment variables. The simplest way to do this is to create a `.env` file in your current working directory, the app will automatically load this file into the environment if it can find it.

    DEFAULT_ZIP_CODE=90210
    SLACK_BOT_NAME=myhanish
    SLACK_ACCESS_TOKEN=xoxb-slackaccesstoken
    DARKSKY_ACCESS_TOKEN=darkskyaccesstoken

Note that the Hanish chatbot is primarily configured from the environment. Hanish commands are run from the `hanishbot.py` script in the root of the repository (feel free to add this to your `$PATH`). To see all the commands and arguments, use help:

    $ ./hanishbot.py --help

This README.md will be updated with more commands and instructions as they are added to the application.

## About

### Brief

Create a chatbot for Slack that tells the weather. The minimum features are:

- Can assume that all requests are for one location (no need to manage individual user location... an instance of the bot can serve "Washington, DC" only).
- Respond to two commands triggered upon mention. "Weather now" "Weather tomorrow". They do what you'd expect.
- When the weather is going to be materially different from yesterday, let @channel know in the morning.
- One embellishment of your choice.

The exercise should take no more than four hours, do fewer items in the most professional quality rather than more things.

API Accounts:

- [darksky](https://darksky.net/dev/)
- [slack](https://api.slack.com/bot-users)

Professional quality and items for code review:

- Tests! What you test and how you test it matter a lot.
- Code style. Try to write idiomatic code in whatever language you choose. When you do un-idiomatic things, comment as to why.
- PR rapport. Sometimes code doesn't require comments, but the PR does to give readers a guide into how to approach the files. How do you set up your team to make the best assessment of your code.
- Performance doesn't matter, unless it's truly awful (though noting where solutions are naive is nice).

### Attribution

- This application is [powered by Dark Sky](https://darksky.net/poweredby/)
- The Zip Code to latitude, longitude mapping file was downloaded from a Gist by [@erichurst](https://gist.github.com/erichurst/7882666).

### Name Origin

The name [Hanish](https://nameberry.com/babyname/Hanish) means &ldquo;one who forewarns of storms&rdquo;. The name has a literary origin, from the [Epic of Gilgamesh](https://en.wikipedia.org/wiki/Gilgamesh_flood_myth), a legend that tells of a great flood. The thunder god, Adad, and the cloud and storm gods Shullar and Hanish all foretold of the flood by rumbling and coming over mountains and land.
