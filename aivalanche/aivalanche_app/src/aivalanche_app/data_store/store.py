import json
from aivalanche_app.data_store.utils import project, model, user
from aivalanche_app.paths import dummy_data_path

# Just to test the UI
dummy_data = json.load(open(dummy_data_path))

class store():
    def __init__(self, user_id: str = None):
        self.user = user(id = user_id)
        
        self.projects = []
        self.active_project_id = None
        self.active_project = None
        
        self.models = []
        self.active_model_id = None
        self.active_model = None
    
        self.get_all_projects()
    
    def get_all_projects(self):
        for item in dummy_data['projects']:
            models = [model(id = m['id'], title = m['title'], created = m['created'], last_modified = m['last_modified']) for m in item['models']]
            p = project(id = item['id'], title = item['title'], created = item['created'], last_modified = item['last_modified'], models = models)
            self.projects.append(p)

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