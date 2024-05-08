
IAM_TOKEN = "t1.9euelZrIzJmamJCPiZuenoyOjpbPyu3rnpWamZ6RnZGVyJfPnZbIxs7IjMnl8_cvIRJO-e8NRUNL_d3z929PD0757w1FQ0v9zef1656VmpHOx5bMnZSayJiXmcyLkZCe7_zF656VmpHOx5bMnZSayJiXmcyLkZCeveuelZqXzsbMmZydk8bMi46QncyKzLXehpzRnJCSj4qLmtGLmdKckJKPioua0pKai56bnoue0oye.-RiZe8UMM54c0RvZxnRqyL1cj0NNa8-aQxGCUJoWvbbzur_AB5a8lV0Y5YhosVHemCMYRIl8LGM_pS5wycazBQ"

FOLDER_ID = "b1ggl5ujmq7hn5b0to43"

TOKEN = "6671793616:AAEwJwYW5dg6hEpBTPXsdWrajg3yZJ6sJHc"


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


