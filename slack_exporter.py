import json
from typing import Any
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import re 

slack_token = "YOUR_SLACK_TOKEN_HERE"
dumps_dir = './dumps'

class SlackExporter():
    def __init__(self, channel_name, channel_id = None) -> None:
        self.channel_name = channel_name

        if channel_id is None:
            self.channel_id = self.get_channel_id(channel_name)
        else:
            self.channel_id = channel_id

        self.client = WebClient(token="slack_token")

    @staticmethod
    def anonymize(text):
        # Anonymize user mentions and other identifiable information
        return re.sub(r'(?<=<@)U[A-Z0-9]+', 'ANONYMIZED', text)

    def get_channel_id(self, channel_name):
        cursor = None
        page = 1
        response = {}
        try:
            while True:
                response = self.client.conversations_list(limit=1000, cursor=cursor)
                channels = response['channels']
                for channel in channels:
                    if channel['name'] == channel_name:
                        print(f"Found channel {channel_name} with id {channel['id']}")
                        return channel['id']
                else:
                    cursor = response.get('response_metadata', {}).get('next_cursor')

                    if not cursor:
                        break

                    page += 1
                
        except SlackApiError as e:
            print(f"Error: {e.response['error']}")

    def separate_code(self, text):
        code_blocks = re.findall(r'```(.*?)```', text, re.DOTALL)
        clean_text = re.sub(r'```(.*?)```', '', text, flags=re.DOTALL)
        
        # remove ascii apostrophes without loosing meanings
        for word in clean_text.split():
            if "\u2019" in word:
                if word.split('\u2019')[0].lower() == 'i' and word.split('\u2019')[1].lower() == 'm':
                    clean_text = clean_text.replace(word, 'I am')
                if word.split('\u2019')[0].lower() in ['i', 'we'] and word.split('\u2019')[1].lower() == 'll':
                    first = word.split('\u2019')[0]
                    clean_text = clean_text.replace(word, f'{first} will')                
                elif word.split('\u2019')[0].lower() in ['it', 'that', 'there'] and word.split('\u2019')[1].lower() == 's':
                    first = word.split('\u2019')[0]
                    clean_text = clean_text.replace(word, f'{first} is')
                elif word.split('\u2019')[0].lower() in ['you', 'thay', 'there', 'we'] and word.split('\u2019')[1].lower() == 're':
                    first = word.split('\u2019')[0]
                    clean_text = clean_text.replace(word, f'{first} are')   
                elif word.split('\u2019')[0].lower() in ['do', 'don', 'does', 'he', 'she', 'ain', 'can'] and word.split('\u2019')[1].lower() == 't':
                    first = word.split('\u2019')[0]
                    clean_text = clean_text.replace(word, f'{first} not')
                else:
                    # in case literals are magically there
                    clean_text = self.clean.text.replace("'s", "").replace('"', '')
        for each in ['\u2018', '\u2019', '`']:
            clean_text = clean_text.replace(each, " ")
                    
        return clean_text, code_blocks

    def dump_history(self):
        cursor = None
        all_messages = []
        whole_text = ''
        while True:
            try:
                response = self.client.conversations_history(
                channel=self.channel_id,
                limit=200,
                cursor=cursor
                )

                messages = response['messages']
                
                for message in messages:
                    # Skip 'join channel' messages
                    if 'has joined the channel' in message['text']:
                        continue
                    
                    if not self.message_sanity(message['text'], message.get('user')):
                        continue
                    
                    
                    clean_message, code_blocks = self.separate_code(message['text'])
                    
                    # Remove mentions
                    clean_message = ' '.join(
                        word for word in clean_message.split() if '<@' not in word
                    )
                    clean_message = self.anonymize(clean_message)  # Anonymize user mentions
                    whole_text += '\n'.join(clean_message)
                    
                    msg_obj = {
                        'text': clean_message,
                        'code_blocks': code_blocks,
                        'user': message.get('user'),
                        'timestamp': message.get('ts'),
                        'thread': []
                    }

                    if 'thread_ts' in message:
                        thread_ts = message['thread_ts']
                        thread_response = self.client.conversations_replies(
                            channel=self.channel_id,
                            ts=thread_ts
                        )
                        thread_messages = thread_response['messages']

                        for thread_message in thread_messages:
                            
                            if not self.message_sanity(thread_message['text'], thread_message.get('user')):
                                continue
                            
                            thread_clean_message, thread_code_blocks = self.separate_code(thread_message['text'])
                    
                            # Remove mentions
                            thread_clean_message = ' '.join(
                                word for word in thread_clean_message.split() if '<@' not in word
                            )
                            
                            whole_text += '\n'.join(thread_clean_message)
                            
                            thread_msg_obj = {
                                'text': thread_clean_message,
                                'code_blocks': thread_code_blocks,
                                'user': message.get('user'),
                                'timestamp': message.get('ts'),
                            }
                            
                            
                            msg_obj['thread'].append(thread_msg_obj)

                    all_messages.append(msg_obj)

                cursor = response.get('response_metadata', {}).get('next_cursor', None)
                if not cursor:
                    break
                
            except SlackApiError as e:
                print(f"Slack API Error: {e.response['error']}")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break

        with open(f'{dumps_dir}/{self.channel_name}.json', 'w') as f:
            json.dump(all_messages, f, indent=4, ensure_ascii=False)
        
        return whole_text

    def message_sanity(self, message, user_id):
        if len(message.split()) < 5:
            return False
        if message.startswith('!'):
            return False
        else:
            return True
    