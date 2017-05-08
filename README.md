# Hanish

**A slackbot that makes small talk about the weather.**

## Name Origin

The name [Hanish](https://nameberry.com/babyname/Hanish) means &ldquo;one who forewarns of storms&rdquo;. The name has a literary origin, from the [Epic of Gilgamesh](https://en.wikipedia.org/wiki/Gilgamesh_flood_myth), a legend that tells of a great flood. The thunder god, Adad, and the cloud and storm gods Shullar and Hanish all foretold of the flood by rumbling and coming over mountains and land.

## Brief

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
