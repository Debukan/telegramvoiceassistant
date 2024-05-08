import logging
import sqlite3
from configs.config import DB_FILE, LOGS, TABLE_NAME, COUNT_LAST_MSG

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=LOGS,
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class DataBase:
    def __init__(self):
        self.conn = self.prepare_db()


    # подготовка базы данных
    def prepare_db(self):
        try:
            conn = sqlite3.connect(DB_FILE, check_same_thread=False)
            logging.info("База готова")
            return conn
        except sqlite3.OperationalError as e:
            logging.error(f"Операционная ошибка: {e}")
            exit(1)
        except sqlite3.DatabaseError as e:
            logging.error(f"Ошибка базы данных: {e}")
            exit(1)
        except sqlite3.Error as e:
            logging.error(f"Общая ошибка SQLite: {e}")
            exit(1)
        except Exception as e:
            logging.error(f"Неизвестная ошибка: {e}")     
            exit(1)


    # функция для отправки запроса
    def execute_query(self, sql_query, data=None):
        logging.info(f"База данных выполнила: {sql_query}")

        cursor = self.conn.cursor()
        if data:
            cursor.execute(sql_query, data)
        else:
            cursor.execute(sql_query)

        self.conn.commit()
        logging.info("База данных успешно выполнила запрос")


    # функция для выполнения любого sql-запроса для получения данных (возвращает значение)
    def execute_selection_query(self, sql_query, data=None):
        logging.info(f"DATABASE: Execute query: {sql_query}")

        cursor = self.conn.cursor()

        if data:
            cursor.execute(sql_query, data)
        else:
            cursor.execute(sql_query)
        rows = cursor.fetchall()
        logging.info(f"DATABASE: Query executed successfully")
        return rows


    # создание таблицы messages
    def create_table(self):
        cursor = self.conn.cursor()
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            username TEXT,
            message TEXT,
            role TEXT,
            total_tokens INTEGER,
            tts_symbols INTEGER,
            stt_blocks INTEGER
        );
        """
        cursor.execute(create_table_query)
        self.conn.commit()
        logging.info("База создана")

    
    # обновление значения в таблице
    def update_data(self, user_id, column, value):
        cursor = self.conn.cursor()
        update_table_query = f"""
        UPDATE users SET {column} = ? WHERE user_id = ?;
        """
        cursor.execute(update_table_query, (value, user_id))
        self.conn.commit()
        logging.info(f"DATABASE: Table updated")


    # вставка значения в таблицу
    def insert_data(self, user_id, subject, value):
        cursor = self.conn.cursor()
        insert_data_query = f"""
        INSERT INTO users ({subject})
        SELECT ?
        WHERE NOT EXISTS (SELECT * FROM users WHERE user_id = ?);
        """
        cursor.execute(insert_data_query, (value, user_id))
        self.conn.commit()
        logging.info(f"DATABASE: Data inserted")


    # добавление сообщение в базу данных
    def add_message(self, user_id, username = "", message = "", role = "", total_tokens = 0, tts_symbols = 0, stt_blocks = 0):
        add_message_query = f"""
        INSERT INTO {TABLE_NAME} (user_id, username, message, role, total_tokens, tts_symbols, stt_blocks)
        SELECT ?, ?, ?, ?, ?, ?, ?
        WHERE NOT EXISTS (SELECT 1 FROM {TABLE_NAME} WHERE user_id = ?);
        """
        self.execute_query(add_message_query, [user_id, username, message, role, total_tokens, tts_symbols, stt_blocks, user_id])
        logging.info(f"DATABASE: User added")


    # проверка есть ли такой столбец в таблице
    def is_value_in_table(self, column_name, value):
        sql_query = f'SELECT EXISTS (SELECT 1 FROM {TABLE_NAME} WHERE {column_name} = ?)'
        rows = self.execute_selection_query(sql_query, [value])
        return len(rows) > 0
    

    # получение словаря с данными пользователя из базы данных
    def get_data_for_user(self, user_id):
        if self.is_value_in_table('user_id', user_id):
            sql_query = f'SELECT *' \
                        f'FROM {TABLE_NAME} WHERE user_id = ? LIMIT 1'
            row = self.execute_selection_query(sql_query, [user_id])[0]
            result = {
                "username": row[2],
                "message": row[3],
                "role": row[4],
                "total_tokens": row[5],
                "tts_symbols": row[6],
                "stt_blocks": row[7],
            }
            logging.info(f"DATABASE: Данные были возвращены")
            return result
        else:
            logging.info(f"DATABASE: Пользователь с id = {user_id} не найден")
            self.add_user(user_id)
            return {
                "username": "",
                "message": "",
                "role": "",
                "total_tokens": 0,
                "tts_symbols": 0,
                "stt_blocks": 0,
            }
        

    # проверка есть ли такой пользователь в базе данных
    def user_exists(self, user_id):
        if not self.is_value_in_table('user_id', user_id):
            logging.info(f"DATABASE: Пользователь с id = {user_id} не найден")
            self.add_user(user_id)
            return True
        return False
    

    # подсчет количество уникальных пользователей
    def count_users(self, user_id):
        cursor = self.conn.cursor()
        sql_query = f"""
        SELECT COUNT(DISTINCT user_id) FROM {TABLE_NAME} WHERE user_id <> ?
        """
        count = self.execute_selection_query(sql_query, [user_id])[0]
        return count[0]
    

    # выбор последних сообщений
    def select_last_messages(self, user_id, last=COUNT_LAST_MSG):
        messages = []
        total_spent_tokens = 0
        cursor = self.conn.cursor()
        sql_query = f"""
        SELECT message, role, total_tokens
        FROM {TABLE_NAME}
        WHERE user_id=?
        ORDER BY id DESC LIMIT ?
        """
        data = self.execute_selection_query(sql_query, [user_id, last])
        if data and data[0]:
            for message in reversed(data):
                messages.append({'text': message[0], 'role': message[1]})
                total_spent_tokens = max(total_spent_tokens, message[2])
        return messages, total_spent_tokens
    

    # подсчет всех потраченных ресурсов пользователя
    def count_spent(self, user_id, limit_type):
        cursor = self.conn.cursor()
        sql_query = f"""
        SELECT SUM({limit_type})
        FROM {TABLE_NAME} 
        WHERE user_id=?
        """
        data = self.execute_selection_query(sql_query, [user_id])
        if data and data[0]:
            logging.info(f"База данных: У user_id={user_id} использовано {data[0]} {limit_type}")
            return data[0][0]
        else:
            return 0
        
    
    # подсчет всех потраченных ресурсов бота
    def count_all_spent(self, limit_type):
        cursor = self.conn.cursor()
        sql_query = f"""
        SELECT SUM({limit_type})
        FROM {TABLE_NAME}
        """
        data = self.execute_selection_query(sql_query, [])
        if data and data[0]:
            logging.info(f"База данных всего использовано {data[0]} {limit_type}")
            return data[0]
        else:
            return 0
    

    
