import logging
import requests
from configs.config import URL, FOLDER_ID, HEADERS, SYSTEM_PROMPT, TEMPERATURE, MAX_USER_GPT_TOKENS, IAM_TOKEN, LOGS, YAURL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=LOGS,
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S"
)
class GPT:
    def __init__(self):
        self.url = URL

    
    def count_tokens(self, prompt):
        data = {
            "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
            "text": prompt
        }
        print(requests.post(
                "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize",
                json=data,
                headers=HEADERS
            ).json())
        return len(
            requests.post(
                "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize",
                json=data,
                headers=HEADERS
            ).json()['tokens']
        )
    

    def process_resp(self, response) -> [bool, str]:
    # Проверка статус кода
        try:            
            if response.status_code < 200 or response.status_code >= 300:
                if response.status_code == 204:
                    logging.warning("Статус: 204 No Content")
                logging.error(response.text)
                return False, f"Ошибка: {response.status_code}"
        except:
            return False, "Ошибка получения статус кода"

        # Проверка json
        try:
            full_response = response.json()
        except:
            return False, "Ошибка получения JSON"

        # Проверка сообщения об ошибке
        try:
            if "error" in full_response or "result" not in full_response or "alternatives" not in full_response['result']:
                logging.error(full_response)
                return False, f"Ошибка: {full_response}"
        except:
            return False, "Ошибка получения JSON"
        
        try:
            result = full_response["result"]["alternatives"][0]["message"]["text"]
        except:
            return False, "Ошибка получения результата"
        
        if "error" in result.lower():
            return False, result["error"]

        # Пустой результат == объяснение закончено
        if result is None or result == "":
            logging.info("Закончено")
            return True, "Объяснение закончено"

        # Сохраняем сообщение в историю
        return True, result
        

    def make_prompt(self, data, used_tokens=0):
        json = {
            "modelUri": URL,
            "completionOptions": {
                "stream": False,
                "temperature": TEMPERATURE,
                "maxTokens": MAX_USER_GPT_TOKENS - used_tokens,
            },
            "messages": SYSTEM_PROMPT + data
        }
        logging.info("Промпт создан")
        if len(json['messages']) == 3:
            tokens = self.count_tokens(json['messages'][0]['text'] + json['messages'][1]['text'] + json['messages'][2]['text'])
        else:
            tokens = self.count_tokens(json['messages'][0]['text'] + json['messages'][1]['text'])
        return json, tokens
    

    def send_request(self, json):
        response = requests.post(YAURL, headers=HEADERS, json=json)
        logging.info("Запрос отправлен")
        return response
    