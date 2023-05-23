import requests
import re


class Sender:
    def __init__(self, params):
        self.channelid = params['channelid']
        self.authorization = params['authorization']
        self.application_id = params['application_id']
        self.guild_id = params['guild_id']
        self.session_id = params['session_id']
        self.version = params['version']
        self.id = params['id']
        self.flags = params['flags']

    def generate(self, prompt):
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
        
        r = requests.post('https://discord.com/api/v9/interactions', json=payload, headers=header)
        # while r.status_code != 204:
        #     r = requests.post('https://discord.com/api/v9/interactions', json=payload, headers=header)

        print('prompt [{}] successfully sent!'.format(prompt))

    # 提交任务
    def send_(self, msg_id, index, msg_hash, operate_type):
        """

        :param msg_id:      id
        :param index:       下序列
        :param msg_hash:
        :param operate_type:    操作类型, variation微调, upsample放大, reroll重置
        :return:
        """
        kwargs = {
            "message_flags": 0,
            "message_id": msg_id,
        }
        type_ = 3
        data = {
            "component_type": 2,
            "custom_id": f"MJ::JOB::{operate_type}::{index}::{msg_hash}"
            if operate_type != 'reroll' else f"MJ::JOB::{operate_type}::{index}::{msg_hash}::SOLO"
        }

        payload = {
            "type": type_,
            "application_id": self.application_id,
            "guild_id": self.guild_id,
            "channel_id": self.channelid,
            "session_id": self.session_id,
            "data": data
        }
        payload.update(kwargs)

        header = {
            'authorization': self.authorization
        }
        r = requests.post('https://discord.com/api/v9/interactions', json=payload, headers=header)
        print(r.status_code)

    # 微调
    def send_variation(self, msg_id, index, msg_hash):
        self.send_(msg_id, index, msg_hash, 'variation')

    # 放大
    def send_upscale(self, msg_id, index, msg_hash):
        self.send_(msg_id, index, msg_hash, 'upsample')

    # 重置
    def send_reroll(self, msg_id, index=0, msg_hash=''):
        self.send_(msg_id, index, msg_hash, 'reroll')


# def parse_args(args):
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--params',        help='Path to discord authorization and channel parameters', required=True)
#     parser.add_argument('--prompt',           help='prompt to generate', required=True)
#
#     return parser.parse_args(args)
#
#
# if __name__ == "__main__":
#
#     args = sys.argv[1:]
#     args = parse_args(args)
#     params = args.params
#     prompt = args.prompt
#
#     sender = Sender(params)
#     sender.generate(prompt)
