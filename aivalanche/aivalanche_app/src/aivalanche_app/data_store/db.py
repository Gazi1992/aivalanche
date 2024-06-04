import mysql.connector, time, pandas as pd, uuid
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

    def execute_query(self, query, description, return_data = {}):
        try:
            self.cursor.execute(query)
            if 'insert' in query or 'update' in query:
                self.connection.commit()
                data = return_data
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

    #%% Optimizers
    def fetch_optimizers(self):
        query = "select * from aivalanche_db.optimizers"
        return self.execute_query(query, 'fetch_optimizers')
    
    #%% Simulators
    def fetch_simulators(self):
        query = "select * from aivalanche_db.simulators"
        return self.execute_query(query, 'fetch_simulators')

    #%% User
    def fetch_users(self):
        query = "select * from aivalanche_db.users"
        return self.execute_query(query, 'fetch_users')
    
    def fetch_user_by_username_and_password(self, username: str = '', password: str = ''):
        query = f"select * from aivalanche_db.users where username = '{username}' and password = '{password}'"
        return self.execute_query(query, 'fetch_user_by_username_and_password') 
    
    #%% Projects
    def fetch_projects_by_user_id(self, user_id: str = None):
        if user_id is not None:
            query = f"select * from aivalanche_db.projects where user_id = '{user_id}' order by created_at desc"
            return self.execute_query(query, 'fetch_projects_by_user_id')
        
    def create_project_by_user_id(self, user_id: str = None, title: str = None):
        if user_id is not None and title is not None:
            query = f"insert into aivalanche_db.projects (user_id, created_at, last_modified_at, title, labels) values ('{user_id}', now(), now(), '{title}', '')"
            return self.execute_query(query, 'create_project_by_user_id')
    
    def update_project_path_by_id(self, project_id: str = None, path: str = None):
        if id is not None and path is not None:
            query = f"update aivalanche_db.projects set path = '{path}' where id = '{project_id}'"
            return self.execute_query(query, 'update_project_path_by_id')
    
    #%% Models
    def fetch_all_models(self):
        query = "select * from aivalanche_db.models"
        return self.execute_query(query, 'fetch_all_models')
    
    def fetch_models_by_project_id(self, project_id):
        query = f"select * from aivalanche_db.models where project_id = '{project_id}' order by created_at desc"
        return self.execute_query(query, 'fetch_models_by_project_id')

    def create_model_by_project_id(self, project_id: str = None, title: str = None):
       query = f"insert into aivalanche_db.models (project_id, created_at, last_modified_at, title, labels, status) values ('{project_id}', now(), now(), '{title}', '', 'setup')"
       return self.execute_query(query, 'create_model_by_project_id')

    def fetch_model_templates(self):
        query = "select * from aivalanche_db.model_templates"
        return self.execute_query(query, 'fetch_model_templates')

    #%% Reference data files
    def fetch_reference_data_by_project_id(self, project_id: str = None):
        query = f"select * from aivalanche_db.reference_data_files where project_id = '{project_id}' order by path desc"
        return self.execute_query(query, 'fetch_reference_data_by_project_id')

    def add_reference_data_by_project_id(self, path: str = None, project_id: str = None):
        id = str(uuid.uuid4())
        query = f"insert into aivalanche_db.reference_data_files (id, path, project_id) values ('{id}', '{path}', '{project_id}')"
        return_data = {'id': id, 'path': path, 'project_id': project_id}
        return self.execute_query(query, 'add_reference_data_by_project_id', return_data)
    
    def update_reference_data_id_by_model_id(self, reference_data_id: str = None, model_id: str = None):
        if reference_data_id is None:
            query = f"update aivalanche_db.models set reference_data_id = NULL where id = '{model_id}'"
        else:
            query = f"update aivalanche_db.models set reference_data_id = '{reference_data_id}' where id = '{model_id}'"
        return self.execute_query(query, 'update_reference_data_id_by_model_id')
    
    def fetch_reference_data_by_path_and_project_id(self, path: str = None, project_id: str = None):
        query = f"select * from aivalanche_db.reference_data_files where project_id = '{project_id}' and path = '{path}' order by path desc"
        return self.execute_query(query, 'fetch_reference_data_by_path_and_project_id')
    
    #%% Parameters files
    def fetch_parameters_by_project_id(self, project_id: str = None):
        query = f"select * from aivalanche_db.parameters_files where project_id = '{project_id}' order by path desc"
        return self.execute_query(query, 'fetch_parameters_by_project_id')

    def add_parameters_by_project_id(self, path: str = None, project_id: str = None):
        id = str(uuid.uuid4())
        query = f"insert into aivalanche_db.parameters_files (id, path, project_id) values ('{id}', '{path}', '{project_id}')"
        return_data = {'id': id, 'path': path, 'project_id': project_id}
        return self.execute_query(query, 'add_parameters_by_project_id', return_data)
    
    def update_parameters_id_by_model_id(self, parameters_id: str = None, model_id: str = None):
        if parameters_id is None:
            query = f"update aivalanche_db.models set parameters_id = NULL where id = '{model_id}'"
        else:
            query = f"update aivalanche_db.models set parameters_id = '{parameters_id}' where id = '{model_id}'"
        return self.execute_query(query, 'update_parameters_id_by_model_id')
    
    def fetch_parameters_by_path_and_project_id(self, path: str = None, project_id: str = None):
        query = f"select * from aivalanche_db.parameters_files where project_id = '{project_id}' and path = '{path}' order by path desc"
        return self.execute_query(query, 'fetch_parameters_by_path_and_project_id')