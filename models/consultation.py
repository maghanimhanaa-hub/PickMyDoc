class Consultation:
    def __init__(self, patient, medecin, date, heure):
        self.patient = patient
        self.medecin = medecin
        self.date = date
        self.heure = heure
        self.statut = "Confirmée"

    def afficher_informations(self):
        return (
            f"Patient : {self.patient.nom}\n"
            f"Médecin : {self.medecin.nom}\n"
            f"Date : {self.date}\n"
            f"Heure : {self.heure}\n"
            f"Statut : {self.statut}"
        )

    def annuler(self):
        self.statut = "Annulée"

    def modifier_horaire(self, nouvelle_date, nouvelle_heure):
        self.date = nouvelle_date
        self.heure = nouvelle_heure
