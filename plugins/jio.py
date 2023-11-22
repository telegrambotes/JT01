import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

import os
import re
import json
import math
import time
import shutil
import random
import ffmpeg
import asyncio
import requests
import subprocess

from WKSKEYS.pywidevin.L3.cdm import deviceconfig
from base64 import b64encode
from WKSKEYS.pywidevin.L3.getPSSH import get_pssh
from WKSKEYS.pywidevin.L3.decrypt.wvdecryptcustom import WvDecrypt

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from script import script

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from datetime import datetime

@Client.on_message(filters.private & filters.regex(pattern=".*http.*"))
async def Vrott_capture(bot, update):

    if update.from_user.id in Config.BANNED_USERS:
        await bot.delete_messages(
            chat_id=update.chat.id,
            message_ids=update.message_id,
            revoke=True
        )
        return

    logger.info(update.from_user.id)
    
    if "jiocinema" in update.text:
        async def get_accesstoken():
            IdURL = "https://cs-jv.voot.com/clickstream/v1/get-id"
            GuestURL = "https://auth-jiocinema.voot.com/tokenservice/apis/v4/guest"
            id = requests.get(url=IdURL).json()['id']
        
            token = requests.post(url=GuestURL, json={
                    'adId': id,
                    "appName": "RJIL_JioCinema",
                    "appVersion": "23.10.13.0-841c2bc7",
                    "deviceId": id,
                    "deviceType": "phone",
                    "freshLaunch": True,
                    "os": "ios"
                }, headers={
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
                }).json()
    
            return token["authToken"]

        access_token= get_accesstoken()

        try:
            w = update.text 
            link = "https://www.jiocinema.com/tv-shows/ramachari/1/vyshakha-hurts-charu/3850024"
            link_id = re.findall(r'.*/(.*)', link)[0].strip()
            
            # m3u8DL_RE = 'N_m3u8DL-RE'
            
            def replace_invalid_chars(title: str) -> str:
                invalid_chars = {'<': '\u02c2', '>': '\u02c3',
                ':': '\u02d0', '"': '\u02ba', '/': '\u2044',
                '\\': '\u29f9', '|': '\u01c0', '?': '\u0294',
                '*': '\u2217'}
                
                return ''.join(invalid_chars.get(c, c) for c in title)
            
            decoded = jwt.decode(access_token, options={"verify_signature": False})
            print(f'\n{decoded}\n')
            
            deviceId = decoded['data']['deviceId']
            uniqueid = decoded['data']['userId']
            appName = decoded['data']['appName']
            
            headers2 = {
                'authority': 'apis-jiovoot.voot.com',
                'accept': 'application/json, text/plain, */*',
                'accesstoken': access_token,
                'appname': appName,
                'content-type': 'application/json',
                'deviceid': deviceId,
                'origin': 'https://www.jiocinema.com',
                'referer': 'https://www.jiocinema.com/',
                'uniqueid': uniqueid,
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
                'versioncode': '560',
                'x-platform': 'androidweb',
                'x-platform-token': 'web',
            }
            
            json_data2 = {
                '4k': False,
                'ageGroup': '18+',
                'appVersion': '3.4.0',
                'bitrateProfile': 'xhdpi',
                'capability': {
                    'drmCapability': {
                        'aesSupport': 'yes',
                        'fairPlayDrmSupport': 'yes',
                        'playreadyDrmSupport': 'none',
                        'widevineDRMSupport': 'yes',
                    },
                    'frameRateCapability': [
                        {
                            'frameRateSupport': '30fps',
                            'videoQuality': '1440p',
                        },
                    ],
                },
                'continueWatchingRequired': True,
                'dolby': False,
                'downloadRequest': False,
                'hevc': False,
                'kidsSafe': False,
                'manufacturer': 'Windows',
                'model': 'Windows',
                'multiAudioRequired': True,
                'osVersion': '10',
                'parentalPinValid': True,
            }
            
            response2 = requests.post('https://apis-jiovoot.voot.com/playbackjv/v4/'+link_id+'', headers=headers2, json=json_data2, verify=False).json()
            
            contentType = response2['data']['contentType']
            
            if contentType == 'MOVIE':
                movie_name = response2['data']['name']
                title = f'{movie_name}'
            
            elif contentType == 'EPISODE':
                showName = response2['data']['show']['name']
                season_num = int(response2['data']['episode']['season'])
                episode_num = int(response2['data']['episode']['episodeNo'])
                episode_title = response2['data']['fullTitle']
                
                title = f'{showName} - S{season_num:02d}E{episode_num:02d} - {episode_title}'
                print(title)
            
            else:
                movie_name = response2['data']['name']
                title = f'{movie_name}'
            
            title = replace_invalid_chars(title)
            # print(f'\n{title}\n')
            
            mpd = response2['data']['playbackUrls'][0]['url']
            # print("MPD :\n",mpd)
            lic_url = response2['data']['playbackUrls'][0]['licenseurl']
            
            try:
                import requests
                
                headers03 = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Connection': 'keep-alive',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
                }
                
                response03 = requests.get(mpd, headers=headers03, verify=False).text
                
                pssh = re.findall(r'<cenc:pssh>(.{20,170})</cenc:pssh>', response03)[0].strip()
                print(f'{pssh}\n')
            
                import base64, requests, sys, xmltodict, json
                from WKSKEYS.pywidevin.L3.cdm import deviceconfig
                from base64 import b64encode
                from WKSKEYS.pywidevin.L3.getPSSH import get_pssh
                from WKSKEYS.pywidevin.L3.decrypt.wvdecryptcustom import WvDecrypt
                import re  
                
                headers = {
                    'authority': 'prod.media.jio.com',
                    'accesstoken': access_token,
                    'appname': appName,
                    'content-type': 'application/octet-stream',
                    'deviceid': deviceId,
                    'devicetype': 'Web',
                    'isdownload': 'false',
                    'origin': 'https://www.jiocinema.com',
                    'os': 'android',
                    'referer': 'https://www.jiocinema.com/',
                    'uniqueid': uniqueid,
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
                    'versioncode': '570',
                    'x-feature-code': 'ytvjywxwkn',
                    'x-platform': 'Web',
                    'x-playbackid': uniqueid,
                }
                
                def WV_Function(pssh, lic_url, cert_b64=None):
                    wvdecrypt = WvDecrypt(init_data_b64=pssh, cert_data_b64=cert_b64, device=deviceconfig.device_android_generic)                   
                    widevine_license = requests.post(url=lic_url, data=wvdecrypt.get_challenge(), headers=headers, verify=False)
                    license_b64 = b64encode(widevine_license.content)
                    wvdecrypt.update_license(license_b64)
                    Correct, keyswvdecrypt = wvdecrypt.start_process()
                    if Correct:
                        return Correct, keyswvdecrypt
                Correct, keys = WV_Function(pssh, lic_url)
                
                for key in keys:
                    print('--key ' + key)
                
                ke_ys = ' '.join([f'--key {key}' for key in keys]).split()
            
            url = mpd    
            logger.info(url)
            
        except:
            await update.reply_text("There's some issue with your URL 😕", quote=True)
            return
            
    else:
        await update.reply_text("I can download from jiocinema links only! 😇", quote=True)
        return
    
    try:
        mxplayer_capture.url = url    
        
        command_to_exec = [
            "youtube-dl",
            "--no-warnings",
            "--youtube-skip-dash-manifest",
            "-j",
            url,
            "--geo-bypass-country",
            "IN"
        ]
        
        process = await asyncio.create_subprocess_exec(
            *command_to_exec,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()

        if e_response:
            logger.info(e_response)

        if t_response:
            x_reponse = t_response
            if "\n" in x_reponse:
                x_reponse, _ = x_reponse.split("\n")
            response_json = json.loads(x_reponse)
            save_ytdl_json_path = Config.DOWNLOAD_LOCATION + \
                "/" + str(update.from_user.id) + ".json"
            with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
                json.dump(response_json, outfile, ensure_ascii=False)
            inline_keyboard = []
            duration = None
            if "duration" in response_json:
                duration = response_json["duration"]
            if "formats" in response_json:
                for formats in response_json["formats"]:
                    format_id = formats.get("format_id")
                    format_string = formats.get("format_note")
                    if format_string is None:
                        format_string = formats.get("format")
                    format_ext = formats.get("ext")
                    approx_file_size = ""
                    if "filesize" in formats:
                        approx_file_size = humanbytes(formats["filesize"])
                    cb_string_video = "{}|{}|{}".format(
                        "video", format_id, format_ext)
                    cb_string_file = "{}|{}|{}".format(
                        "file", format_id, format_ext)
                    if format_string is not None and not "audio only" in format_string:
                        ikeyboard = [
                            InlineKeyboardButton(
                                "🎞 (" + format_string + ") " + approx_file_size + " ",
                                callback_data=(cb_string_video).encode("UTF-8")
                            ),
                            InlineKeyboardButton(
                                "📁 FILE " + format_ext + " " + approx_file_size + " ",
                                callback_data=(cb_string_file).encode("UTF-8")
                            )
                        ]                           
                        inline_keyboard.append(ikeyboard)
                        
            inline_keyboard.append([
                InlineKeyboardButton(
                    "✖️ CLOSE ✖️",
                     callback_data=(
                        "closeformat").encode("UTF-8")
                )
             ])

            reply_markup = InlineKeyboardMarkup(inline_keyboard)
            thumbnail = Config.DEF_THUMB_NAIL_VID_S
            thumbnail_image = Config.DEF_THUMB_NAIL_VID_S
            if "thumbnail" in response_json:
               if response_json["thumbnail"] is not None:
                   thumbnail = response_json["thumbnail"]
                   thumbnail_image = response_json["thumbnail"]
            thumb_image_path = DownLoadFile(
                thumbnail_image,
                Config.DOWNLOAD_LOCATION + "/" +
                str(update.from_user.id) + ".jpg",
                Config.CHUNK_SIZE,
                None,  # bot,
                script.DOWNLOAD_START,
                update.message_id,
                update.chat.id
            )   
 
            await bot.send_message(
                chat_id=update.chat.id,
                text=script.FORMAT_SELECTION.format(thumbnail),
                reply_markup=reply_markup,
                parse_mode="html",
                reply_to_message_id=update.message_id
            )
        else:
            await update.reply_text("There's some issue with your URL 😕 Or may be DRM protected!", quote=True)
            return
    except:
        await update.reply_text("Couldn't download your video!", quote=True)
        logger.info('format send error')
        return
             
async def mxplayer_execute(bot, update):
  
    try:
        cb_data = update.data
        tg_send_type, youtube_dl_format, youtube_dl_ext = cb_data.split("|")
        
        thumb_image_path = Config.DOWNLOAD_LOCATION + \
            "/" + str(update.from_user.id) + ".jpg"

        save_ytdl_json_path = Config.DOWNLOAD_LOCATION + \
            "/" + str(update.from_user.id) + ".json"
        try:
            with open(save_ytdl_json_path, "r", encoding="utf8") as f:
                response_json = json.load(f)
        except (FileNotFoundError) as e:
            await bot.delete_messages(
                chat_id=update.message.chat.id,
                message_ids=update.message.message_id,
                revoke=True
            )
            return False
        
        youtube_dl_url = mxplayer_capture.url
        
        linksplit = update.message.reply_to_message.text.split("/")
        videoname = linksplit[+5]
        logger.info(videoname)
        
        custom_file_name = videoname + ".mp4"

        await bot.edit_message_text(
            text=script.DOWNLOAD_START,
            chat_id=update.message.chat.id,
            message_id=update.message.message_id
        )
        description = script.CUSTOM_CAPTION_UL_FILE.format(newname=custom_file_name)

        tmp_directory_for_each_user = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id)
        if not os.path.isdir(tmp_directory_for_each_user):
            os.makedirs(tmp_directory_for_each_user)
        download_directory = tmp_directory_for_each_user + "/" + custom_file_name
        command_to_exec = []
        
        minus_f_format = youtube_dl_format + "+bestaudio"
        command_to_exec = [
            "youtube-dl",
            "-c",
            "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
            "-f", minus_f_format,
            "--hls-prefer-ffmpeg", youtube_dl_url,
            "-o", download_directory
        ]                  
        command_to_exec.append("--no-warnings")
        command_to_exec.append("--geo-bypass-country")
        command_to_exec.append("IN")
        
        start = datetime.now()
        process = await asyncio.create_subprocess_exec(
            *command_to_exec,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()

        if os.path.isfile(download_directory):
            logger.info("no issues")
        else:
            logger.info("issues found, passing to sub process")
            command_to_exec.clear()
            minus_f_format = youtube_dl_format
            command_to_exec = [
                "youtube-dl",
                "-c",
                "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
                "-f", minus_f_format,
                "--hls-prefer-ffmpeg", youtube_dl_url,
                "-o", download_directory
            ]                  
            command_to_exec.append("--no-warnings")
            command_to_exec.append("--geo-bypass-country")
            command_to_exec.append("IN")
        
            start = datetime.now()
            process = await asyncio.create_subprocess_exec(
                *command_to_exec,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            e_response = stderr.decode().strip()
            t_response = stdout.decode().strip()

        ad_string_to_replace = "please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output."
        if e_response and ad_string_to_replace in e_response:
            error_message = e_response.replace(ad_string_to_replace, "")
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                message_id=update.message.message_id,
                text=error_message
            )
            return False
        if t_response:
            os.remove(save_ytdl_json_path)
            end_one = datetime.now()
            time_taken_for_download = (end_one -start).seconds
            file_size = Config.TG_MAX_FILE_SIZE + 1
            try:
                file_size = os.stat(download_directory).st_size
            except FileNotFoundError as exc:
                download_directory = os.path.splitext(download_directory)[0] + "." + "mp4"
                file_size = os.stat(download_directory).st_size
            if file_size > Config.TG_MAX_FILE_SIZE:
                await bot.edit_message_text(
                    chat_id=update.message.chat.id,
                    text=script.RCHD_TG_API_LIMIT.format(time_taken_for_download, humanbytes(file_size)),
                    message_id=update.message.message_id
                )
            else:
                await bot.edit_message_text(
                    text=script.UPLOAD_START,
                    chat_id=update.message.chat.id,
                    message_id=update.message.message_id
                )

                # get the correct width, height, and duration for videos greater than 10MB
                width = 0
                height = 0
                duration = 0
                if tg_send_type != "file":
                    metadata = extractMetadata(createParser(download_directory))
                    if metadata is not None:
                        if metadata.has("duration"):
                            duration = metadata.get('duration').seconds            
                # get the correct width, height, and duration for videos greater than 10MB
                
                if not os.path.exists(thumb_image_path):
                    mes = await thumb(update.from_user.id)
                    if mes != None:
                        m = await bot.get_messages(update.chat.id, mes.msg_id)
                        await m.download(file_name=thumb_image_path)
                        thumb_image_path = thumb_image_path
                    else:
                        try:
                            thumb_image_path = await take_screen_shot(
                                download_directory,
                                os.path.dirname(download_directory),
                                random.randint(
                                    0,
                                    duration - 1
                                )
                            )
                        except:
                            thumb_image_path = None
                            pass  
                else:
                    width = 0
                    height = 0
                    metadata = extractMetadata(createParser(thumb_image_path))
                    if metadata.has("width"):
                        width = metadata.get("width")
                    if metadata.has("height"):
                        height = metadata.get("height")
                    if tg_send_type == "vm":
                        height = width               
                    Image.open(thumb_image_path).convert(
                        "RGB").save(thumb_image_path)
                    img = Image.open(thumb_image_path)
                    img.thumbnail((90, 90))
                    if tg_send_type == "file":
                        img.resize((320, height))
                    else:
                        img.resize((90, height))
                    img.save(thumb_image_path, "JPEG")
  
                start_time = time.time()

                if tg_send_type == "file":
                    await bot.send_document(
                        chat_id=update.message.chat.id,
                        document=download_directory,
                        thumb=thumb_image_path,
                        caption=description,
                        parse_mode="HTML",
                        # reply_markup=reply_markup,
                        reply_to_message_id=update.message.reply_to_message.message_id,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            script.UPLOAD_START,
                            update.message,
                            start_time
                        )
                    )
                elif tg_send_type == "video":
                    await bot.send_video(
                        chat_id=update.message.chat.id,
                        video=download_directory,
                        caption=description,
                        parse_mode="HTML",
                        duration=duration,
                        width=width,
                        height=height,
                        supports_streaming=True,
                        # reply_markup=reply_markup,
                        thumb=thumb_image_path,
                        reply_to_message_id=update.message.reply_to_message.message_id,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            script.UPLOAD_START,
                            update.message,
                            start_time
                        )
                    )
                else:
                    logger.info("Did this happen? :\\")

                try:
                    shutil.rmtree(tmp_directory_for_each_user)
                except:
                    pass
                try:
                    os.remove(thumb_image_path)
                except:
                    pass

                await bot.edit_message_text(
                    text=script.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="🙌🏻 SHARE ME 🙌🏻", url="https://t.me/share/url?url=https://t.me/Dads_links_bot")]]),
                    chat_id=update.message.chat.id,
                    message_id=update.message.message_id,
                    disable_web_page_preview=True
                )               
    except:
        await update.reply_text("Couldn't download your video!", quote=True)
        logger.info('error in process')
