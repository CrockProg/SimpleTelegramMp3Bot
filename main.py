#encoding: utf-8
from __future__ import unicode_literals

import logging
import os
import glob
import telebot
import youtube_dl

from mutagen.mp3 import MP3
from mutagen import MutagenError
from config import TG_TOKEN
from config import FOLDER


#Constants
bot = telebot.TeleBot(TG_TOKEN)
LIMIT = 2300

#Logger
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    #Logger settings
    class MyLogger(object):
        def debug(self, msg):
            pass
        def warning(self, msg):
            pass
        def error(self, msg):
            print(msg)

    if message.text.lower() == '/start':
        bot.send_message(message.from_user.id, "Welcome! Send me the video link")
    else:
        bot.send_message(message.from_user.id, "Checking...")
    #As soon as the link passes all checks, the bot sends a message about the start of conversion
        def my_hook(d):
            if d['status'] == 'finished':
                bot.send_message(message.from_user.id, "Processing has begun!")

        #Youtube_dl options
        ydl_opts = {
            'updatetime': False,
            'writethumbnail': True,
            'outtmpl': FOLDER+'%(title)s.%(etx)s',
            'noplaylist': True,
            'format': 'bestaudio/best',
            'progress_hooks': [my_hook],
            'logger': MyLogger(),
            'postprocessors': [{'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': '192'},
                                {'key': 'EmbedThumbnail'}]}
        try:
            #Checking the link
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(message.text, download=False)
                stream = info.get('is_live', None)
                url = info.get('url', None)
                length = info.get('duration', None)
                if url is None or 'google' not in url:
                    bot.send_message(message.from_user.id, "Only from youtube.com")
                else:
                    if stream:
                        bot.send_message(message.from_user.id, "Don't download streams")
                    if length > LIMIT:
                        bot.send_message(message.from_user.id, "File is too large")
                    else:
                        ydl.download([message.text])
                        file_list = glob.glob(os.path.join(FOLDER, '*.mp3'))
                        #Compare video duration
                        for fn in file_list:
                            audio = MP3(fn)
                            dutation = audio.info.length
                            if int(round(dutation)) == length:
                                with open (fn, 'rb') as f:
                                    bot.send_chat_action(message.from_user.id, 'upload_audio')
                                    bot.send_audio(message.from_user.id, f, timeout=500)
                                os.remove(str(fn))
                            else:
                                pass

        #If link isn't valid
        except youtube_dl.utils.DownloadError:
            bot.send_message(message.from_user.id, "The link isn't valid")
         #File size must be 50 MB
        except telebot.apihelper.ApiException:
            bot.send_message(message.from_user.id, "File is too large")
        #If link isn't valid
        except KeyError:
            bot.send_message(message.from_user.id, "The link isn't valid")
        except MutagenError:
            pass

#Infinite loop
bot.polling(none_stop=True, timeout=500)
