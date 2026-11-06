class Consultation:
    def __init__(self, patient, medecin, date_consultation, heure_consultation):
        self.patient = patient
        self.medecin = medecin
        self.date_consultation = date_consultation
        self.heure_consultation = heure_consultation
        self.statut = "Planifiée"

    def afficher_informations(self):
        return (
            f"Patient : {self.patient.prenom} {self.patient.nom}\n"
            f"Médecin : Dr {self.medecin.nom} {self.medecin.prenom}\n"
            f"Date : {self.date_consultation}\n"
            f"Heure : {self.heure_consultation}\n"
            f"Statut : {self.statut}"
        )

    def annuler(self):
        self.statut = "Annulée"

    def modifier_horaire(self, nouvelle_date, nouvelle_heure):
        self.date_consultation = nouvelle_date
        self.heure_consultation = nouvelle_heure