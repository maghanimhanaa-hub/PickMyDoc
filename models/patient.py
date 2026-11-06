class Patient:
    def __init__(self, nom, prenom, telephone, email=None):
        self.nom = nom
        self.prenom = prenom
        self.telephone = telephone
        self.email = email
    def afficher_informations(self):
        return (
            f"Nom : {self.nom}\n"
            f"Prénom : {self.prenom}\n"
            f"Téléphone : {self.telephone}\n"
            f"Email : {self.email if self.email else 'Non renseigné'}"
        )