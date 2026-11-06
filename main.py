from models.medecin import Medecin
from models.patient import Patient
from models.consultation import Consultation
# Création d'un médecin
medecin1 = Medecin("Amine", "Karim", "Cardiologie", "0612345678", "Casablanca", 300)
# Création d'un patient
patient1 = Patient("Alaoui", "Sara", "0623456789")
# Création d'une consultation
consultation1 = Consultation(patient1, medecin1, "2026-11-10", "10:30")
# Afficher les informations
print("=== MÉDECIN ===")
print(medecin1.afficher_informations())
print("\n=== PATIENT ===")
print(patient1.afficher_informations())
print("\n=== CONSULTATION ===")
print(consultation1.afficher_informations())
# Annuler la consultation
consultation1.annuler()
print("\n=== APRÈS ANNULATION ===")
print(consultation1.afficher_informations())