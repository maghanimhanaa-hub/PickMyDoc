import sqlite3
def creer_base_de_donnees():
    # Connexion à la base de données
    connexion = sqlite3.connect("pickmydoc.db")
    # Activer les clés étrangères
    connexion.execute("PRAGMA foreign_keys = ON")
    curseur = connexion.cursor()
    # Table Patient
    curseur.execute("""
        CREATE TABLE IF NOT EXISTS Patient (
            id_patient INTEGER PRIMARY KEY,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            telephone TEXT NOT NULL,
            email TEXT
        )
    """)
   # Table Medecin
    curseur.execute("""
        CREATE TABLE IF NOT EXISTS Medecin (
            id_medecin INTEGER PRIMARY KEY,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            specialite TEXT NOT NULL,
            telephone TEXT NOT NULL,
            ville TEXT NOT NULL
            tarif REAL NOT NULL
        )
    """)
    # Table Consultation
    curseur.execute("""
        CREATE TABLE IF NOT EXISTS Consultation (
            id_consultation INTEGER PRIMARY KEY,
            id_patient INTEGER NOT NULL,
            id_medecin INTEGER NOT NULL,
            date_consultation TEXT NOT NULL,
            heure_consultation TEXT NOT NULL,
            statut TEXT NOT NULL DEFAULT 'Planifiée',

            FOREIGN KEY (id_patient)
                REFERENCES Patient(id_patient),

            FOREIGN KEY (id_medecin)
                REFERENCES Medecin(id_medecin),

            CHECK (statut IN ('Planifiée', 'Annulée', 'Terminée'))
        )
    """)
    connexion.commit()
    connexion.close()
    print("Base de données créée avec succès !")
if __name__ == "__main__":
    creer_base_de_donnees()