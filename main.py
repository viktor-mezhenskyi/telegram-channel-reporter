import asyncio
import re
from telethon import TelegramClient
from telethon import functions, types
from config import api_id, api_hash

channels = open('channels.txt','r', encoding="utf8").read().splitlines()

def normalize_channel_name(channel_name):
    channel_name = re.sub(".*https","https", channel_name)
    return channel_name.replace("https://t.me/", "")

def get_message():
    with open('message.txt') as f:
        message = f.read()
        return message

def check_channel_name(strg, search=re.compile(r'[^_A-Za-z0-9.]').search):
    return not bool(search(strg))

async def search_channel(client, name):
    result = await client(functions.contacts.SearchRequest(
             q=name,
             limit=1
            ))
    return result.results

async def ban_channel(client, id, message):
    response = await client(functions.messages.ReportRequest(
                   peer='channel',
                   id=[id],
                   reason=types.InputReportReasonOther(),
                   message=message
                ))
    return response

async def main():
    async with TelegramClient('session', api_id, api_hash) as client:
        message = get_message()
        for channel_name in channels:
            channel_name=channel_name.replace(" ", "")
            if len(channel_name) == 0:
                continue
            #normalize channel name
            channel_name = normalize_channel_name(channel_name)
            # if not check_channel_name(channel_name):
            #     print("{} has incorrect symbols in name".format(channel_name))
            #     continue

            found_channels = await search_channel(client, channel_name)
            #try ban channel if found
            if len(found_channels) > 0:
                if not hasattr(found_channels[0], 'channel_id'):
                    print("{} is private. Couldn't found channel.".format(channel_name))
                    continue
                id = found_channels[0].channel_id
                response = await ban_channel(client, id, message)
                if response:
                    print("{} was banned".format(channel_name))
                else:
                    print("{} was NOT banned".format(channel_name))  
            else:
                print("{} was NOT found".format(channel_name))                
asyncio.run(main())

