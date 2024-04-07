import json, pandas as pd, threading, uuid
from pathlib import Path
from datetime import datetime
from aivalanche_app.paths import dummy_data_path
from aivalanche_app.resources.themes.style import style
from aivalanche_app.data_store.db import db
from PySide6.QtCore import QObject, Signal

class store(QObject):
    on_user_validation = Signal(object)
    on_projects_fetched = Signal(object)
    on_project_created = Signal(object)
    
    def __init__(self, db_type: str = 'local_files', style: style = None,
                 on_query_success: callable = None, on_query_error: callable = None):
        super().__init__()
        
        self.db_type = db_type
        self.style = style

        if self.db_type == 'local_files':
            self.users_path = Path.joinpath(dummy_data_path, 'users.csv')
            self.projects_path = Path.joinpath(dummy_data_path, 'projects.csv')
            self.models_path = Path.joinpath(dummy_data_path, 'models.csv')   
        elif self.db_type == 'local_mysql_db':
            self.db = db()
            self.db.connect_to_db()
        
        # User        
        self.user = None
        
        # Projects
        self.projects = pd.DataFrame()
        self.active_project_id = None
        self.active_project = None
        
        # Models
        self.models = pd.DataFrame()
        self.active_model_id = None
        self.active_model = None
    
        # Extra variables        
        self.model_templates = json.load(open(Path.joinpath(dummy_data_path, 'model_templates.json')))
        self.testbench_templates = json.load(open(Path.joinpath(dummy_data_path, 'testbench_templates.json')))
        self.optimizers = json.load(open(Path.joinpath(dummy_data_path, 'optimizers.json')))
        self.simulators = json.load(open(Path.joinpath(dummy_data_path, 'simulators.json')))
    
    
    def validate_user(self, username: str = None, password: str = None):
        threading.Thread(target = self._validate_user, args = (username, password)).start()
        
    def _validate_user(self, username: str = None, password: str = None):
        success = True
        error = None
        user = None
        
        if username is None:
            success = False
            error = 'username is None!'
        elif password is None:
            success = False
            error = 'password is None!'
        elif self.db_type == 'local_files':
            all_users = pd.read_csv(self.users_path)
            user = all_users[(all_users['username'] == username) & (all_users['password'] == password)]
        elif self.db_type == 'local_mysql_db':
            db_response = self.db.fetch_user_by_username_and_password(username, password)
            if db_response['success']:
                user = db_response['data']
            else:
                success = False
                error = db_response['error']
                
        if success:
            if user.empty:
                success = False
                error = 'No user matches the username and password given! Please contact aivalanche support for further information!'
            elif len(user.index) > 1:
                success = False
                error = 'More than 1 user matches the username and password given! Please contact aivalanche support for further information!'
            else:
                user = user.squeeze()
                self.user = user
                
        self.on_user_validation.emit({'success': success, 'error': error, 'data': user})
    
    
    def fetch_projects(self, username: str = None, password: str = None):
        threading.Thread(target = self._fetch_projects).start()

    
    def _fetch_projects(self):
        success = True
        error = None
        projects = None
        
        if self.user is None:
            success = False
            error = 'User is None!'
        else:
            user_id = self.user['id']
            if self.db_type == 'local_files':
                all_projects = pd.read_csv(self.projects_path)
                projects = all_projects[(all_projects['user_id'] == user_id)]
                projects['created_at'] = pd.to_datetime(projects['created_at'])
                projects['last_modified_at'] = pd.to_datetime(projects['last_modified_at'])
                projects.sort_values(by = 'created_at', ascending = False, inplace = True)
                projects.reset_index(inplace = True)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.fetch_projects_by_user_id(user_id)
                if db_response['success']:
                    projects = db_response['data']
                else:
                    success = False
                    error = db_response['error']
        
        if success:
            self.projects = projects
        
        self.on_projects_fetched.emit({'success': success, 'error': error, 'data': projects})
    
    def create_project(self, title: str = None):
        threading.Thread(target = self._create_project, args = (title,)).start()

    def _create_project(self, title: str = None):
        success = True
        error = None
        data = None
        
        if title is None:
            success = False
            error = 'Title is None!'
        else:
            user_id = self.user['id']
            if self.db_type == 'local_files':
                current_time = datetime.now()
                formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
                all_projects = pd.read_csv(self.projects_path)
                new_project = pd.DataFrame.from_dict([{'id': uuid.uuid4(),
                                                       'user_id': user_id,
                                                       'created_at': formatted_time,
                                                       'last_modified_at': formatted_time,
                                                       'title': title,
                                                       'labels': ''}])
                all_projects = pd.concat((all_projects, new_project))
                all_projects.to_csv(path_or_buf = self.projects_path, index = False)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.create_project_by_user_id(user_id, title)
                if db_response['success']:
                    data = db_response['data']
                else:
                    success = False
                    error = db_response['error']
        
        self.on_project_created.emit({'success': success, 'error': error, 'data': data})
    
    
    def get_models_by_project_id(self, project_id):
        self.models = pd.DataFrame.read_csv(self.models_path)


    def set_active_project(self, id: str = None):
        project_ids = [p.id for p in self.projects]
        if id not in project_ids:
            print(f'Warning: No project with id = {id} exists.')
            self.active_project_id = None
            self.active_project = None
            self.models = []
        else:
            self.active_project_id = id
            self.active_project = list(filter(lambda p: p.id == id, self.projects))[0]
            self.models = self.active_project.models
    
    
    def set_active_model(self, id: str = None):
        model_ids = [m.id for m in self.models]
        if id not in model_ids:
            print(f'Warning: No model with id = {id} exists in project {self.active_project.title}.')
            self.active_model_id = None
            self.active_model = None
        else:
            self.active_model_id = id
            self.active_model = list(filter(lambda m: m.id == id, self.models))[0]
            
        
    def update(self, data):
        for key, values in data.items():
            if key == 'user':
                self.user.update(values)
            