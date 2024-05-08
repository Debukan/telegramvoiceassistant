
IAM_TOKEN = ""

FOLDER_ID = ""

TOKEN = ""


ABOUT = "Я умный голосовой помощник. Проси все что хочешь. Я понимаю только аудио и текст."

MAX_USERS = 3
MAX_GPT_TOKENS = 500
COUNT_LAST_MSG = 4

MAX_USER_STT_BLOCKS = 5
MAX_USER_TTS_SYMBOLS = 120
MAX_USER_GPT_TOKENS = 120

LOGS = 'log_file.log'
DB_FILE = 'data.db'
TABLE_NAME = 'messages'

TEMPERATURE = 0.7

SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты веселый собеседник. Поддерживай диалог.'}]

COMMANDS = {
    '/start': 'Запустить бота',
    '/help': 'Отобразить справку',
    '/about': 'Расскажу о себе',
    '/tts': 'Озвучу твой текст',
    '/stt': 'Найду текст в твоем аудио',
}

HEADERS = {
    'Authorization': f'Bearer {IAM_TOKEN}',
    'Content-Type': 'application/json'
}

URL = f'gpt://{FOLDER_ID}/yandexgpt-lite'

YAURL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"


