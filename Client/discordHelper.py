#!/usr/bin/env python3
from discord import SyncWebhook
import sys

sys.path.append('.')
sys.path.append('..')
from Common.config import telescope,logger,discordWebHook

def sendDiscordMessage(message):
  if discordWebHook is not None:
    webhook = SyncWebhook.from_url(discordWebHook)
    webhook.send(message)
  else:
    logger.warning(f"Discord message not sent because webhook for telescope {telescope['shortname']} is not configured in config.json")
  pass

if __name__ == '__main__':
  sendDiscordMessage('Hello World!')
