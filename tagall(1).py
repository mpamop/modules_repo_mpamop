import logging
import requests
from .. import loader, utils
import asyncio

logger = logging.getLogger(__name__)

def register(cb):
    cb(TagAllMod())

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class TagAllMod(loader.Module):
    def __init__(self):
        self.config = loader.ModuleConfig("DEFAULT_MENTION_MESSAGE", "Так блин!", "Default message of mentions")
        self.name = "TagAll"
        
    async def client_ready(self, client, db):
        self.client = client

    async def tagallcmd(self, message):
        arg = utils.get_args_raw(message)
        
        logger.error(message)
        notifies = []
        async for user in self.client.iter_participants(message.to_id):
            notifies.append("<a href=\"tg://user?id="+ str(user.id) +"\">​</a>")
        chunkss = list(chunks(notifies, 10))
        logger.error(chunkss)
        await message.delete()
        for chunk in chunkss:
            await self.client.send_message(message.to_id, (self.config["DEFAULT_MENTION_MESSAGE"] if not arg else arg) + ' '.join(chunk))

#мрампер давай не будет слевать..............
#а вот будет
