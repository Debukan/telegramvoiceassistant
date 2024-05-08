import logging
import requests
from configs.config import FOLDER_ID, IAM_TOKEN, LOGS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=LOGS,
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class TTS:

    def count_symbols(self, text):
        return len(text)


    def process_resp(self, response) -> [bool, str]:        
        try:
            if response.status_code < 200 or response.status_code >= 300:
                logging.info("Произошла ошибка при запросе")
                return False, response.json()['error_message']
        except:
            logging.error(f"Код статуса {response.status_code}")
            return False, "Ошибка получения статуса кода"

        try:
            logging.info(response)
            if "error_code" in response or "error_message" in response:
                return False, response.json()['error_message']
        except:
            return False, "Ошибка получения ответа"
        
        return True, response.content
    

    def make_json(self, text):
        json = {
            "text": text,
            "lang": "ru-RU",
            "voice": "filipp",
            "folderId": FOLDER_ID
        }
        logging.info("Создан json для текста")
        token = self.count_symbols(text)
        return json, token
    

    def send_request(self, data):
        url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
        headers = {
            'Authorization': f'Bearer {IAM_TOKEN}'
        }
        response = requests.post(url, headers=headers, data=data)
        logging.info("Запрос отправлен")
        return response