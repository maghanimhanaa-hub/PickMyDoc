
from models.personne import Personne


class Patient(Personne):
    def __init__(self, nom, telephone):
        super().__init__(nom, telephone)
