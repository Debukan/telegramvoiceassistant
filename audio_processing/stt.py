import logging
import requests
from math import ceil
from configs.config import FOLDER_ID, IAM_TOKEN, LOGS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=LOGS,
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class STT:
    
    def count_blocks(self, durations):
        return ceil(durations / 15)
    

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
        
        try:
            result = response.json()['result']
        except:
            return False, "Ошибка получения результата"

        return True, result
    

    def send_request(self, data):
        params = "&".join([
            "topic=general",
            f"folderId={FOLDER_ID}"
        ])
        url = f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}"
        headers = {
            "Authorization": f"BEARER {IAM_TOKEN}"
        }
        response = requests.post(url, headers=headers, data=data)
        logging.info("Запрос отправлен")
        return response