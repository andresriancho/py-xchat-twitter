# py-xchat-twitter

Twitter client written as an XChat plugin (Python). It allows you to tweet, read friends' timeline and check your replies. The twitter output will be sent out to an IRC channel of your choice (so, if you don't want to mix up your tweet and your chat, create a new channel and make it private).

## Configuration

Create a file called `.xchattwitt.cfg` in your home folder with following format:

```ini
[twitter]
oauth_token = ...
oauth_secret = ...
consumer_key = ...
consumer_secret = ...
interval = 180

[irc]
channel = irc_channel_name
```

The [Twitter API uses OAUTH](https://dev.twitter.com/docs/moving-basic-auth-oauth) instead of the "simple" username and password, so you'll have to [generate this information at dev.twitter.com](https://dev.twitter.com/docs/auth/oauth/faq).

This plugin will join the channel that you specify in the `channel` parameter. By the way, no `#` in front of the channel name.

For the `interval`, it's friends' timeline update interval in seconds.

## Installation

To install this plugin follow these steps:
 * `sudo pip install -r requirements.txt`
 * `cp xchat_twitter.py ~/.xchat2/`
 * Then restart your XChat, the plugin should be loaded automatically

This plugin should be compatible with both XChat and XChat-Aqua. For XChat-Aqua, the directory where the plugin should be copied is `/Applications/X-Chat Aqua/Plugins`.

## Commands

Following is the list of commands provided by this plugin:

| Command                            | Action                                  |
|------------------------------------|-----------------------------------------|
| /tweet "message" or /tw "message"  | Tweeting                                |
| /rt "name" "message"               | Re-tweeting                             |
| /dm "name" "message"	             | Direct message (DM)                     |
| /friends	                         | Retrieving friends' timeline            |
| /replies	                         | Retrieving replies (@yourname) timeline |
| /follow "screen name"	             | Follow a person using the screen name   |
| /unfollow "screen name"	         | Unfollow a person using the screen name |

## Original version

The [original version](https://code.google.com/p/py-xchat-twitter/) of this software, idea and architecture was developed by [Pruet Boona](pruetboonma@gmail.com) in 2009.