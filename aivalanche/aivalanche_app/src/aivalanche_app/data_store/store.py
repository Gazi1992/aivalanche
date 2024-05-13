import json, pandas as pd, threading, uuid
from pathlib import Path
from datetime import datetime
from aivalanche_app.paths import dummy_data_path
from aivalanche_app.resources.themes.style import style
from aivalanche_app.data_store.db import db
from PySide6.QtCore import QObject, Signal

class store(QObject):
    validate_user_start = Signal(object)
    validate_user_end = Signal(object)

    active_project_changed = Signal(object)
    fetch_projects_start = Signal(object)
    fetch_projects_end = Signal(object)
    create_project_start = Signal(object)
    create_project_end = Signal(object)
    fetch_available_reference_data_start = Signal(object)
    fetch_available_reference_data_end = Signal(object)
    add_available_reference_data_start = Signal(object)
    add_available_reference_data_end = Signal(object)
    
    active_model_changed = Signal(object)
    fetch_models_start = Signal(object)
    fetch_models_end = Signal(object)
    create_model_start = Signal(object)
    create_model_end = Signal(object)
    fetch_model_templates_start = Signal()
    fetch_model_templates_end = Signal(object)
    update_reference_data_id_start = Signal(object)
    update_reference_data_id_end = Signal(object)
    
    def __init__(self, db_type: str = 'local_files', style: style = None,
                 on_query_success: callable = None, on_query_error: callable = None):
        super().__init__()
        
        self.db_type = db_type
        self.style = style

        if self.db_type == 'local_files':
            self.users_path = Path.joinpath(dummy_data_path, 'users.csv')
            self.projects_path = Path.joinpath(dummy_data_path, 'projects.csv')
            self.models_path = Path.joinpath(dummy_data_path, 'models.csv')
            self.available_reference_data_path = Path.joinpath(dummy_data_path, 'reference_data_files.csv')
            self.available_parameters_path = Path.joinpath(dummy_data_path, 'parameters_files.csv')
            self.available_loss_function_path = Path.joinpath(dummy_data_path, 'loss_function_files.csv')
        elif self.db_type == 'local_mysql_db':
            self.db = db()
            self.db.connect_to_db()
        
        # User        
        self.user = None
        
        # Projects
        self.projects = pd.DataFrame()
        self.active_project = None
        
        # Models
        self.models = pd.DataFrame()
        self.active_model = None
    
        # Extra variables        
        self.model_templates = pd.DataFrame()
        self.optimizers = json.load(open(Path.joinpath(dummy_data_path, 'optimizers.json')))
        self.simulators = json.load(open(Path.joinpath(dummy_data_path, 'simulators.json')))
        
        self.available_reference_data = pd.DataFrame()
        self.available_parameters = pd.DataFrame()
        self.available_loss_functions = pd.DataFrame()

        
    #%% Users
    def validate_user(self, username: str = None, password: str = None):
        threading.Thread(target = self._validate_user, args = (username, password)).start()
        
    def _validate_user(self, username: str = None, password: str = None):
        self.validate_user_start.emit({'username': username, 'password': password})
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
                
        self.validate_user_end.emit({'success': success, 'error': error, 'data': user})
    
    
    #%% Projects
    def set_active_project(self, p: pd.Series = None):
        if self.active_project is None or p is None or self.active_project['id'] != p['id']:
            self.active_project = p
            if p is not None:
                self.fetch_available_reference_data(project_id = self.active_project['id'])
            self.active_project_changed.emit({'active_project': p})
    
    def fetch_projects(self):
        threading.Thread(target = self._fetch_projects).start()

    def _fetch_projects(self):
        self.fetch_projects_start.emit({'user': self.user})
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
                projects.loc[:,'created_at'] = pd.to_datetime(projects['created_at'])
                projects.loc[:,'last_modified_at'] = pd.to_datetime(projects['last_modified_at'])
                projects.sort_values(by = 'created_at', ascending = False, inplace = True, ignore_index = True)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.fetch_projects_by_user_id(user_id)
                if db_response['success']:
                    projects = db_response['data']
                else:
                    success = False
                    error = db_response['error']
        
        if success:
            self.projects = projects
        
        self.fetch_projects_end.emit({'success': success, 'error': error, 'data': projects})
    
    def create_project(self, title: str = None):
        threading.Thread(target = self._create_project, args = (title,)).start()

    def _create_project(self, title: str = None):
        self.create_project_start.emit({'title': title})
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
                if title in all_projects['title'].tolist():
                    success = False
                    error = f'You already have a project called {title}. Please specify a different title.'
                else:
                    new_project = pd.DataFrame.from_dict([{'id': str(uuid.uuid4()),
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
        
        self.create_project_end.emit({'success': success, 'error': error, 'data': data})
        
    def fetch_available_reference_data(self, project_id: str = None):
        threading.Thread(target = self._fetch_available_reference_data, args = (project_id,)).start()
        # self._fetch_available_reference_data(project_id)
        
    def _fetch_available_reference_data(self, project_id: str = None):
        self.fetch_available_reference_data_start.emit({'project_id': project_id})
        success = True
        error = None
        available_reference_data = None
        
        if project_id is None:
            success = False
            error = 'project_id is None!'
        else:
            if self.db_type == 'local_files':
                all_reference_data = pd.read_csv(self.available_reference_data_path)
                available_reference_data = all_reference_data[(all_reference_data['project_id'] == project_id)]
                available_reference_data.sort_values(by = 'path', ascending = False, inplace = True)
                available_reference_data.reset_index(inplace = True)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.fetch_reference_data_by_project_id(project_id)
                if db_response['success']:
                    available_reference_data = db_response['data']
                else:
                    success = False
                    error = db_response['error']
        
        if success:
            self.available_reference_data = available_reference_data
        
        self.fetch_available_reference_data_end.emit({'success': success, 'error': error, 'data': available_reference_data})
    
    def add_available_reference_data(self, path: str = None, project_id: str = None):
        # threading.Thread(target = self._add_available_reference_data, args = (path, project_id)).start()
        self._add_available_reference_data(path, project_id)
        
    def _add_available_reference_data(self, path: str = None, project_id: str = None):
        self.add_available_reference_data_start.emit({'path': path, 'project_id': project_id})
        success = True
        error = None
        data = None
        
        if path is None:
            success = False
            error = 'path is None!'
        elif project_id is None:
            success = False
            error = 'project_id is None!'
        else:
            if self.db_type == 'local_files':
                all_reference_data = pd.read_csv(self.available_reference_data_path)
                if path in all_reference_data[all_reference_data['project_id'] == project_id]['path'].tolist():
                    success = False
                    error = f'You already have a reference data file with the path {path} for the project {project_id}. Please specify a different file.'
                else:
                    new_reference_data_file = pd.DataFrame.from_dict([{'id': str(uuid.uuid4()),
                                                                       'path': path,
                                                                       'project_id': project_id}])
                    all_reference_data = pd.concat((all_reference_data, new_reference_data_file))
                    all_reference_data.to_csv(path_or_buf = self.available_reference_data_path, index = False)
                    data = new_reference_data_file.squeeze()
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.add_reference_data_by_project_id(path, project_id)
                if db_response['success']:
                    data = db_response['data']
                else:
                    success = False
                    error = db_response['error']
        
        self.add_available_reference_data_end.emit({'success': success, 'error': error, 'data': data})
        
        
    #%% Models
    def set_active_model(self, m: pd.Series = None, override: bool = False):
        if self.active_model is None or m is None or self.active_model['id'] != m['id'] or override:
            self.active_model = m
            if not override:
                self.active_model_changed.emit({'active_model': m})
    
    def fetch_model_templates(self):
        threading.Thread(target = self._fetch_model_templates).start()
        
    def _fetch_model_templates(self):
        self.fetch_model_templates_start.emit()
        success = True
        error = None
        if self.db_type == 'local_files':
            self.model_templates = pd.read_csv(Path.joinpath(dummy_data_path, 'model_templates.csv'))
        elif self.db_type == 'local_mysql_db':
            db_response = self.db.fetch_model_templates()
            if db_response['success']:
                self.model_templates = db_response['data']
            else:
                success = False
                error = db_response['error']
                
        self.fetch_model_templates_end.emit({'success': success, 'error': error, 'data': self.model_templates})
    
    def fetch_models(self):
        threading.Thread(target = self._fetch_models).start()

    def _fetch_models(self):
        self.fetch_models_start.emit({'project': self.active_project})
        success = True
        error = None
        models = None
        
        if self.active_project is None:
            success = False
            error = 'active_project is None!'
        else:
            project_id = self.active_project['id']
            if self.db_type == 'local_files':
                all_models = pd.read_csv(self.models_path)
                models = all_models[(all_models['project_id'] == project_id)]
                models.loc[:,'created_at'] = pd.to_datetime(models['created_at'])
                models.loc[:,'last_modified_at'] = pd.to_datetime(models['last_modified_at'])
                models_sorted = models.sort_values(by = 'created_at', ascending = False, ignore_index = True)
                models = models_sorted
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.fetch_models_by_project_id(project_id)
                if db_response['success']:
                    models = db_response['data']
                else:
                    success = False
                    error = db_response['error']
        
        if success:
            self.models = models
        
        self.fetch_models_end.emit({'success': success, 'error': error, 'data': models})
    
    def create_model(self, title: str = None):
        threading.Thread(target = self._create_model, args = (title,)).start()

    def _create_model(self, title: str = None):
        self.create_model_start.emit({'title': title})
        success = True
        error = None
        data = None
        
        if title is None:
            success = False
            error = 'Title is None!'
        else:
            project_id = self.active_project['id']
            if self.db_type == 'local_files':
                current_time = datetime.now()
                formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
                all_models = pd.read_csv(self.models_path)
                if title in all_models['title'].tolist():
                    success = False
                    error = f'You already have a model called {title}. Please specify a different title.'
                else:
                    new_model = pd.DataFrame.from_dict([{'id': str(uuid.uuid4()),
                                                         'project_id': project_id,
                                                         'created_at': formatted_time,
                                                         'last_modified_at': formatted_time,
                                                         'title': title,
                                                         'labels': ''}])
                    all_models = pd.concat((all_models, new_model))
                    all_models.to_csv(path_or_buf = self.models_path, index = False)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.create_model_by_project_id(project_id, title)
                if db_response['success']:
                    data = db_response['data']
                else:
                    success = False
                    error = db_response['error']
        
        self.create_model_end.emit({'success': success, 'error': error, 'data': data})
    
    def update_reference_data_id(self, reference_data_id: str = None, model_id: str = None):
        # threading.Thread(target = self._update_reference_data_id, args = (reference_data_id, model_id)).start()
        self._update_reference_data_id(reference_data_id, model_id)
    
    def _update_reference_data_id(self, reference_data_id: str = None, model_id: str = None):
        self.update_reference_data_id_start.emit({'reference_data_id': reference_data_id, 'model_id': model_id})
        success = True
        error = None
        data = None
        
        if model_id is None:
            success = False
            error = 'model_id is None!'
        elif reference_data_id == self.models.loc[self.models['id'] == model_id, 'reference_data_id'].iloc[0]:
            success = False
            error = 'reference_data_id is the same as the one you are trying to set!'
        else:
            if self.db_type == 'local_files':
                all_models = pd.read_csv(self.models_path)
                all_models.loc[all_models['id'] == model_id, 'reference_data_id'] = reference_data_id
                all_models.to_csv(path_or_buf = self.models_path, index = False)
                self.models.loc[self.models['id'] == model_id, 'reference_data_id'] = reference_data_id
                if self.active_model is not None and self.active_model['id'] == model_id:
                    self.set_active_model(all_models[all_models['id'] == model_id].squeeze(), override = True)
            elif self.db_type == 'local_mysql_db':
                db_response = self.db.update_reference_data_id_by_model_id(reference_data_id, model_id)
                if db_response['success']:
                    data = db_response['data']
                else:
                    success = False
                    error = db_response['error']
        
        self.update_reference_data_id_end.emit({'success': success, 'error': error, 'data': data})
        