import sqlite3

DB = "pickmydoc.db"


def creer_base_de_donnees():
    connexion = sqlite3.connect(DB)
    connexion.execute("PRAGMA foreign_keys = ON")
    curseur = connexion.cursor()

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS Patient (
            id_patient INTEGER PRIMARY KEY,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            telephone TEXT NOT NULL,
            email TEXT
        )
    """)

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS Medecin (
            id_medecin INTEGER PRIMARY KEY,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            specialite TEXT NOT NULL,
            telephone TEXT NOT NULL,
            ville TEXT NOT NULL,
            tarif REAL NOT NULL
        )
    """)

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS Consultation (
            id_consultation INTEGER PRIMARY KEY,
            id_patient INTEGER NOT NULL,
            id_medecin INTEGER NOT NULL,
            date_consultation TEXT NOT NULL,
            heure_consultation TEXT NOT NULL,
            statut TEXT NOT NULL DEFAULT 'Planifiée',
            FOREIGN KEY (id_patient) REFERENCES Patient(id_patient),
            FOREIGN KEY (id_medecin) REFERENCES Medecin(id_medecin),
            CHECK (statut IN ('Planifiée', 'Annulée', 'Terminée'))
        )
    """)

    connexion.commit()
    connexion.close()


def executer(sql, params=(), lire=False):
    connexion = sqlite3.connect(DB)
    connexion.execute("PRAGMA foreign_keys = ON")
    try:
        curseur = connexion.execute(sql, params)
        resultat = curseur.fetchall() if lire else None
        connexion.commit()
        return resultat
    finally:
        connexion.close()


# ---------- Patients ----------
def lister_patients():
    return executer("SELECT id_patient, nom, prenom, telephone, email FROM Patient ORDER BY nom", lire=True)

def ajouter_patient(nom, prenom, telephone, email):
    executer("INSERT INTO Patient (nom, prenom, telephone, email) VALUES (?, ?, ?, ?)",
             (nom, prenom, telephone, email))

def modifier_patient(id_patient, nom, prenom, telephone, email):
    executer("UPDATE Patient SET nom=?, prenom=?, telephone=?, email=? WHERE id_patient=?",
             (nom, prenom, telephone, email, id_patient))

def supprimer_patient(id_patient):
    executer("DELETE FROM Patient WHERE id_patient=?", (id_patient,))


# ---------- Médecins ----------
def lister_medecins():
    return executer("SELECT id_medecin, nom, prenom, specialite, telephone, ville, tarif "
                    "FROM Medecin ORDER BY nom", lire=True)

def rechercher_medecins(nom="", specialite="", ville=""):
    return executer(
        "SELECT id_medecin, nom, prenom, specialite, telephone, ville, tarif "
        "FROM Medecin WHERE nom LIKE ? AND specialite LIKE ? AND ville LIKE ? "
        "ORDER BY nom",
        (f"%{nom}%", f"%{specialite}%", f"%{ville}%"), lire=True)

def ajouter_medecin(nom, prenom, specialite, telephone, ville, tarif):
    executer("INSERT INTO Medecin (nom, prenom, specialite, telephone, ville, tarif) "
             "VALUES (?, ?, ?, ?, ?, ?)", (nom, prenom, specialite, telephone, ville, tarif))

def modifier_medecin(id_medecin, nom, prenom, specialite, telephone, ville, tarif):
    executer("UPDATE Medecin SET nom=?, prenom=?, specialite=?, telephone=?, ville=?, tarif=? "
             "WHERE id_medecin=?", (nom, prenom, specialite, telephone, ville, tarif, id_medecin))

def supprimer_medecin(id_medecin):
    executer("DELETE FROM Medecin WHERE id_medecin=?", (id_medecin,))


# ---------- Consultations ----------
def lister_consultations():
    # Jointure écrite avec FROM + WHERE
    return executer(
        "SELECT c.id_consultation, p.nom || ' ' || p.prenom, m.nom || ' ' || m.prenom, "
        "m.specialite, c.date_consultation, c.heure_consultation, c.statut "
        "FROM Consultation c, Patient p, Medecin m "
        "WHERE c.id_patient = p.id_patient AND c.id_medecin = m.id_medecin "
        "ORDER BY c.date_consultation, c.heure_consultation", lire=True)

def details_consultation(id_consultation):
    """Retourne toutes les infos d'une consultation (patient, médecin, date, heure, statut)."""
    lignes = executer(
        "SELECT p.nom, p.prenom, p.telephone, p.email, "
        "m.nom, m.prenom, m.specialite, m.telephone, m.ville, m.tarif, "
        "c.date_consultation, c.heure_consultation, c.statut "
        "FROM Consultation c, Patient p, Medecin m "
        "WHERE c.id_patient = p.id_patient AND c.id_medecin = m.id_medecin "
        "AND c.id_consultation = ?", (id_consultation,), lire=True)
    return lignes[0] if lignes else None

def creneau_disponible(id_medecin, date, heure, ignorer=-1):
    n = executer("SELECT COUNT(*) FROM Consultation "
                 "WHERE id_medecin=? AND date_consultation=? AND heure_consultation=? "
                 "AND statut='Planifiée' AND id_consultation != ?",
                 (id_medecin, date, heure, ignorer), lire=True)[0][0]
    return n == 0

def ajouter_consultation(id_patient, id_medecin, date, heure):
    executer("INSERT INTO Consultation (id_patient, id_medecin, date_consultation, heure_consultation) "
             "VALUES (?, ?, ?, ?)", (id_patient, id_medecin, date, heure))

def changer_statut(id_consultation, statut):
    executer("UPDATE Consultation SET statut=? WHERE id_consultation=?", (statut, id_consultation))

def modifier_horaire(id_consultation, date, heure):
    id_medecin = executer("SELECT id_medecin FROM Consultation WHERE id_consultation=?",
                          (id_consultation,), lire=True)[0][0]
    if not creneau_disponible(id_medecin, date, heure, ignorer=id_consultation):
        return False
    executer("UPDATE Consultation SET date_consultation=?, heure_consultation=? "
             "WHERE id_consultation=?", (date, heure, id_consultation))
    return True