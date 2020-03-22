import sqlite3 as sq

connection = None


class Sql:
    def __init__(self):
        self.connection = sq.connect("data.db")
        self.cursor = self.connection.cursor()

    def init_db(self, clear: bool=False):
        """ Проверить что нужные таблицы существуют , иначе создать
            их
            Для удаление и создание заного
            флаг clear должен принять значение True
        """
        if clear:
            self.cursor.execute('DROP TABLE IF EXISTS user_req')
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS user_req (
                            f_id int, name text, class text, numb int)
                        """)
        self.connection.commit()

sql = Sql()


def addName(f_id: int, name: str):
    if nameChecker(f_id):
        sql.cursor.execute(f"INSERT INTO user_req (f_id, name) VALUES ({f_id}, '{name}')")
        print((f_id, name))
    else:
        sql.cursor.execute(f"UPDATE user_req SET name = '{name}' WHERE f_id = {f_id}")
    sql.connection.commit()


def nameChecker(f_id: int):
    """f_id check in Data base"""
    sql.cursor.execute(f"SELECT * FROM user_req WHERE f_id={f_id}")
    if sql.cursor.fetchone() is None:
        return True
    else:
        return False
