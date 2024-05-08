import logging
from configs.config import LOGS, MAX_USERS, MAX_USER_GPT_TOKENS, MAX_GPT_TOKENS, MAX_USER_STT_BLOCKS, MAX_USER_TTS_SYMBOLS
from db import DataBase

db = DataBase()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=LOGS,
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# функция проверки на пользователей
def check_number_of_users(user_id):
    count = db.count_users(user_id)
    if count > MAX_USERS:
        return False, "Превышено максимальное количество пользователей"
    return True, ""


# функция на проверку лимита токенов у пользователя
def is_gpt_token_limit(user_id):
    tokens = db.count_spent(user_id, "total_tokens")
    if tokens >= MAX_USER_GPT_TOKENS:
        return False, "Превышен лимит токенов у пользователя"
    return True, ""


# функция проверки всех использованных токенов бота
def check_all_token_usage():
    amount = db.count_all_spent('total_tokens')
    if amount >= MAX_GPT_TOKENS:
        return False, "Превышен лимит токенов бота"
    return True, ""


# проверяем, не превысил ли пользователь лимиты на преобразование аудио в текст
def is_stt_block_limit(user_id, duration):
    if duration >= MAX_USER_STT_BLOCKS:
        return False, "Превышен лимит блоков бота"
    return True, ""


# проверяем, не превысил ли пользователь лимиты на преобразование текста в аудио
def is_tts_symbol_limit(user_id, text):
    amount = db.count_spent(user_id, 'tts_symbols')
    if amount >= MAX_USER_TTS_SYMBOLS:
        return False, "Превышен лимит символов для преобразование в аудио"
    return True, ""