import requests
import json
import time
import pandas as pd
import os
import re
from datetime import datetime
import argparse
import sys
import sqlite3
import traceback
db_path = '/home/admin/project/AI/db.sqlite3'


class Receiver:

    def __init__(self, params, local_path):
        
        self.params = params
        self.local_path = local_path

        self.sender_initializer()

        self.df = pd.DataFrame(columns=['prompt', 'url', 'filename', 'is_downloaded'])

    # 重连数据库
    @staticmethod
    def reconnect_sql():
        conn = sqlite3.connect(db_path)  # 连接数据库
        cursor = conn.cursor()  # 创建一个游标对象
        return conn, cursor

    def sender_initializer(self):

        with open(self.params, "r") as json_file:
            params = json.load(json_file)

        self.channelid=params['channelid']
        self.authorization=params['authorization']
        self.headers = {'authorization': self.authorization}

    def retrieve_messages(self):
        r = requests.get(
            f'https://discord.com/api/v10/channels/{self.channelid}/messages?limit={100}', headers=self.headers)
        jsonn = json.loads(r.text)
        # print(jsonn)
        return jsonn

    def collecting_results(self):
        message_list = self.retrieve_messages()
        self.awaiting_list = pd.DataFrame(columns=['prompt', 'status'])
        for message in message_list:
            # print(message)
            if (message['author']['username'] == 'Midjourney Bot') and ('**' in message['content']):
                
                if len(message['attachments']) > 0:

                    if (message['attachments'][0]['filename'][-4:] == '.png') or ('(Open on website for full quality)' in message['content']):
                        id = message['id']
                        prompt = message['content'].split('**')[1].split(' --')[0]
                        url = message['attachments'][0]['url']
                        filename = message['attachments'][0]['filename']
                        # print('attachments', message['attachments'])
                        if id not in self.df.index:
                            self.df.loc[id] = [prompt, url, filename, 0]

                    else:
                        id = message['id']
                        prompt = message['content'].split('**')[1].split(' --')[0]
                        if ('(fast)' in message['content']) or ('(relaxed)' in message['content']):
                            try:
                                status = re.findall("(\w*%)", message['content'])[0]
                            except:
                                status = 'unknown status'
                        self.awaiting_list.loc[id] = [prompt, status]

                else:
                    id = message['id']
                    prompt = message['content'].split('**')[1].split(' --')[0]
                    if '(Waiting to start)' in message['content']:
                        status = 'Waiting to start'
                    self.awaiting_list.loc[id] = [prompt, status]

    def outputer(self):
        if len(self.awaiting_list) > 0:
            print(datetime.now().strftime("%H:%M:%S"))
            print('prompts in progress:')
            print(self.awaiting_list)
            print('=========================================')

        waiting_for_download = [self.df.loc[i].prompt for i in self.df.index if self.df.loc[i].is_downloaded == 0]
        if len(waiting_for_download) > 0:
            print(datetime.now().strftime("%H:%M:%S"))
            print('waiting for download prompts: ', waiting_for_download)
            print('=========================================')

    def downloading_results(self):
        processed_prompts = []
        for i in self.df.index:
            if self.df.loc[i].is_downloaded == 0:
                # file_path = os.path.join(self.local_path, self.df.loc[i].filename)
                prompt = '_'.join(self.df.loc[i].filename.split('_')[1:-1])
                msg_hash, zui = self.df.loc[i].filename.split('_')[-1].split('.')
                msg_id = i
                file_name = '{}_{}.{}'.format(msg_id, msg_hash, zui)

                file_path = os.path.join(self.local_path, file_name)
                if os.path.isfile(file_path):
                    self.df.loc[i, 'is_downloaded'] = 1
                    continue

                response = requests.get(self.df.loc[i].url)
                with open(file_path, "wb") as req:
                    print(i, '\t', self.df.loc[i])
                    req.write(response.content)

                # 更新数据
                conn, cursor = self.reconnect_sql()
                sql = "update cm_task set msg_id='{}', msg_hash='{}', content='{}', update_time='{}', state=2 " \
                      "where id in (select id from cm_task where content ISNULL and prompt='{}' order by id limit 1)".\
                    format(msg_id, msg_hash, file_name, datetime.now(), prompt)
                print(sql)
                cursor.execute(sql)
                conn.commit()
                cursor.close()
                # 更新数据

                self.df.loc[i, 'is_downloaded'] = 1
                processed_prompts.append(self.df.loc[i].prompt)
        if len(processed_prompts) > 0:
            print(datetime.now().strftime("%H:%M:%S"))
            print('processed prompts: ', processed_prompts)
            print('=========================================')
  
    def main(self):
        try_time = 10
        while True:
            if try_time <= 0:
                break
            try:
                self.collecting_results()
                self.outputer()
                self.downloading_results()
                time.sleep(30)
                try_time = 10
            except:
                print('{} :: 接收流程出现错误, 错误原因为: {}\n 休眠2分钟后进行重试'.format(datetime.now(), traceback.format_exc()))
                print('{} :: 剩余重试次数为{}'.format(datetime.now(), try_time))
                time.sleep(60 * 2)


def parse_args(args):
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--params',        help='Path to discord authorization and channel parameters', required=True)
    parser.add_argument('--local_path',           help='Path to output images', required=True)
        
    return parser.parse_args(args)


if __name__ == "__main__":

    args = sys.argv[1:]
    args = parse_args(args)
    params = args.params
    local_path = args.local_path #'/Users/georgeb/discord_api/images/'

    print('=========== listening started ===========')
    receiver = Receiver(params, local_path)
    receiver.main()
