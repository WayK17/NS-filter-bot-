import os, requests
import logging
import random
import asyncio
import string
import pytz
from datetime import timedelta
from datetime import datetime as dt
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, ReplyKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, get_bad_files, unpack_new_file_id
from database.users_chats_db import db
from database.config_db import mdb
from database.topdb import JsTopDB
from database.jsreferdb import referdb
from plugins.pm_filter import auto_filter
from utils import formate_file_name, get_settings, save_group_settings, is_req_subscribed, get_size, get_shortlink, is_check_admin, get_status, temp, get_readable_time, save_default_settings
import re
import base64
from info import *
import traceback
logger = logging.getLogger(__name__)
movie_series_db = JsTopDB(DATABASE_URI)
verification_ids = {}

# REVISAR LA CARPETA "components" PARA MÁS COMANDOS
@Client.on_message(filters.command("invite") & filters.private & filters.user(ADMINS))
async def invite(client, message):
    toGenInvLink = message.command[1]
    if len(toGenInvLink) != 14:
        return await message.reply("ID de chat inválido\nAgrega -100 antes del ID del chat si aún no lo has agregado.")
    try:
        link = await client.export_chat_invite_link(toGenInvLink)
        await message.reply(link)
    except Exception as e:
        print(f'Error al generar el enlace de invitación: {e}\nPara el chat: {toGenInvLink}')
        await message.reply(f'Error al generar el enlace de invitación: {e}\nPara el chat: {toGenInvLink}')

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client: Client, message):
    await message.react(emoji=random.choice(REACTIONS))
    pm_mode = False
    try:
         data = message.command[1]
         if data.startswith('pm_mode_'):
             pm_mode = True
    except:
        pass
    m = message
    user_id = m.from_user.id
    if len(m.command) == 2 and m.command[1].startswith('notcopy'):
        _, userid, verify_id, file_id = m.command[1].split("_", 3)
        user_id = int(userid)
        grp_id = temp.CHAT.get(user_id, 0)
        settings = await get_settings(grp_id)
        verify_id_info = await db.get_verify_id_info(user_id, verify_id)
        if not verify_id_info or verify_id_info["verified"]:
            await message.reply("<b>El enlace ha expirado, intenta de nuevo...</b>")
            return  
        ist_timezone = pytz.timezone('Asia/Kolkata')
        if await db.user_verified(user_id):
            key = "third_time_verified"
        else:
            key = "second_time_verified" if await db.is_user_verified(user_id) else "last_verified"
        current_time = dt.now(tz=ist_timezone)
        result = await db.update_notcopy_user(user_id, {key: current_time})
        await db.update_verify_id_info(user_id, verify_id, {"verified": True})
        if key == "third_time_verified": 
            num = 3 
        else: 
            num = 2 if key == "second_time_verified" else 1 
        if key == "third_time_verified":
            msg = script.THIRDT_VERIFY_COMPLETE_TEXT
        else:
            msg = script.SECOND_VERIFY_COMPLETE_TEXT if key == "second_time_verified" else script.VERIFY_COMPLETE_TEXT
        await client.send_message(settings['log'], script.VERIFIED_LOG_TEXT.format(m.from_user.mention, user_id, dt.now(pytz.timezone('Asia/Kolkata')).strftime('%d %B %Y'), num))
        btn = [[
            InlineKeyboardButton("‼️ HAZ CLIC AQUÍ PARA OBTENER EL ARCHIVO ‼️", url=f"https://telegram.me/{temp.U_NAME}?start=file_{grp_id}_{file_id}"),
        ]]
        reply_markup = InlineKeyboardMarkup(btn)
        await m.reply_photo(
            photo=VERIFY_IMG,
            caption=msg.format(message.from_user.mention, get_readable_time(TWO_VERIFY_GAP)),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return 
        # refer
    if len(message.command) == 2 and message.command[1].startswith("reff_"):
        try:
            user_id = int(message.command[1].split("_")[1])
        except ValueError:
            await message.reply_text("¡Referencia inválida!")
            return
        if user_id == message.from_user.id:
            await message.reply_text("Oye, no puedes referirte a ti mismo.")
            return
        if referdb.is_user_in_list(message.from_user.id):
            await message.reply_text("‼️ Ya has sido invitado o te has unido previamente")
            return
        if await db.is_user_exist(message.from_user.id): 
            await message.reply_text("‼️ Ya has sido invitado o te has unido previamente")
            return            
        try:
            uss = await client.get_users(user_id)
        except Exception:
            return
        referdb.add_user(message.from_user.id)
        fromuse = referdb.get_refer_points(user_id) + 10
        if fromuse == 100:
            referdb.add_refer_points(user_id, 0) 
            await message.reply_text(f"¡Has sido invitado exitosamente por {uss.mention}!") 
            await client.send_message(user_id, text=f"¡Has sido invitado exitosamente por {message.from_user.mention}!") 
            await add_premium(client, user_id, uss)
        else:
            referdb.add_refer_points(user_id, fromuse)
            await message.reply_text(f"¡Has sido invitado exitosamente por {uss.mention}!")
            await client.send_message(user_id, f"¡Has sido invitado exitosamente por {message.from_user.mention}!")
        return

    if len(message.command) == 2 and message.command[1].startswith('getfile'):
        searches = message.command[1].split("-", 1)[1] 
        search = searches.replace('-', ' ')
        message.text = search 
        await auto_filter(client, message) 
        return

    if len(message.command) == 2 and message.command[1] in ["ads"]:
        msg, _, impression = await mdb.get_advirtisment()
        user = await db.get_user(message.from_user.id)
        seen_ads = user.get("seen_ads", False)
        JISSHU_ADS_LINK = await db.jisshu_get_ads_link()
        buttons = [[
                    InlineKeyboardButton('❌ CERRAR ❌', callback_data='close_data')
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        if msg:
            await message.reply_photo(
                photo=JISSHU_ADS_LINK if JISSHU_ADS_LINK else URL,
                caption=msg,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            if impression is not None and not seen_ads:
                await mdb.update_advirtisment_impression(int(impression) - 1)
                await db.update_value(message.from_user.id, "seen_ads", True)
        else:
            await message.reply("<b>No se encontraron anuncios</b>")
        await mdb.reset_advertisement_if_expired()
        if msg is None and seen_ads:
            await db.update_value(message.from_user.id, "seen_ads", False)
        return

    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        status = get_status()
        aks = await message.reply_text(f"<b>🔥 Sí {status},\n¿Cómo puedo ayudarte?</b>")
        await asyncio.sleep(600)
        await aks.delete()
        await m.delete()
        if (str(message.chat.id)).startswith("-100") and not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            group_link = await message.chat.export_invite_link()
            user = message.from_user.mention if message.from_user else "Estimado"
            await client.send_message(LOG_CHANNEL, script.NEW_GROUP_TXT.format(temp.B_LINK, message.chat.title, message.chat.id, message.chat.username, group_link, total, user))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.NEW_USER_TXT.format(temp.B_LINK, message.from_user.id, message.from_user.mention))
        try: 
            if AUTH_CHANNEL and await is_req_subscribed(client, message):
                buttons = [[
                    InlineKeyboardButton('☆ Agrégame a tu grupo ☆', url=f'http://t.me/{temp.U_NAME}?startgroup=start')
                ],[
                    InlineKeyboardButton("Ayuda ⚙️", callback_data='features')
                ],[
                    InlineKeyboardButton('Búsqueda 🔍', callback_data="mostsearch"),
                    InlineKeyboardButton('Tendencias ⚡', callback_data="trending")
                ]] 
                reply_markup = InlineKeyboardMarkup(buttons)
                m = await message.reply_sticker("CAACAgQAAxkBAAEn9_ZmGp1uf1a38UrDhitnjOOqL1oG3gAC9hAAAlC74FPEm2DxqNeOmB4E") 
                await asyncio.sleep(1)
                await m.delete()
                await message.reply_photo(
                    photo=random.choice(START_IMG),
                    caption=script.START_TXT.format(message.from_user.mention, get_status(), message.from_user.id),
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML
                )
        except Exception as e:
            traceback.print_exc()
            pass
    if len(message.command) != 2:
        buttons = [[
                    InlineKeyboardButton('☆ Agrégame a tu grupo ☆', url=f'http://t.me/{temp.U_NAME}?startgroup=start')
                ],[
                    InlineKeyboardButton("Ayuda ⚙️", callback_data='features')
                ],[
                    InlineKeyboardButton('Búsqueda 🔍', callback_data="mostsearch"),
                    InlineKeyboardButton('Tendencias ⚡', callback_data="trending")
                ]] 
        reply_markup = InlineKeyboardMarkup(buttons)
        m = await message.reply_sticker("CAACAgQAAxkBAAEn9_ZmGp1uf1a38UrDhitnjOOqL1oG3gAC9hAAAlC74FPEm2DxqNeOmB4E") 
        await asyncio.sleep(1)
        await m.delete()
        await message.reply_photo(
            photo=random.choice(START_IMG),
            caption=script.START_TXT.format(message.from_user.mention, get_status(), message.from_user.id),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    if AUTH_CHANNEL and not await is_req_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL), creates_join_request=True)
        except ChatAdminRequired:
            logger.error("Asegúrate de que el bot sea administrador en el canal de suscripción forzada")
            return
        btn = [[
            InlineKeyboardButton("🔥 ÚNETE AHORA 💧", url=invite_link.invite_link)
        ]]
        if message.command[1] != "subscribe":
            try:
                chksub_data = message.command[1].replace('pm_mode_', '') if pm_mode else message.command[1]
                kk, grp_id, file_id = chksub_data.split('_', 2)
                pre = 'checksubp' if kk == 'filep' else 'checksub'
                btn.append(
                    [InlineKeyboardButton("♻️ INTENTA DE NUEVO ♻️", callback_data=f"checksub#{file_id}#{int(grp_id)}")]
                )
            except (IndexError, ValueError):
                print('IndexError: ', IndexError)
                btn.append(
                    [InlineKeyboardButton("♻️ INTENTA DE NUEVO ♻️", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")]
                )
        reply_markup = InlineKeyboardMarkup(btn)
        await client.send_photo(
            chat_id=message.from_user.id,
            photo=FORCESUB_IMG, 
            caption=script.FORCESUB_TEXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return

    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
            InlineKeyboardButton('☆ Agrégame a tu grupo ☆', url=f'http://t.me/{temp.U_NAME}?startgroup=start')
        ],[
            InlineKeyboardButton("Ayuda ⚙️", callback_data='features')
        ],[
            InlineKeyboardButton('Búsqueda 🔍', callback_data="mostsearch"),
            InlineKeyboardButton('Tendencias ⚡', callback_data="trending")
        ]] 
        reply_markup = InlineKeyboardMarkup(buttons)
        return await message.reply_photo(
            photo=START_IMG,
            caption=script.START_TXT.format(message.from_user.mention, get_status(), message.from_user.id),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    if data.startswith('pm_mode_'):
        pm_mode = True
        data = data.replace('pm_mode_', '')
    try:
        pre, grp_id, file_id = data.split('_', 2)
    except:
        pre, grp_id, file_id = "", 0, data

    user_id = m.from_user.id
    if not await db.has_premium_access(user_id):
        grp_id = int(grp_id)
        user_verified = await db.is_user_verified(user_id)
        settings = await get_settings(grp_id, pm_mode=pm_mode)
        is_second_shortener = await db.use_second_shortener(user_id, settings.get('verify_time', TWO_VERIFY_GAP))
        is_third_shortener = await db.use_third_shortener(user_id, settings.get('third_verify_time', THREE_VERIFY_GAP))
        if settings.get("is_verify", IS_VERIFY) and not user_verified or is_second_shortener or is_third_shortener:
            verify_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
            await db.create_verify_id(user_id, verify_id)
            temp.CHAT[user_id] = grp_id
            verify = await get_shortlink(f"https://telegram.me/{temp.U_NAME}?start=notcopy_{user_id}_{verify_id}_{file_id}", grp_id, is_second_shortener, is_third_shortener, pm_mode=pm_mode)
            if is_third_shortener:
                howtodownload = settings.get('tutorial_3', TUTORIAL_3)
            else:
                howtodownload = settings.get('tutorial_2', TUTORIAL_2) if is_second_shortener else settings.get('tutorial', TUTORIAL)
            buttons = [[
                InlineKeyboardButton(text="✅ VERIFICAR ✅", url=verify),
                InlineKeyboardButton(text="¿CÓMO VERIFICAR?", url=howtodownload)
            ],[
                InlineKeyboardButton(text="😁 COMPRAR SUSCRIPCIÓN - SIN VERIFICAR 😁", callback_data='seeplans'),
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            if await db.user_verified(user_id): 
                msg = script.THIRDT_VERIFICATION_TEXT
            else:            
                msg = script.SECOND_VERIFICATION_TEXT if is_second_shortener else script.VERIFICATION_TEXT
            d = await m.reply_text(
                text=msg.format(message.from_user.mention, get_status()),
                protect_content=False,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            await asyncio.sleep(300)
            await d.delete()
            await m.delete()
            return

    if data and data.startswith("allfiles"):
        _, key = data.split("_", 1)
        files = temp.FILES_ID.get(key)
        if not files:
            await message.reply_text("<b>⚠️ No se encontraron todos los archivos ⚠️</b>")
            return
        files_to_delete = []
        for file in files:
            user_id = message.from_user.id 
            grp_id = temp.CHAT.get(user_id)
            settings = await get_settings(grp_id, pm_mode=pm_mode)
            CAPTION = settings['caption']
            f_caption = CAPTION.format(
                file_name=formate_file_name(file.file_name),
                file_size=get_size(file.file_size),
                file_caption=file.caption
            )
            btn = [[
                InlineKeyboardButton("✛ VER Y DESCARGAR ✛", callback_data=f'stream#{file.file_id}')
            ]]
            toDel = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file.file_id,
                caption=f_caption,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            files_to_delete.append(toDel)
        delCap = "<b>Todos los {} archivos serán eliminados después de {} para evitar violaciones de derechos de autor.</b>".format(
            len(files_to_delete),
            f'{FILE_AUTO_DEL_TIMER / 60} minutos' if FILE_AUTO_DEL_TIMER >= 60 else f'{FILE_AUTO_DEL_TIMER} segundos'
        )
        afterDelCap = "<b>Todos los {} archivos han sido eliminados después de {} para evitar violaciones de derechos de autor.</b>".format(
            len(files_to_delete),
            f'{FILE_AUTO_DEL_TIMER / 60} minutos' if FILE_AUTO_DEL_TIMER >= 60 else f'{FILE_AUTO_DEL_TIMER} segundos'
        )
        replyed = await message.reply(delCap)
        await asyncio.sleep(FILE_AUTO_DEL_TIMER)
        for file in files_to_delete:
            try:
                await file.delete()
            except:
                pass
        return await replyed.edit(afterDelCap)
    if not data:
        return
    files_ = await get_file_details(file_id)
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        return await message.reply('<b>⚠️ No se encontraron archivos ⚠️</b>')
    files = files_[0]
    settings = await get_settings(grp_id, pm_mode=pm_mode)
    CAPTION = settings['caption']
    f_caption = CAPTION.format(
        file_name=formate_file_name(files.file_name),
        file_size=get_size(files.file_size),
        file_caption=files.caption
    )
    btn = [[
        InlineKeyboardButton("✛ VER Y DESCARGAR ✛", callback_data=f'stream#{file_id}')
    ]]
    toDel = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        reply_markup=InlineKeyboardMarkup(btn)
    )
    delCap = "<b>Tu archivo será eliminado después de {} para evitar violaciones de derechos de autor.</b>".format(
        f'{FILE_AUTO_DEL_TIMER / 60} minutos' if FILE_AUTO_DEL_TIMER >= 60 else f'{FILE_AUTO_DEL_TIMER} segundos'
    )
    afterDelCap = "<b>Tu archivo ha sido eliminado después de {} para evitar violaciones de derechos de autor.</b>".format(
        f'{FILE_AUTO_DEL_TIMER / 60} minutos' if FILE_AUTO_DEL_TIMER >= 60 else f'{FILE_AUTO_DEL_TIMER} segundos'
    )
    replyed = await message.reply(delCap, reply_to_message_id=toDel.id)
    await asyncio.sleep(FILE_AUTO_DEL_TIMER)
    await toDel.delete()
    return await replyed.edit(afterDelCap)


@Client.on_message(filters.command('delete'))
async def delete(bot, message):
    if message.from_user.id not in ADMINS:
        await message.reply('Solo el propietario del bot puede usar este comando... 😑')
        return
    """Eliminar archivo de la base de datos"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Procesando...⏳", quote=True)
    else:
        await message.reply('Responde al archivo con /delete que deseas eliminar', quote=True)
        return
    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('<b>Este formato de archivo no es soportado</b>')
        return
    file_id, file_ref = unpack_new_file_id(media.file_id)
    result = await Media.collection.delete_one({'_id': file_id})
    if result.deleted_count:
        await msg.edit('<b>El archivo ha sido eliminado exitosamente de la base de datos 💥</b>')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
        })
        if result.deleted_count:
            await msg.edit('<b>El archivo ha sido eliminado exitosamente de la base de datos 💥</b>')
        else:
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('<b>El archivo ha sido eliminado exitosamente de la base de datos 💥</b>')
            else:
                await msg.edit('<b>No se encontró el archivo en la base de datos</b>')


@Client.on_message(filters.command('deleteall'))
async def delete_all_index(bot, message):
    files = await Media.count_documents()
    if int(files) == 0:
        return await message.reply_text('No hay archivos para eliminar')
    btn = [[
            InlineKeyboardButton(text="sí", callback_data="all_files_delete")
        ],[
            InlineKeyboardButton(text="cancelar", callback_data="close_data")
        ]]
    if message.from_user.id not in ADMINS:
        await message.reply('Solo el propietario del bot puede usar este comando... 😑')
        return
    await message.reply_text('<b>Esto eliminará todos los archivos indexados.\n¿Deseas continuar?</b>', reply_markup=InlineKeyboardMarkup(btn))


@Client.on_message(filters.command('settings'))
async def settings(client, message):
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return await message.reply("<b>💔 Eres anónimo, como administrador no puedes usar este comando...</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<code>Usa este comando en un grupo.</code>")
    grp_id = message.chat.id
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>No eres administrador en este grupo</b>')
    settings = await get_settings(grp_id)
    title = message.chat.title
    if settings is not None:
          buttons = [[
              InlineKeyboardButton('Auto Filtro', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}'),
              InlineKeyboardButton('Encendido ✓' if settings["auto_filter"] else 'Apagado ✗', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}')
            ],[
              InlineKeyboardButton('IMDb', callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}'),
              InlineKeyboardButton('Encendido ✓' if settings["imdb"] else 'Apagado ✗', callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}')
            ],[
              InlineKeyboardButton('Revisión ortográfica', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}'),
              InlineKeyboardButton('Encendido ✓' if settings["spell_check"] else 'Apagado ✗', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}')
            ],[
              InlineKeyboardButton('Auto Eliminar', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}'),
              InlineKeyboardButton(f'{get_readable_time(DELETE_TIME)}' if settings["auto_delete"] else 'Apagado ✗', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}')
            ],[
             InlineKeyboardButton('Modo de Resultado', callback_data=f'setgs#link#{settings["link"]}#{str(grp_id)}'),
                  InlineKeyboardButton('⛓ Enlace' if settings["link"] else '🧲 Botón', callback_data=f'setgs#link#{settings["link"]}#{str(grp_id)}')
            ],[
                  InlineKeyboardButton('❌ Cerrar ❌', callback_data='close_data')
            ]]
            await message.reply_text(
                  text=f"Cambia tus configuraciones para <b>'{title}'</b> como desees ✨",
                  reply_markup=InlineKeyboardMarkup(buttons),
                  parse_mode=enums.ParseMode.HTML
            )
    else:
        await message.reply_text('<b>Algo salió mal</b>')

@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>Usa este comando en un grupo...</b>")
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>No eres administrador en este grupo</b>')
    try:
        template = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("Comando incompleto!")    
    await save_group_settings(grp_id, 'template', template)
    await message.reply_text(f"Plantilla cambiada exitosamente para {title} a\n\n{template}", disable_web_page_preview=True)

@Client.on_message(filters.command("send"))
async def send_msg(bot, message):
    if message.from_user.id not in ADMINS:
        await message.reply('<b>Sólo el propietario del bot puede usar este comando...</b>')
        return
    if message.reply_to_message:
        target_ids = message.text.split(" ")[1:]
        if not target_ids:
            await message.reply_text("<b>Por favor proporciona uno o más ID de usuario separados por espacios...</b>")
            return
        out = "\n\n"
        success_count = 0
        try:
            users = await db.get_all_users()
            for target_id in target_ids:
                try:
                    user = await bot.get_users(target_id)
                    out += f"{user.id}\n"
                    await message.reply_to_message.copy(int(user.id))
                    success_count += 1
                except Exception as e:
                    out += f"‼️ Error en este ID - <code>{target_id}</code> <code>{str(e)}</code>\n"
            await message.reply_text(f"<b>✅ Mensaje enviado exitosamente a `{success_count}` ID\n<code>{out}</code></b>")
        except Exception as e:
            await message.reply_text(f"<b>‼️ Error - <code>{e}</code></b>")
    else:
        await message.reply_text("<b>Usa este comando como respuesta a un mensaje, por ejemplo: <code>/send userid1 userid2</code></b>")

@Client.on_message(filters.regex("#request"))
async def send_request(bot, message):
    try:
        request = message.text.split(" ", 1)[1]
    except:
        await message.reply_text("<b>‼️ Tu solicitud está incompleta</b>")
        return
    buttons = [[
        InlineKeyboardButton('👀 Ver solicitud', url=f"{message.link}")
    ],[
        InlineKeyboardButton('⚙ Mostrar opciones', callback_data=f'show_options#{message.from_user.id}#{message.id}')
    ]]
    sent_request = await bot.send_message(REQUEST_CHANNEL, script.REQUEST_TXT.format(message.from_user.mention, message.from_user.id, request), reply_markup=InlineKeyboardMarkup(buttons))
    btn = [[
         InlineKeyboardButton('✨ Ver tu solicitud ✨', url=f"{sent_request.link}")
    ]]
    await message.reply_text("<b>✅ Tu solicitud se ha agregado exitosamente, por favor espera un momento...</b>", reply_markup=InlineKeyboardMarkup(btn))

@Client.on_message(filters.command("search"))
async def search_files(bot, message):
    if message.from_user.id not in ADMINS:
        await message.reply('Solo el propietario del bot puede usar este comando... 😑')
        return
    chat_type = message.chat.type
    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hola {message.from_user.mention}, este comando no funciona en grupos. Funciona sólo en mi chat privado!</b>")  
    try:
        keyword = message.text.split(" ", 1)[1]
    except IndexError:
        return await message.reply_text(f"<b>Hola {message.from_user.mention}, proporcióname una palabra clave junto con el comando para eliminar archivos.</b>")
    files, total = await get_bad_files(keyword)
    if int(total) == 0:
        await message.reply_text('<i>No pude encontrar ningún archivo con esta palabra clave 😐</i>')
        return 
    file_names = "\n\n".join(f"{index + 1}. {item['file_name']}" for index, item in enumerate(files))
    file_data = f"🚫 Tu búsqueda - '{keyword}':\n\n{file_names}"    
    with open("file_names.txt", "w", encoding='utf-8') as file:
        file.write(file_data)
    await message.reply_document(
        document="file_names.txt",
        caption=f"<b>♻️ Según tu búsqueda, encontré <code>{total}</code> archivos</b>",
        parse_mode=enums.ParseMode.HTML
    )
    os.remove("file_names.txt")

@Client.on_message(filters.command("deletefiles"))
async def deletemultiplefiles(bot, message):
    if message.from_user.id not in ADMINS:
        await message.reply('Solo el propietario del bot puede usar este comando... 😑')
        return
    chat_type = message.chat.type
    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hola {message.from_user.mention}, este comando no funciona en grupos. Funciona sólo en mi chat privado!</b>")    
    try:
        keyword = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(f"<b>Hola {message.from_user.mention}, proporcióname una palabra clave junto con el comando para eliminar archivos.</b>")   
    files, total = await get_bad_files(keyword)
    if int(total) == 0:
        await message.reply_text('<i>No pude encontrar ningún archivo con esta palabra clave 😐</i>')
        return 
    btn = [[
       InlineKeyboardButton("sí, continuar ✅", callback_data=f"killfilesak#{keyword}")
       ],[
       InlineKeyboardButton("no, abortar operación 😢", callback_data="close_data")
    ]]
    await message.reply_text(
        text=f"<b>Total de archivos encontrados - <code>{total}</code>\n\n¿Deseas continuar?\n\nNOTA: ¡Esta acción puede ser destructiva!</b>",
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command("del_file"))
async def delete_files(bot, message):
    if message.from_user.id not in ADMINS:
        await message.reply('Solo el propietario del bot puede usar este comando... 😑')
        return
    chat_type = message.chat.type
    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hola {message.from_user.mention}, este comando no funciona en grupos. Funciona sólo en mi chat privado!</b>")    
    try:
        keywords = message.text.split(" ", 1)[1].split(",")
    except IndexError:
        return await message.reply_text(f"<b>Hola {message.from_user.mention}, proporcióname palabras clave separadas por comas junto con el comando para eliminar archivos.</b>")   
    deleted_files_count = 0
    not_found_files = []
    for keyword in keywords:
        result = await Media.collection.delete_many({'file_name': keyword.strip()})
        if result.deleted_count:
            deleted_files_count += 1
        else:
            not_found_files.append(keyword.strip())
    if deleted_files_count > 0:
        await message.reply_text(f'<b>{deleted_files_count} archivo(s) eliminados exitosamente de la base de datos 💥</b>')
    if not_found_files:
        await message.reply_text(f'<b>Archivos no encontrados en la base de datos - <code>{", ".join(not_found_files)}</code></b>')

@Client.on_message(filters.command('set_caption'))
async def save_caption(client, message):
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>No eres administrador en este grupo</b>')
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>Usa este comando en un grupo...</b>")
    try:
        caption = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("Comando incompleto!")
    await save_group_settings(grp_id, 'caption', caption)
    await message.reply_text(f"Se cambió la leyenda para {title} a\n\n{caption}", disable_web_page_preview=True)

@Client.on_message(filters.command('set_tutorial'))
async def save_tutorial(client, message):
    grp_id = message.chat.id
    title = message.chat.title
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>Usa este comando en un grupo...</b>")
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>No eres administrador en este grupo</b>')
    try:
        tutorial = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("<b>Comando incompleto!!\n\nUsa de esta forma -</b>\n\n<code>/set_tutorial https://t.me/Jisshu_support</code>")    
    await save_group_settings(grp_id, 'tutorial', tutorial)
    await message.reply_text(f"<b>Cambio exitoso del tutorial de verificación 1 para {title} a</b>\n\n{tutorial}", disable_web_page_preview=True)

@Client.on_message(filters.command('set_tutorial_2'))
async def set_tutorial_2(client, message):
    grp_id = message.chat.id
    title = message.chat.title
    invite_link = await client.export_chat_invite_link(grp_id)
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>No eres administrador en este grupo</b>')
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text(f"<b>Usa este comando en un grupo...\n\nNombre del Grupo: {title}\nID del Grupo: {grp_id}\nEnlace de Invitación: {invite_link}</b>")
    try:
        tutorial = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("<b>Comando incompleto !!\n\nUsa de esta forma -</b>\n\n<code>/set_tutorial_2 https://t.me/DwldMS/2</code>")
    await save_group_settings(grp_id, 'tutorial_2', tutorial)
    await message.reply_text(f"<b>Cambio exitoso del tutorial de verificación 2 para {title} a</b>\n\n{tutorial}", disable_web_page_preview=True)

@Client.on_message(filters.command('set_tutorial_3'))
async def set_tutorial_3(client, message):
    grp_id = message.chat.id
    title = message.chat.title
    invite_link = await client.export_chat_invite_link(grp_id)
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>No eres administrador en este grupo</b>')
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text(f"<b>Usa este comando en un grupo...\n\nNombre del Grupo: {title}\nID del Grupo: {grp_id}\nEnlace de Invitación: {invite_link}</b>")
    try:
        tutorial = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("<b>Comando incompleto!!\n\nUsa de esta forma -</b>\n\n<code>/set_tutorial_3 https://t.me/Aksbackup</code>")
    await save_group_settings(grp_id, 'tutorial_3', tutorial)
    await message.reply_text(f"<b>Cambio exitoso del tutorial de verificación 3 para {title} a</b>\n\n{tutorial}", disable_web_page_preview=True)

@Client.on_message(filters.command('set_verify'))
async def set_shortner(c, m):
    grp_id = m.chat.id
    chat_type = m.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await m.reply_text("<b>Usa este comando en un grupo...</b>")
    if not await is_check_admin(c, grp_id, m.from_user.id):
        return await m.reply_text('<b>No eres administrador en este grupo</b>')        
    if len(m.text.split()) == 1:
        await m.reply("<b>Usa este comando como sigue - \n\n`/set_shortner tnshort.net 06b24eb6bbb025713cd522fb3f696b6d5de11354`</b>")
        return        
    sts = await m.reply("<b>♻️ Comprobando...</b>")
    await asyncio.sleep(1.2)
    await sts.delete()
    try:
        URL = m.command[1]
        API = m.command[2]
        resp = requests.get(f'https://{URL}/api?api={API}&url=https://telegram.dog/Jisshu_support').json()
        if resp['status'] == 'success':
            SHORT_LINK = resp['shortenedUrl']
        await save_group_settings(grp_id, 'shortner', URL)
        await save_group_settings(grp_id, 'api', API)
        await m.reply_text(f"<b><u>✓ Shortner agregado exitosamente</u>\n\ndemo - {SHORT_LINK}\n\nsitio - `{URL}`\n\napi - `{API}`</b>", quote=True)
        user_id = m.from_user.id
        user_info = f"@{m.from_user.username}" if m.from_user.username else f"{m.from_user.mention}"
        link = (await c.get_chat(m.chat.id)).invite_link
        grp_link = f"[{m.chat.title}]({link})"
        log_message = f"#New_Shortner_Set_For_1st_Verify\n\nName - {user_info}\nId - `{user_id}`\n\nNombre de dominio - {URL}\nApi - `{API}`\nEnlace del grupo - {grp_link}"
        await c.send_message(LOG_API_CHANNEL, log_message, disable_web_page_preview=True)
    except Exception as e:
        await save_group_settings(grp_id, 'shortner', SHORTENER_WEBSITE)
        await save_group_settings(grp_id, 'api', SHORTENER_API)
        await m.reply_text(f"<b><u>💢 ¡Ocurrió un error!</u>\n\nSe agregó automáticamente el shortner predeterminado del propietario del bot\n\nSi deseas cambiarlo, usa el formato correcto o agrega un dominio y api válidos\n\nTambién puedes contactar a nuestro <a href=https://t.me/Jisshu_support>grupo de soporte</a> para resolver este problema...\n\nEjemplo -\n\n`/set_shortner mdiskshortner.link e7beb3c8f756dfa15d0bec495abc65f58c0dfa95`\n\n💔 Error - <code>{e}</code></b>", quote=True)

@Client.on_message(filters.command('set_verify_2'))
async def set_shortner_2(c, m):
    grp_id = m.chat.id
    chat_type = m.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await m.reply_text("<b>Usa este comando en un grupo...</b>")
    if not await is_check_admin(c, grp_id, m.from_user.id):
        return await m.reply_text('<b>No eres administrador en este grupo</b>')
    if len(m.text.split()) == 1:
        await m.reply("<b>Usa este comando como sigue - \n\n`/set_shortner_2 tnshort.net 06b24eb6bbb025713cd522fb3f696b6d5de11354`</b>")
        return
    sts = await m.reply("<b>♻️ Comprobando...</b>")
    await asyncio.sleep(1.2)
    await sts.delete()
    try:
        URL = m.command[1]
        API = m.command[2]
        resp = requests.get(f'https://{URL}/api?api={API}&url=https://telegram.dog/bisal_files').json()
        if resp['status'] == 'success':
            SHORT_LINK = resp['shortenedUrl']
        await save_group_settings(grp_id, 'shortner_two', URL)
        await save_group_settings(grp_id, 'api_two', API)
        await m.reply_text(f"<b><u>✅ Shortner agregado exitosamente</u>\n\ndemo - {SHORT_LINK}\n\nsitio - `{URL}`\n\napi - `{API}`</b>", quote=True)
        user_id = m.from_user.id
        user_info = f"@{m.from_user.username}" if m.from_user.username else f"{m.from_user.mention}"
        link = (await c.get_chat(m.chat.id)).invite_link
        grp_link = f"[{m.chat.title}]({link})"
        log_message = f"#New_Shortner_Set_For_2nd_Verify\n\nName - {user_info}\nId - `{user_id}`\n\nNombre de dominio - {URL}\nApi - `{API}`\nEnlace del grupo - {grp_link}"
        await c.send_message(LOG_API_CHANNEL, log_message, disable_web_page_preview=True)
    except Exception as e:
        await save_group_settings(grp_id, 'shortner_two', SHORTENER_WEBSITE2)
        await save_group_settings(grp_id, 'api_two', SHORTENER_API2)
        await m.reply_text(f"<b><u>💢 ¡Ocurrió un error!</u>\n\nSe agregó automáticamente el shortner predeterminado del propietario del bot\n\nSi deseas cambiarlo, usa el formato correcto o agrega un dominio y api válidos\n\nTambién puedes contactar a nuestro <a href=https://t.me/Jisshu_support>grupo de soporte</a> para resolver este problema...\n\nEjemplo -\n\n`/set_shortner_2 mdiskshortner.link e7beb3c8f756dfa15d0bec495abc65f58c0dfa95`\n\n💔 Error - <code>{e}</code></b>", quote=True)

@Client.on_message(filters.command('set_verify_3'))
async def set_shortner_3(c, m):
    chat_type = m.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await m.reply_text("<b>Usa este comando en tu grupo! No en privado</b>")
    if len(m.text.split()) == 1:
        return await m.reply("<b>Usa este comando como sigue - \n\n`/set_shortner_3 tnshort.net 06b24eb6bbb025713cd522fb3f696b6d5de11354`</b>")
    sts = await m.reply("<b>♻️ Comprobando...</b>")
    await sts.delete()
    userid = m.from_user.id if m.from_user else None
    if not userid:
        return await m.reply(f"<b>⚠️ No eres administrador de este grupo</b>")
    grp_id = m.chat.id
    # Verificar si el usuario es administrador
    if not await is_check_admin(c, grp_id, userid):
        return await m.reply_text('<b>No eres administrador en este grupo</b>')
    if len(m.command) == 1:
        await m.reply_text("<b>Usa este comando para agregar shortner y api\n\nEjemplo - `/set_shortner_3 mdiskshortner.link e7beb3c8f756dfa15d0bec495abc65f58c0dfa95`</b>", quote=True)
        return
    try:
        URL = m.command[1]
        API = m.command[2]
        resp = requests.get(f'https://{URL}/api?api={API}&url=https://telegram.dog/Jisshu_support').json()
        if resp['status'] == 'success':
            SHORT_LINK = resp['shortenedUrl']
        await save_group_settings(grp_id, 'shortner_three', URL)
        await save_group_settings(grp_id, 'api_three', API)
        await m.reply_text(f"<b><u>✅ Shortner agregado exitosamente</u>\n\ndemo - {SHORT_LINK}\n\nsitio - `{URL}`\n\napi - `{API}`</b>", quote=True)
        user_id = m.from_user.id
        if m.from_user.username:
            user_info = f"@{m.from_user.username}"
        else:
            user_info = f"{m.from_user.mention}"
        link = (await c.get_chat(m.chat.id)).invite_link
        grp_link = f"[{m.chat.title}]({link})"
        log_message = f"#New_Shortner_Set_For_3rd_Verify\n\nName - {user_info}\nId - `{user_id}`\n\nNombre de dominio - {URL}\nApi - `{API}`\nEnlace del grupo - {grp_link}"
        await c.send_message(LOG_API_CHANNEL, log_message, disable_web_page_preview=True)
    except Exception as e:
        await save_group_settings(grp_id, 'shortner_three', SHORTENER_WEBSITE3)
        await save_group_settings(grp_id, 'api_three', SHORTENER_API3)
        await m.reply_text(f"<b><u>💢 ¡Ocurrió un error!</u>\n\nSe agregó automáticamente el shortner predeterminado del propietario del bot\n\nSi deseas cambiarlo, usa el formato correcto o agrega un dominio y api válidos\n\nTambién puedes contactar a nuestro <a href=https://t.me/Jisshu_support>grupo de soporte</a> para resolver este problema...\n\nEjemplo -\n\n`/set_shortner_3 mdiskshortner.link e7beb3c8f756dfa15d0bec495abc65f58c0dfa95`\n\n💔 Error - <code>{e}</code></b>", quote=True)

@Client.on_message(filters.command('set_log'))
async def set_log(client, message):
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>No eres administrador en este grupo</b>')
    if len(message.text.split()) == 1:
        await message.reply("<b><u>Formato inválido!!</u>\n\nUsa de esta forma -\n`/log -100xxxxxxxx`</b>")
        return
    sts = await message.reply("<b>♻️ Comprobando...</b>")
    await asyncio.sleep(1.2)
    await sts.delete()
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>Usa este comando en un grupo...</b>")
    try:
        log = int(message.text.split(" ", 1)[1])
    except IndexError:
        return await message.reply_text("<b><u>Formato inválido!!</u>\n\nUsa de esta forma -\n`/log -100xxxxxxxx`</b>")
    except ValueError:
        return await message.reply_text('<b>Asegúrate de que el ID sea un número entero...</b>')
    try:
        t = await client.send_message(chat_id=log, text="<b>Hola, ¿qué tal?</b>")
        await asyncio.sleep(3)
        await t.delete()
    except Exception as e:
        return await message.reply_text(f'<b><u>😐 Asegúrate de que este bot sea administrador en ese canal...</u>\n\n💔 Error - <code>{e}</code></b>')
    await save_group_settings(grp_id, 'log', log)
    await message.reply_text(f"<b>✅ Se ha configurado exitosamente tu canal de logs para {title}\n\nID `{log}`</b>", disable_web_page_preview=True)
    user_id = m.from_user.id
    user_info = f"@{m.from_user.username}" if m.from_user.username else f"{m.from_user.mention}"
    link = (await client.get_chat(message.chat.id)).invite_link
    grp_link = f"[{message.chat.title}]({link})"
    log_message = f"#New_Log_Channel_Set\n\nName - {user_info}\nId - `{user_id}`\n\nID del canal de logs - `{log}`\nEnlace del grupo - {grp_link}"
    await client.send_message(LOG_API_CHANNEL, log_message, disable_web_page_preview=True)  

@Client.on_message(filters.command('details'))
async def all_settings(client, message):
    grp_id = message.chat.id
    title = message.chat.title
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>Usa este comando en un grupo...</b>")
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>No eres administrador en este grupo</b>')
    settings = await get_settings(grp_id)
    text = f"""<b><u>Tus configuraciones para -</u> {title}

<u>✅ 1er shortner de verificación (nombre/api)</u>
Nombre - `{settings["shortner"]}`
Api - `{settings["api"]}`

<u>✅ 2do shortner de verificación (nombre/api)</u>
Nombre - `{settings["shortner_two"]}`
Api - `{settings["api_two"]}`

<u>✅ 3er shortner de verificación (nombre/api)</u>
Nombre - `{settings["shortner_three"]}`
Api - `{settings["api_three"]}`

🧭 Tiempo de 2da verificación - `{settings['verify_time']}`

🧭 Tiempo de 3ra verificación - `{settings['third_verify_time']}`

📝 ID del canal de logs - `{settings['log']}`

🌀 ID del canal fsub - /show_fsub

📍 Enlace del tutorial 1 - {settings['tutorial']}

📍 Enlace del tutorial 2 - {settings['tutorial_2']}

📍 Enlace del tutorial 3 - {settings['tutorial_3']}

🎯 Plantilla IMDb - `{settings['template']}`

📂 Leyenda de archivo - `{settings['caption']}`</b>"""
    btn = [[
        InlineKeyboardButton("Resetear datos", callback_data="reset_grp_data")
    ],[
        InlineKeyboardButton("Cerrar", callback_data="close_data")
    ]]
    reply_markup = InlineKeyboardMarkup(btn)
    dlt = await message.reply_text(text, reply_markup=reply_markup, disable_web_page_preview=True)
    await asyncio.sleep(300)
    await dlt.delete()

@Client.on_message(filters.command('set_time_2'))
async def set_time_2(client, message):
    userid = message.from_user.id if message.from_user else None
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>Usa este comando en un grupo...</b>")       
    if not userid:
        return await message.reply("<b>Eres un administrador anónimo en este grupo...</b>")
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>No eres administrador en este grupo</b>')
    try:
        time = int(message.text.split(" ", 1)[1])
    except:
        return await message.reply_text("Comando incompleto!")   
    await save_group_settings(grp_id, 'verify_time', time)
    await message.reply_text(f"Se ha establecido exitosamente el tiempo de 1era verificación para {title}\n\nTiempo: <code>{time}</code>")

@Client.on_message(filters.command('set_time_3'))
async def set_time_3(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>Eres un administrador anónimo en este grupo...</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>Usa este comando en un grupo...</b>")       
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>No eres administrador en este grupo</b>')
    try:
        time = int(message.text.split(" ", 1)[1])
    except:
        return await message.reply_text("Comando incompleto!")   
    await save_group_settings(grp_id, 'third_verify_time', time)
    await message.reply_text(f"Se ha establecido exitosamente el tiempo de 3ra verificación para {title}\n\nTiempo: <code>{time}</code>")
    
@Client.on_callback_query(filters.regex("mostsearch"))
async def most(client, callback_query):
    def is_alphanumeric(string):
        return bool(re.match('^[a-zA-Z0-9 ]*$', string))
    limit = 20  
    top_messages = await mdb.get_top_messages(limit)
    seen_messages = set()
    truncated_messages = []
    for msg in top_messages:
        msg_lower = msg.lower()
        if msg_lower not in seen_messages and is_alphanumeric(msg):
            seen_messages.add(msg_lower)
            if len(msg) > 35:
                truncated_messages.append(msg[:32] + "...")
            else:
                truncated_messages.append(msg)

    keyboard = [truncated_messages[i:i+2] for i in range(0, len(truncated_messages), 2)]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        one_time_keyboard=True, 
        resize_keyboard=True, 
        placeholder="Búsquedas más realizadas del día"
    )
    await callback_query.message.reply_text("<b>Aquí está la lista de las búsquedas más realizadas 👇</b>", reply_markup=reply_markup)
    await callback_query.answer()


@Client.on_callback_query(filters.regex(r"^trending$"))
async def top(client, query):
    movie_series_names = await movie_series_db.get_movie_series_names(1)
    if not movie_series_names:
        await query.message.reply("No hay nombres de películas o series disponibles para las búsquedas principales.")
        return
    buttons = [movie_series_names[i:i + 2] for i in range(0, len(movie_series_names), 2)]
    spika = ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True
    )
    await query.message.reply("<b>Aquí está la lista principal de tendencias 👇</b>", reply_markup=spika)


@Client.on_message(filters.command("refer"))
async def refer(bot, message):
    btn = [[
        InlineKeyboardButton('enlace de invitación', url=f'https://telegram.me/share/url?url=https://t.me/{bot.me.username}?start=reff_{message.from_user.id}&text=Hello%21%20Experience%20a%20bot%20that%20offers%20a%20vast%20library%20of%20unlimited%20movies%20and%20series.%20%F0%9F%98%83'),
        InlineKeyboardButton(f'⏳ {referdb.get_refer_points(message.from_user.id)}', callback_data='ref_point'),
        InlineKeyboardButton('Cerrar', callback_data='close_data')
    ]]  
    m = await message.reply_sticker("CAACAgQAAxkBAAEkt_Rl_7138tgHJdEsqSNzO5mPWioZDgACGRAAAudLcFGAbsHU3KNJUx4E")      
    await m.delete()
    reply_markup = InlineKeyboardMarkup(btn)
    await message.reply_photo(
        photo=random.choice(REFER_PICS),
        caption=(
            f'👋Hola {message.from_user.mention},\n\n'
            f'Aquí está tu enlace de referido:\n'
            f'https://t.me/{bot.me.username}?start=reff_{message.from_user.id}\n\n'
            f'Comparte este enlace con tus amigos. Cada vez que se unan, obtendrás 10 puntos de referido y, '
            f'después de 100 puntos, recibirás 1 mes de suscripción premium.'
        ),
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.private & filters.command("pm_search_on"))
async def set_pm_search_on(client, message):
    user_id = message.from_user.id
    bot_id = client.me.id
    if user_id not in ADMINS:
        await message.delete()
        return
    await db.update_pm_search_status(bot_id, enable=True)
    await message.reply_text("<b><i>✅️ Búsqueda en PM habilitada, ahora los usuarios pueden buscar películas en PM del bot.</i></b>")


@Client.on_message(filters.private & filters.command("pm_search_off"))
async def set_pm_search_off(client, message):
    user_id = message.from_user.id
    bot_id = client.me.id
    if user_id not in ADMINS:
        await message.delete()
        return
    await db.update_pm_search_status(bot_id, enable=False)
    await message.reply_text("<b><i>❌️ Búsqueda en PM deshabilitada, ahora nadie puede buscar películas en PM del bot.</i></b>")


@Client.on_message(filters.private & filters.command("movie_update_on"))
async def set_send_movie_on(client, message):
    user_id = message.from_user.id
    bot_id = client.me.id
    if user_id not in ADMINS:
        await message.delete()
        return    
    await db.update_send_movie_update_status(bot_id, enable=True)
    await message.reply_text("<b><i>✅️ Envío de actualizaciones de películas habilitado.</i></b>")


@Client.on_message(filters.private & filters.command("movie_update_off"))
async def set_send_movie_update_off(client, message):
    user_id = message.from_user.id
    bot_id = client.me.id
    if user_id not in ADMINS:
        await message.delete()
        return    
    await db.update_send_movie_update_status(bot_id, enable=False)
    await message.reply_text("<b><i>❌️ Envío de actualizaciones de películas deshabilitado.</i></b>")


@Client.on_message(filters.command("verify_id"))
async def generate_verify_id(bot, message):
    if message.from_user.id not in ADMINS:
        await message.reply('Solo el administrador del bot puede usar este comando... 😑')
        return
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("¡Este comando solo funciona en grupos!")
    grpid = message.chat.id   
    if grpid in verification_ids:
        await message.reply_text(f"Ya existe un ID de verificación activo para este grupo: `/verifyoff {verification_ids[grpid]}`")
        return
    verify_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    verification_ids[grpid] = verify_id
    await message.reply_text(f"ID de verificación: `/verifyoff {verify_id}` (Válido para este grupo, de un solo uso)")
    return


@Client.on_message(filters.command("verifyoff"))
async def verifyoff(bot, message):
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("¡Este comando solo funciona en grupos!")
    grpid = message.chat.id
    if not await is_check_admin(bot, grpid, message.from_user.id):  # Se cambió client por bot
        return await message.reply_text('<b>¡No eres administrador en este grupo!</b>')
    try:
        input_id = message.command[1]
    except IndexError:
        return await message.reply_text("Por favor, proporciona el ID de verificación junto con el comando.\nUso: `/verifyoff {id}`")
    if grpid not in verification_ids or verification_ids[grpid] != input_id:
        return await message.reply_text("¡ID de verificación inválido! Por favor, contacta al administrador para obtener el ID correcto.")
    await save_group_settings(grpid, 'is_verify', False)
    del verification_ids[grpid]
    return await message.reply_text("Verificación deshabilitada con éxito.")


@Client.on_message(filters.command("verifyon"))
async def verifyon(bot, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("¡Este comando solo funciona en grupos!")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    if not await is_check_admin(bot, grpid, message.from_user.id):  # Se cambió client por bot
        return await message.reply_text('<b>¡No eres administrador en este grupo!</b>')
    await save_group_settings(grpid, 'is_verify', True)
    return await message.reply_text("Verificación habilitada con éxito.")


@Client.on_message(filters.command("reset_group"))
async def reset_group_command(client, message):
    grp_id = message.chat.id
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>No eres administrador en este grupo</b>')
    sts = await message.reply("<b>♻️ Verificando...</b>")
    await asyncio.sleep(1.2)
    await sts.delete()
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>Usa este comando en un grupo...</b>")
    btn = [[
        InlineKeyboardButton('🚫 Cerrar 🚫', callback_data='close_data')
    ]]
    reply_markup = InlineKeyboardMarkup(btn)
    await save_default_settings(grp_id)
    await message.reply_text("Configuraciones del grupo reiniciadas con éxito...")