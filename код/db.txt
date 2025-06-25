import sqlite3
from pathlib import Path

class Database:
    def __init__(self, db_path='company.db'):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Создает таблицы в базе данных"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            coefficient REAL NOT NULL
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL,
            price REAL NOT NULL,
            unit TEXT NOT NULL
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            type_id INTEGER NOT NULL,
            min_price REAL NOT NULL,
            width REAL NOT NULL,
            FOREIGN KEY (type_id) REFERENCES product_types(id)
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_materials (
            product_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            PRIMARY KEY (product_id, material_id),
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (material_id) REFERENCES materials(id)
        )""")
        
        self.conn.commit()

    def execute(self, query, params=()):
        """Выполняет SQL-запрос"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor

    def fetch_all(self, query, params=()):
        """Возвращает все строки результата"""
        cursor = self.execute(query, params)
        return cursor.fetchall()

    def fetch_one(self, query, params=()):
        """Возвращает одну строку результата"""
        cursor = self.execute(query, params)
        return cursor.fetchone()

    def close(self):
        """Закрывает соединение с базой"""
        self.conn.close()