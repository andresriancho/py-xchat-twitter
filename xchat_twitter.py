#!/usr/bin/env python
#Copyright (C) 2008,2009 Pruet Boona, <pruetboonma@gmail.com>
# Version 1.3.2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  US
import os
import urllib2

from ConfigParser import ConfigParser

# When you load your script in XChat, this module will be added to sys.path
# there is no need to install it, since it comes with xchat
import xchat

# This is required in requirements.txt
from twitter import Twitter, OAuth, api

__module_name__ = 'Twitter Plug-in'
__module_version__ = '2.0.0'
__module_description__ = 'Send/Receive Twitter Status Updates from XChat'

oauth_token = ''
oauth_secret = ''
consumer_key = ''
consumer_secret = ''
channel = None
interval = 180
since = 0
since_replies = 0
since_dm = 0
conf = ConfigParser()
cnc = None
source = 'pyxchattwitter'
user_agent = source
cnh = None
twitter_client = None


def confopt(conf, section, option, default=None):
    try:
        return conf.get(section, option)
    except:
        return default


def str_encode(str):
    return str.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')


def str_decode(str):
    return str.replace('&amp;', '&').replace('&lt;','<').replace('&gt;','>').replace('&quot;','"')


def user_timeline(since_id=0):
    results = twitter_client.statuses.user_timeline()
    return filter(lambda x: x['id'] > since_id, results)


def replies_timeline(since_replies_id=0):
    global username
    global password
    global user_agent
    auth = base64.encodestring('%s:%s' % (username, password)).strip()
    url = 'http://twitter.com/statuses/mentions.json'
    if since_replies_id > 0:
        url = url + '?since_id=%' + str(since_replies_id)
    req = urllib2.Request(url, None, {'Authorization': 'Basic %s' % auth, 'User-Agent': user_agent})

    try:
        fd = urllib2.urlopen(req)
    except Exception, why:
        print_msg('Channel Message', 'Twitter Error', "Couldn't retrieve your replies timeline, please try again" + str(why), '@' )
        return []
    results = simplejson.loads(fd.read())
    return filter(lambda x: x['id'] > since_replies_id, results)


def mydebug(msg):
    xchat.emit_print('Channel Message', 'debug', msg, '@')


def print_msg(arg1, arg2, arg3, arg4):
    global channel
    cnc = None
    arg3 = str_decode(arg3)
    cnc = xchat.find_context(channel='#%s'%channel)
    if cnc is not None:
        cnc.emit_print(arg1, arg2, arg3, arg4)
    else:
        xchat.emit_print(arg1, arg2, arg3, arg4)


def check_channel(userdata):
    global cnh
    global channel
    cn = xchat.find_context(channel='#%s' % channel)
    if cn is not None:
        xchat.unhook(cnh)
    else:
        xchat.command("join #" + channel)
    return xchat.EAT_ALL


def timeline_cb(userdata):
    global since
    global conf
    global username

    try:
        results = user_timeline(since)
    except Exception, why:
        print_msg('Channel Message', 'Twitter Error', 'xx' + str(why), '@')
        return xchat.EAT_ALL

    results.reverse()
    for item in results:
        txt = item['text'].encode('utf-8')

        if txt.find('@' + username) >= 0:
            print_msg('Channel Message', 'Tweet', '4' + item['user']['screen_name'].encode('utf-8') + ': ' + txt, '@')

        # FIXME, should be better way
        elif item['user']['screen_name'] == username:
            print_msg('Channel Message', 'Tweet', '6' + item['user']['screen_name'].encode('utf-8') + ': ' + txt, '@')

        else:
            print_msg('Channel Message', 'Tweet', item['user']['screen_name'].encode('utf-8') + ': ' + txt, '@')

        since = item['id']

    conf.set('twitter', 'since_id', str(since))
    conf.write(open(os.path.expanduser('~/.xchattwitt.cfg'), 'w'))
    return xchat.EAT_ALL


def friends_cb(words, word_eol, userdata):
    return timeline_cb(userdata)


def replies_cb(words, word_eol, userdata):
    global since_replies
    global conf
    try:
        results = replies_timeline(since_replies)
    except Exception, why:
        print_msg('Channel Message', 'Twitter Error', str(why), '@' )
        results = []
        return xchat.EAT_ALL
    results.reverse()
    for item in results:
        print_msg('Channel Message', 'Replies', item['user']['screen_name'].encode('utf-8') + ': ' + item['text'].encode('utf-8'), '@' )
        since_replies = item['id']
    conf.set('twitter', 'since_replies_id', str(since_replies))
    conf.write(open(os.path.expanduser('~/.xchattwitt.cfg'), 'w'))
    return xchat.EAT_ALL


def dm(receiver, msg):
    global username
    global password
    global source
    global user_agent
    auth = base64.encodestring('%s:%s' % (username, password)).strip()
    data = {}
    data['text'] = str_encode(msg)
    data['user'] = receiver
    #data['source'] = source
    url = 'http://twitter.com/direct_messages/new.json'
    try:
        urllib2.urlopen(urllib2.Request(url, urllib.urlencode(data), {'Authorization': 'Basic %s' % auth, 'User-Agent': user_agent}))
    except Exception:
        print_msg('Channel Message', 'Twitter Error', "Couldn't send your dm, please try again", '@' )
        return []
    return xchat.EAT_ALL


