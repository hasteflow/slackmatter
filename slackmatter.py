
from slackclient import SlackClient

import requests
import json
import time
import datetime
import calendar


SETTINGS = {
    'slack': {
        'name': '<slackbot name>',
        'token': '<slackbot token>',
        'channel_id': '<slack channel id for posting messages>'
    },
    'mattermost': {
        'api_link': 'https://<mattermost link>/api/v3/',
        'team_id': '<your team id>',
        'login_user': '<user login>',
        'login_pass': '<raw user password>',
        'channels': {
            '<channel label>': '<channel id>',
            '<channel label2>': '<channel id2>',
        }
    }
}


class Slack(object):

    def __init__(self, settings):
        self.settings = settings
        self.client = SlackClient(token=settings['token'])


    def postMessage(self, text, user=None):

        if not user:
            user = self.settings['channel_id']

        self.client.api_call(
            'chat.postMessage',
            channel=user,
            text=text,
            as_user=True,
            mrkdwn=False,
            username=self.settings['name']
        )


class Mattermost(object):

    def __init__(self, settings):
        self.settings = settings
        self.headers = {}
        self.channel_timestamps = {}

        self.initChannelTimestamps()
        self.user_list = {}
        self.login()


    def getUtcTimestamp(self):
        timestamp = datetime.datetime.utcnow()
        timestamp = calendar.timegm(timestamp.timetuple())

        return str(timestamp) + '000'


    def initChannelTimestamps(self):
        for channel_id in self.settings['channels'].values():
            self.channel_timestamps[channel_id] = self.getUtcTimestamp()

        try:
            with open('timestamps.txt') as f:
                contents = f.read()

                # unusual bug
                data = json.loads(json.loads(contents))

                for channel_id in data:
                    self.channel_timestamps[channel_id] = data[channel_id]

        except:
            pass


    def getUsername(self, user_id=''):
        if user_id in self.user_list:
            return self.user_list[user_id]

        url = self.settings['api_link'] + 'users/ids'
        data = [user_id]
        response = requests.post(url, json=data, headers=self.headers)

        try:
            data = json.loads(response.content)
            username = data[user_id]['username']
            self.user_list[user_id] = username
            return username

        except:
            return ''


    def login(self):
        url = self.settings['api_link'] + 'users/login'

        data = {
            'login_id': self.settings['login_user'],
            'password': self.settings['login_pass'],
            'token': ''
        }

        response = requests.post(url, json=data)
        self.headers = {'Authorization': 'Bearer ' + response.headers['Token']}


    def getPosts(self, channel_id):
        url = self.settings['api_link']
        since_time = self.channel_timestamps[channel_id]

        url += '/teams/{team_id}/channels/{channel_id}/posts/since/{time}'.format(
            team_id=self.settings['team_id'],
            channel_id=channel_id,
            time=since_time
        )

        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                return json.loads(response.content)

        except:
            self.login()

        return


    def saveChannelTimestamp(self, channel_id, timestamp):
        self.channel_timestamps[channel_id] = timestamp
        data = json.dumps(self.channel_timestamps)

        with open('timestamps.txt', 'w') as f:
            f.write(json.dumps(data))


def add_happy_day_tag(message):
    '''check for 'happy day' lowercase in message and
        add @happyday tag
    '''

    if 'happy day' in message.lower():
        return message + u' @happyday'

    return message


if __name__ == '__main__':

    slack = Slack(SETTINGS['slack'])
    mattermost = Mattermost(SETTINGS['mattermost'])

    try:
        while True:
            for channel_name, channel_id in SETTINGS['mattermost']['channels'].items():
                posts = mattermost.getPosts(channel_id)

                if posts and posts['posts']:
                    timestamps = []

                    for message_id in reversed(posts['order']):
                        user_id = posts['posts'][message_id]['user_id']

                        message = u'[ {channel} ][ {user} ]: {message}'.format(
                            channel=channel_name,
                            user=mattermost.getUsername(user_id),
                            message=posts['posts'][message_id]['message']
                        )

                        timestamps.append(posts['posts'][message_id]['create_at'])
                        timestamps.append(posts['posts'][message_id]['update_at'])

                        message = add_happy_day_tag(message)
                        slack.postMessage(message)

                    since_time = max(timestamps)
                    mattermost.saveChannelTimestamp(channel_id, since_time)

            time.sleep(10)

    except KeyboardInterrupt:
        pass





