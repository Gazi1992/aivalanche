import threading, mysql.connector, time, pandas as pd
from PySide6.QtCore import QObject, Signal

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
        
    def execute_query(self, query, description = ''):
        threading.Thread(target=self._execute_query, args=(query, description)).start()
        # self._execute_query(query)
        
    def _execute_query(self, query, description):
        try:
            self.cursor.execute(query)
            columns = [column[0] for column in self.cursor.description]  # Get column names
            result = self.cursor.fetchall()  # Get the result of the query
            if description in ['insert_data']:
                self.connection.commit()
            time.sleep(3)
            self.query_success.emit({'description': description,
                                     'result': pd.DataFrame(data = result, columns = columns)})  # Emit query_success signal with the result
        except mysql.connector.Error as e:
            self.query_error.emit({'description': description,
                                   'error': str(e)}) # Emit query_error signal with error message

    def get_users(self):
        query = "select * from users"
        self.execute_query(query, 'get_users')
        
    def get_projects_by_user(self, user_id):
        query = f"select * from aivalanche_db.projects where 'user_id' = '{user_id}'"
        self.execute_query(query, 'get_projects_by_user')
        
    def get_models_by_user_and_project(self, user_id, project_id):
        query = f"select * from aivalanche_db.models where 'user_id' = '{user_id}' and 'project_id' = '{project_id}'"
        self.execute_query(query, 'get_models_by_user_and_project')

    def create_project(self, user_id, name):
        query = f"insert into projects (user_id, name) values ({user_id}, {name})"
        self.execute_query(query, 'create_project')

        



