from datetime import datetime

# User class
class user():
    def __init__(self, id: str = None, name: str = None, created: datetime = None):
        self.id = id
        self.name = name
        self.created = created
    

# Model class
class model():
    def __init__(self, id: str = None, title: str = None, labels: list[str] = None,
                 created: datetime = None, last_modified: datetime = None):
        self.id = id
        self.title = title
        self.labels = labels
        self.created = created
        self.last_modified = last_modified


# Project class
class project():
    def __init__(self, id: str = None, title: str = None, labels: list[str] = None,
                 created: datetime = None, last_modified: datetime = None, models: list[model] = None):
        self.id = id
        self.title = title
        self.labels = labels
        self.created = created
        self.last_modified = last_modified
        self.models = models


