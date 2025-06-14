# Делал мрамер и чатгпт, за моральку фенькс НикНейму

import os
import asyncio
import logging
import subprocess
import tempfile

from telethon import types, functions
from telethon.errors.rpcerrorlist import RPCError
from telethon.tl.types import DocumentAttributeVideo

from .. import loader, utils


logger = logging.getLogger(__name__)


def run_command(command: str):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"{command} returned error: {error.decode()}")
    return output


@loader.tds
class VideoProcessorMod(loader.Module):
    """Video processing module"""
    strings = {"name": "Video Processor"}

    @loader.unrestricted
    async def vprocvcmd(self, message):
        """Process video from reply"""
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("Reply to a video")
            return
        if not reply.media or not isinstance(reply.media, types.MessageMediaDocument):
            await message.edit("Reply to a video")
            return
        video = reply.media.document
        if not isinstance(video, types.Document) or not video.mime_type.startswith("video/"):
            await message.edit("Reply to a video")
            return

        # Создание временной директории для работы с файлами
        with tempfile.TemporaryDirectory() as tempdir:

            # Скачивание видеофайла во временную директорию
            video_path = f"{tempdir}/{video.id}.{video.mime_type.split('/')[1]}"
            await message.edit("Downloading video...")
            await reply.download_media(file=video_path)
            logger.info(f"Video downloaded to {video_path}")
            
            # Разбор видео на фреймы
            frames_dir = os.path.join(tempdir, 'frames')
            if not os.path.exists(frames_dir):
                os.makedirs(frames_dir)
            output_audio_path = os.path.splitext(video_path)[0]
            subprocess.run(['ffmpeg', '-i', video_path, os.path.join(frames_dir, 'frame%d.jpg')])
            subprocess.run(['ffmpeg', '-i', video_path, '-vn', '-ar', '44100', '-ac', '1', '-b:a', '8k', '-f', 'mp3', output_audio_path])
            
            # Обработка кадров
            await message.edit("Lowrezing...")
            for filename in os.listdir(frames_dir):
                if filename.endswith('.jpg'):
                    filepath = os.path.join(frames_dir, filename)
                    subprocess.run(['jpegoptim', '--strip-all', '-m0', '-o', filepath])
        
    
            # Обработка видео
            await message.edit("Scetching...")
            output_video_path = os.path.splitext(video_path)[0] + '_processed.mp4'
            subprocess.run(['ffmpeg', '-framerate', '30', '-i', os.path.join(frames_dir, 'frame%d.jpg'),
                        '-i', output_audio_path,'-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-preset', 'veryslow', output_video_path])
            logger.info(f"Video processed, saved to {output_video_path}")
    
            # Отправка обработанного видео в телеграм
            await message.edit("Uploading video...")
            try:
                await message.client.send_file(message.to_id, output_video_path, attributes=[DocumentAttributeVideo(0, 0, 0, 0)])
            except RPCError as e:
                logger.error(f"Failed to send processed video: {e}")
                await message.edit("Failed to send processed video")
                return

        await message.edit("Done!")
