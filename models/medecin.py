class Medecin:
    def __init__(self, nom, prenom, specialite, telephone, ville, tarif):
        self.nom = nom
        self.prenom = prenom
        self.specialite = specialite
        self.telephone = telephone
        self.ville = ville
        self.tarif = tarif
    def afficher_informations(self):
        return (
            f"Nom : {self.nom}\n"
            f"Prénom : {self.prenom}\n"
            f"Spécialité : {self.specialite}\n"
            f"Téléphone : {self.telephone}\n"
            f"Ville : {self.ville}\n"
            f"Tarif : {self.tarif} DH"
        )
