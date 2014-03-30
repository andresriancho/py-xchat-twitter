# py-xchat-twitter

Twitter client written as an XChat plugin (Python). It allows you to tweet, read friends' timeline and check your replies. The twitter output will be sent out to an IRC channel of your choice (so, if you don't want to mix up your tweet and your chat, create a new channel and make it private).

## Installation

This plugin should be compatible with both XChat and XChat-Aqua. To install this plugin, put it in your .xchat2 then restart your XChat (for XChat-Aqua, it will be /Applications/X-Chat Aqua/Plugins), the plugin should be loaded automatically.

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

## Configuration

For configuration, please create a file called .xchattwitt.cfg in your home folder with following format:

```ini
[twitter]
username = your_twitter_login_name
password = your_twitter_password
channel = your_irc_channel_name
interval = 300
```

For the first three configurations, you should be able to guest.

This plugin will join the channel that you specify in the channel parameter. By the way, no `#` in front of the channel name.

For the interval, it's friends' timeline update interval in seconds.

## Original version

The [original version](https://code.google.com/p/py-xchat-twitter/) of this software, idea and architecture was developed by [Pruet Boona](pruetboonma@gmail.com) in 2009.