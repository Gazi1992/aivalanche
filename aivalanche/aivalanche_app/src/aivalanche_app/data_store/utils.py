from datetime import datetime

# User class
class user():
    def __init__(self, id: str = None, name: str = None, created_at: datetime = None):
        self.id = id
        self.name = name
        self.created_at = created_at
        
    def update(self, data):
        for key, value in data.items():
            setattr(self, key, value)

# Model class
class model():
    def __init__(self, id: str = None, title: str = None, labels: list[str] = None,
                 created_at: datetime = None, last_modified: datetime = None):
        self.id = id
        self.title = title
        self.labels = labels
        self.created_at = created_at
        self.last_modified = last_modified
        
    def update(self, data):
        for key, value in data.items():
            setattr(self, key, value)


# Project class
class project():
    def __init__(self, id: str = None, user_id: str = None, title: str = None, labels: list[str] = None,
                 created_at: datetime = None, last_modified: datetime = None, models: list[model] = None):
        self.id = id
        self.user_is = user_id
        self.title = title
        self.labels = labels
        self.created_at = created_at
        self.last_modified = last_modified
        self.models = models
        
    def update(self, data):
        for key, value in data.items():
            setattr(self, key, value)


