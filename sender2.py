import requests
import json
import time
import re
import argparse
import sys


class Sender:

    def __init__(self, 
                 params):
        
        self.params = params
        self.sender_initializer()

    def sender_initializer(self):

        with open(self.params, "r") as json_file:
            params = json.load(json_file)

        self.channelid=params['channelid']
        self.authorization=params['authorization']
        self.application_id = params['application_id']
        self.guild_id = params['guild_id']
        self.session_id = params['session_id']
        self.version = params['version']
        self.id = params['id']
        self.flags = params['flags']

    def send(self, prompt):
        header = {
            'authorization': self.authorization
        }
        
        prompt = prompt.replace('_', ' ')
        prompt = " ".join(prompt.split())
        prompt = re.sub(r'[^a-zA-Z0-9\s]+', '', prompt)
        prompt = prompt.lower()

        payload = {'type': 2, 
        'application_id': self.application_id,
        'guild_id': self.guild_id,
        'channel_id': self.channelid,
        'session_id': self.session_id,
        'data': {
            'version': self.version,
            'id': self.id,
            'name': 'imagine',
            'type': 1,
            'options': [{'type': 3, 'name': 'prompt', 'value': str(prompt) + ' ' + self.flags}],
            'attachments': []}
            }
        
        r = requests.post('https://discord.com/api/v9/interactions', json = payload , headers = header)
        while r.status_code != 204:
            r = requests.post('https://discord.com/api/v9/interactions', json = payload , headers = header)

        print('prompt [{}] successfully sent!'.format(prompt))

    # 重新提交
    def re_send(self, id_, num, keyword, uuid_):
        header = {
            'authorization': self.authorization
        }

        payload = {
            "type": 5,
            "application_id": self.application_id,
            "channel_id": self.channelid,
            "guild_id": self.guild_id,
            "data": {
                "id": self.id,
                "custom_id": "MJ::RemixModal::{}::{}".format(id_, num),
                "components": [{
                    "type": 1,
                    "components": [{
                        "type": 4,
                        "custom_id": "MJ::RemixModal::new_prompt",
                        "value": "{} {} --niji --s 750".format(keyword, uuid_)
                    }]
                }]
            },
            "session_id": self.session_id,
            # "nonce": "1109440483664330752"
        }

        r = requests.post('https://discord.com/api/v9/interactions', json=payload, headers=header)
        while r.status_code != 204:
            r = requests.post('https://discord.com/api/v9/interactions', json=payload, headers=header)


def parse_args(args):
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--params',        help='Path to discord authorization and channel parameters', required=True)
    parser.add_argument('--prompt',           help='prompt to generate', required=True)
        
    return parser.parse_args(args)


if __name__ == "__main__":

    args = sys.argv[1:]
    args = parse_args(args)
    params = args.params
    prompt = args.prompt
    print(params)
    print(prompt)
    # sender = Sender(params)
    # sender.send(prompt)
