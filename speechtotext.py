from telethon import events
from .. import loader

@loader.tds
class VoiceReplyMod(loader.Module):
    strings = {"name": "SpeechToText"}
    def __init__(self):
        self.name = "SpeechToText"

    async def client_ready(self, client, db):
        self.client = client

    @loader.unrestricted
    @loader.ratelimit
    async def sttcmd(self, message):
        """
        Команда: .stt
        Пересылает голосовое сообщение боту @smartspeech_sber_bot, дожидается ответа и возвращает его в виде текста.
        """
        if message.is_reply:
            reply_message = await message.get_reply_message()
            if reply_message.voice and reply_message.voice.size > 0:
                # Показываем что хоть работает
                await message.edit("Перевожу..")

                # Пересылаем голосовое сообщение боту @smartspeech_sber_bot
                await reply_message.forward_to('@smartspeech_sber_bot')

                # Подписываемся на событие нового сообщения от бота
                event = self.client.loop.create_future()
                handler = lambda e: event.set_result(e)
                self.client.add_event_handler(handler, events.NewMessage(from_users='smartspeech_sber_bot', incoming=True))

                # Ожидаем ответа от бота
                response = await event

                # Удаляем обработчик события
                self.client.remove_event_handler(handler)

                # Получаем ответ бота в виде текста
                text = response.text

                # Показываем ответ
                await self.client.edit_message(message.to_id, message.id, text)
