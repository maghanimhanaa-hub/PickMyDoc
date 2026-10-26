
class Personne:
    def __init__(self, nom, telephone):
        self.nom = nom
        self.telephone = telephone

    def afficher_informations(self):
        return (
            f"Nom : {self.nom}\n"
            f"Téléphone : {self.telephone}"
        )
