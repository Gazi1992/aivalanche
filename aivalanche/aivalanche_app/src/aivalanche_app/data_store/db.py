import mysql.connector, time, pandas as pd
from PySide6.QtCore import QObject

class db(QObject):
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

    def execute_query(self, query, description):
        try:
            self.cursor.execute(query)
            if 'insert' in query or 'update' in query:
                self.connection.commit()
                data = None
            else:
                columns = [column[0] for column in self.cursor.description]  # Get column names
                result = self.cursor.fetchall()  # Get the result of the query
                data = pd.DataFrame(data = result, columns = columns)
            # time.sleep(3)
            success = True
            error = None
        except mysql.connector.Error as e:
            success = False
            data = None
            error = str(e)
        return {'success': success,
                'description': description,
                'data': data,
                'error': error}

    def fetch_users(self):
        query = "select * from users"
        return self.execute_query(query, 'fetch_users')
    
    def fetch_user_by_username_and_password(self, username: str = '', password: str = ''):
        query = f"select * from aivalanche_db.users where username = '{username}' and password = '{password}'"
        return self.execute_query(query, 'fetch_user_by_username_and_password') 
        
    def fetch_projects_by_user_id(self, user_id: str = ''):
        query = f"select * from aivalanche_db.projects where user_id = '{user_id}' order by created_at desc"
        return self.execute_query(query, 'fetch_projects_by_user_id')
        
    def fetch_models_by_user_id_and_project_id(self, user_id, project_id):
        query = f"select * from aivalanche_db.models where user_id = '{user_id}' and project_id = '{project_id}'"
        return self.execute_query(query, 'fetch_models_by_user_id_and_project_id')

    def create_project_by_user_id(self, user_id: str = None, title: str = None):
        query = f"insert into projects (user_id, created_at, last_modified_at, title, labels) values ('{user_id}', now(), now(), '{title}', '')"
        return self.execute_query(query, 'create_project_by_user_id')

        