def follow(name, flag):
    global username
    global password
    global source
    global user_agent
    auth = base64.encodestring('%s:%s' % (username, password)).strip()
    data = {}
    if flag:
        url = 'http://twitter.com/friendships/create/%s.json?follow=true' % name
    else:
        url = 'http://twitter.com/friendships/destroy/%s.json?follow=true' % name
    try:
        urllib2.urlopen(urllib2.Request(url, urllib.urlencode(data), {'Authorization': 'Basic %s' % auth, 'User-Agent': user_agent}))
    except Exception, msg:
        if str(msg) == "HTTP Error 403: Forbidden":
            if flag:
                print_msg('Channel Message', 'Twitter Error', "You're already following this person", '@')
            else:
                print_msg('Channel Message', 'Twitter Error', "You're not following this person", '@')
        else:
            print_msg('Channel Message', 'Twitter Error', "Couldn't send your request, please try again" + str(msg), '@' )
    return xchat.EAT_ALL


def tweet(msg):
    global username
    global password
    global source
    global user_agent
    auth = base64.encodestring('%s:%s' % (username, password)).strip()
    data = {}
    data['status'] = msg
    data['source'] = source
    url = 'http://twitter.com/statuses/update.json'
    try:
        urllib2.urlopen(urllib2.Request(url, urllib.urlencode(data), {'Authorization': 'Basic %s' % auth, 'User-Agent': user_agent}))
    except Exception:
        print_msg('Channel Message', 'Twitter Error', "Couldn't send your tweet, please try again", '@' )
    return xchat.EAT_ALL


def dm_cb(words, word_eol, userdata):
    if len(words) < 2:
        print_msg('Channel Message', 'Twitter Error', '/dm <name> <message>\nNo message send out.', '@' )
        return xchat.EAT_ALL
    return dm(words[1], word_eol[2])


def follow_cb(words, word_eol, userdata):
    if len(words) < 2:
        print_msg('Channel Message', 'Twitter Error', '/follow <name>\nNo message send out.', '@' )
        return xchat.EAT_ALL
    return follow(word_eol[1], True)


def unfollow_cb(words, word_eol, userdata):
    if len(words) < 2:
        print_msg('Channel Message', 'Twitter Error', '/unfollow <name>\nNo message send out.', '@' )
        return xchat.EAT_ALL
    return follow(word_eol[1], False)


def tweet_cb(words, word_eol, userdata):
    if len(words) < 2:
        print_msg('Channel Message', 'Twitter Error', '/tweet <message>\nNo message send out.', '@' )
        return xchat.EAT_ALL
    return tweet(word_eol[1])


def retweet_cb(words, word_eol, userdata):
    if len(words) < 3:
        print_msg('Channel Message', 'Twitter Error', '/rt <name> <message>\nNo message send out.', '@' )
        return xchat.EAT_ALL
    return tweet('rt @' + word_eol[1])

#
# Configuration loading
#
conf.read([os.path.expanduser('~/.xchattwitt.cfg')])
GENERIC_MESSAGE = 'Please set "%s" in the configuration file then reload'\
                  'this module.'

oauth_token_conf = confopt(conf, 'twitter', 'oauth_token')
if oauth_token_conf is None:
    print_msg('Channel Message', 'Twitter Error',
              GENERIC_MESSAGE % 'oauth_token', '@')
else:
    oauth_token = oauth_token_conf

oauth_secret_conf = confopt(conf, 'twitter', 'oauth_secret')
if oauth_secret_conf is None:
    print_msg('Channel Message', 'Twitter Error',
              GENERIC_MESSAGE % 'oauth_secret', '@')
else:
    oauth_secret = oauth_secret_conf

consumer_key_conf = confopt(conf, 'twitter', 'consumer_key')
if consumer_key_conf is None:
    print_msg('Channel Message', 'Twitter Error',
              GENERIC_MESSAGE % 'consumer_key', '@')
else:
    consumer_key = consumer_key_conf

consumer_secret_conf = confopt(conf, 'twitter', 'consumer_secret')
if consumer_secret_conf is None:
    print_msg('Channel Message', 'Twitter Error',
              GENERIC_MESSAGE % 'consumer_secret', '@')
else:
    consumer_secret = consumer_secret_conf

interval_conf = confopt(conf, 'twitter', 'interval')
if interval_conf is not None:
    interval = int(interval_conf)

channel_conf = confopt(conf, 'irc', 'channel')
if channel_conf is not None:
    channel = channel_conf

if oauth_token and oauth_secret and consumer_key and consumer_secret:
    try:
        twitter_client = Twitter(auth=OAuth(oauth_token, oauth_secret,
                                            consumer_key, consumer_secret))
        twitter_client.statuses.home_timeline()
    except api.TwitterHTTPError:
        print_msg('Channel Message', 'Twitter Error',
                  'Incorrect OAuth tokens.', '@')


# These are hook configuration
xchat.hook_command('TWEET', tweet_cb, help='/tweet <message>')
xchat.hook_command('TW', tweet_cb, help='/tw <message>')
xchat.hook_command('RT', retweet_cb, help='/rt <name> <message>')
xchat.hook_command('DM', dm_cb, help='/dm <name> <message>')
xchat.hook_command('REPLIES', replies_cb, help='/replies')
xchat.hook_command('MENTIONS', replies_cb, help='/mentions')
xchat.hook_command('FRIENDS', friends_cb, help='/friends')
xchat.hook_command('FOLLOW', follow_cb, help='/follow <name>')
xchat.hook_command('UNFOLLOW', unfollow_cb, help='/unfollow <name>')
xchat.hook_timer(interval * 1000, timeline_cb)
cnh = xchat.hook_timer(1000, check_channel)
