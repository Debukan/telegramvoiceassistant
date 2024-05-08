import telebot
import logging
from configs.config import LOGS, COMMANDS, ABOUT, COUNT_LAST_MSG, TOKEN
from models.gpt import GPT
from db import DataBase
from validators import *
from audio_processing.stt import STT
from audio_processing.tts import TTS

gpt = GPT()
db = DataBase()

stt = STT()
tts = TTS()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=LOGS,
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S",
)


bot = telebot.TeleBot(TOKEN)

logging.info("Бот начал работу")


# команды бота
bot.set_my_commands([
    telebot.types.BotCommand("/start", "Запустить бота"),
    telebot.types.BotCommand("/help", "Отобразить справку"),
    telebot.types.BotCommand("/about", "Расскажу о себе"),
    telebot.types.BotCommand("/tts", "Озвучу твой текст"),
    telebot.types.BotCommand("/stt", "Найду текст в твоем аудио")
])

# подготовка базы данных
db.create_table()

print("Бот подготовлен")


# обработка команды start
@bot.message_handler(commands=["start"])
def start_handler(message):
    bot.send_message(message.chat.id, "Привет! Диалог уже начался!")
    bot.send_message(message.chat.id, "Напиши /help для помощи!")


# обработка команды help
@bot.message_handler(commands=["help"])
def help_handler(message):
    text = "Вот список команд, которые я могу выполнить:\n"
    for command, description in COMMANDS.items():
        text += f"{command} - {description}\n"
    bot.send_message(message.chat.id, text)


# обработка команды about
@bot.message_handler(commands=["about"])
def about_handler(message):
    bot.send_message(message.chat.id, ABOUT)


# отправка файла с логами
@bot.message_handler(commands=["debug"])
def debug_handler(message):
    with open(LOGS, "rb") as f:
        bot.send_document(message.chat.id, f)


# обработка текстовых сообщений
@bot.message_handler(content_types=["text"])
def text_handler(message):
    user_id = message.chat.id
    status, error_message = check_number_of_users(user_id)
    if not status:
        bot.send_message(user_id, error_message)
        return

    db.add_message(user_id, message.from_user.first_name, message.text, "user", 0, 0, 0)
    last_messages, total_tokens = db.select_last_messages(user_id, COUNT_LAST_MSG)
    status, error_message = is_gpt_token_limit(user_id)
    if not status:
        bot.send_message(user_id, error_message)
        return

    json, tokens_in_prompt = gpt.make_prompt(last_messages, total_tokens)
    full_response = gpt.send_request(json)
    response = gpt.process_resp(full_response)
    if not response[0]:
        bot.send_message(user_id, response[1])
        return
    tokens_in_answer = gpt.count_tokens(response[1])
    total_tokens += tokens_in_prompt + tokens_in_answer
    db.add_message(
        user_id,
        message.from_user.first_name,
        response[1],
        "assistant",
        total_tokens,
        0,
        0,
    )
    bot.send_message(user_id, response[1])


# обработка голосовых сообщений
@bot.message_handler(content_types=["voice"])
def voice_handler(message):
    user_id = message.chat.id
    status, error_message = check_number_of_users(user_id)
    if not status:
        bot.send_message(user_id, error_message)
        return

    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    status, error_message = is_stt_block_limit(user_id, message.voice.duration)
    if not status:
        bot.send_message(user_id, error_message)
        return

    blocks = stt.count_blocks(message.voice.duration)
    full_response = stt.send_request(downloaded_file)
    response = stt.process_resp(full_response)
    if not response[0]:
        bot.send_message(user_id, response[1])
        return
    db.add_message(user_id, message.from_user.first_name, response[1], "user", 0, 0, 0)
    last_messages, total_spent_tokens = db.select_last_messages(user_id, COUNT_LAST_MSG)
    status, error_message = is_gpt_token_limit(user_id)
    if not status:
        bot.send_message(user_id, error_message)
        return

    json, tokens_in_prompt = gpt.make_prompt(last_messages, total_spent_tokens)
    full_response = gpt.send_request(json)
    response = gpt.process_resp(full_response)
    if not response[0]:
        bot.send_message(user_id, response[1])
        return
    tokens_in_answer = gpt.count_tokens(response[1])
    total_spent_tokens += tokens_in_prompt + tokens_in_answer

    gpt_answer = response[1]

    json, symbols = tts.make_json(response[1])
    full_response = tts.send_request(json)
    response = tts.process_resp(full_response)
    if not response[0]:
        bot.send_message(user_id, response[1])
        return
    db.add_message(
        user_id,
        message.from_user.first_name,
        gpt_answer,
        "assistant",
        total_spent_tokens,
        symbols,
        blocks,
    )
    with open("output.ogg", "wb") as audio_file:
        audio_file.write(response[1])
    with open("output.ogg", "rb") as audio_file:
        bot.send_voice(user_id, audio_file)



# обработка команды tts
@bot.message_handler(commands=["tts"])
def tts_handler(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'Отправь следующим сообщением текст, чтобы я его озвучил!')
    bot.register_next_step_handler(message, tts)


# обработка текста для озвучки
def tts_func(message):
    user_id = message.chat.id
    json, token1 = tts.make_json(message.text)

    full_response = tts.send_request(json)
    response = tts.process_resp(full_response)
    if not response[0]:
        bot.send_message(message.chat.id, response[1])
        logging.error(response[1])
    else:
        with open("output.ogg", "wb") as audio_file:
            audio_file.write(response[1])
        with open("output.ogg", "rb") as audio_file:
            bot.send_voice(message.chat.id, audio_file)
        logging.info("Бот закончил синтез")


# обработка команды stt
@bot.message_handler(commands=['stt'])
def stt_handler(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'Отправь следующим сообщением аудио, чтобы я его распознал!')
    bot.register_next_step_handler(message, stt_func)


# функция аудио для распознавания
def stt_func(message):
    user_id = message.chat.id
    blocks = db.get_blocks_usage()
    if not message.voice:
        bot.send_message(message.chat.id, "Отправьте аудио сообщением!")
        bot.register_next_step_handler(message, stt_func)
        return
    status, error_message = is_stt_block_limit(stt.count_blocks(message.voice.duration))
    if not status:
        bot.send_message(user_id, error_message)
        return
    else:
        file_id = message.voice.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)
        full_response = stt.send_request(file)
        response = stt.process_resp(response=full_response)
        if not response[0]:
            bot.send_message(message.chat.id, response[1])
            logging.error(response[1])
        else:
            bot.send_message(message.chat.id, response[1], reply_to_message_id=message.message_id)
            logging.info("Бот закончил распознавание")

bot.infinity_polling()
