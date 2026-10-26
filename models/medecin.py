
from models.personne import Personne


class Medecin(Personne):
    def __init__(self, nom, telephone, specialite, ville, tarif):
        super().__init__(nom, telephone)
        self.specialite = specialite
        self.ville = ville
        self.tarif = tarif

    def afficher_informations(self):
        informations = super().afficher_informations()
        return (
            f"{informations}\n"
            f"Spécialité : {self.specialite}\n"
            f"Ville : {self.ville}\n"
            f"Tarif : {self.tarif} DH"
        )
