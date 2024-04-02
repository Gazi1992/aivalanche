import threading, mysql.connector
from PySide6.QtCore import QObject, Signal
import time

class db(QObject):
    query_success = Signal(object)
    query_error = Signal(str)

    def __init__(self, host: str = 'localhost', database: str = 'aivalanche_db', user: str = 'root', password: str = '6364',
                 on_query_success: callable = None, on_query_error: callable = None):
        super().__init__()
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None
        
        if on_query_success is not None:
            self.query_success.connect(on_query_success)
            
        if on_query_error is not None:
            self.query_error.connect(on_query_error)
            
            
    def connect_to_db(self):
        try:
            self.connection = mysql.connector.connect(
                host = self.host,
                database = self.database,
                user = self.user,
                password = self.password
            )
            if self.connection.is_connected():
                print('Connected to the MySQL database')
                self.cursor = self.connection.cursor()
        except mysql.connector.Error as e:
            print(f'Error connecting to the MySQL database: {e}')
            

    def close(self):
        try:
            self.cursor.close()
            self.connection.close()
        except mysql.connector.Error as e:
            print(f'Error closing he connection: {e}')
        
    def execute_query(self, query):
        threading.Thread(target=self._execute_query, args=(query,)).start()
        # self._execute_query(query)
        
    def _execute_query(self, query):
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()  # Get the result of the query
            self.connection.commit()
            time.sleep(3)
            self.query_success.emit(result)  # Emit query_success signal with the result
        except mysql.connector.Error as e:
            self.query_error.emit(str(e)) # Emit query_error signal with error message

    def retrieve_data(self, table):
        query = f"SELECT * FROM {table}"
        self.execute_query(query)

    def insert_data(self, table, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.execute_query(query)

        



