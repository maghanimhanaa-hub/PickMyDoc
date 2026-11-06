import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import database as db
from models.patient import Patient
from models.medecin import Medecin
from models.consultation import Consultation


class PageCRUD(ttk.Frame):
    """Page générique : formulaire + tableau + Ajouter/Modifier/Supprimer."""

    def __init__(self, parent, titre, champs, lister, ajouter, modifier, supprimer,
                 optionnels=(), numeriques=(), apres_changement=None):
        super().__init__(parent, padding=10)
        self.champs, self.optionnels, self.numeriques = champs, optionnels, numeriques
        self.f_lister, self.f_ajouter = lister, ajouter
        self.f_modifier, self.f_supprimer = modifier, supprimer
        self.apres_changement = apres_changement
        self.lignes = {}

        form = ttk.LabelFrame(self, text=titre, padding=10)
        form.pack(fill="x")
        self.entrees = {}
        for i, (cle, libelle) in enumerate(champs):
            ttk.Label(form, text=libelle + " :").grid(row=i // 2, column=(i % 2) * 2, sticky="w", padx=5, pady=3)
            e = ttk.Entry(form, width=25)
            e.grid(row=i // 2, column=(i % 2) * 2 + 1, padx=5, pady=3)
            self.entrees[cle] = e

        boutons = ttk.Frame(form)
        boutons.grid(row=(len(champs) + 1) // 2, column=0, columnspan=4, pady=8)
        for texte, cmd in [("Ajouter", self.ajouter), ("Modifier", self.modifier),
                           ("Supprimer", self.supprimer), ("Vider", self.vider)]:
            ttk.Button(boutons, text=texte, command=cmd).pack(side="left", padx=5)

        cles = [c for c, _ in champs]
        self.table = ttk.Treeview(self, columns=cles, show="headings", selectmode="browse")
        for cle, libelle in champs:
            self.table.heading(cle, text=libelle)
            self.table.column(cle, width=110)
        self.table.pack(fill="both", expand=True, pady=10)
        self.table.bind("<<TreeviewSelect>>", self.remplir)
        self.charger()

    def donnees(self):
        """Lignes à afficher (peut être redéfinie, par exemple pour filtrer)."""
        return self.f_lister()

    def charger(self):
        self.table.delete(*self.table.get_children())
        self.lignes = {}
        for row in self.donnees():
            iid = str(row[0])
            self.lignes[iid] = row
            self.table.insert("", "end", iid=iid, values=row[1:])

    def remplir(self, _event=None):
        sel = self.table.selection()
        if not sel:
            return
        row = self.lignes[sel[0]]
        for (cle, _), valeur in zip(self.champs, row[1:]):
            self.entrees[cle].delete(0, "end")
            self.entrees[cle].insert(0, "" if valeur is None else valeur)

    def vider(self):
        for e in self.entrees.values():
            e.delete(0, "end")
        self.table.selection_remove(self.table.selection())

    def lire_formulaire(self):
        valeurs = []
        for cle, libelle in self.champs:
            v = self.entrees[cle].get().strip()
            if not v and cle not in self.optionnels:
                messagebox.showerror("Erreur", f"Le champ « {libelle} » est obligatoire.")
                return None
            if cle in self.numeriques:
                try:
                    v = float(v.replace(",", "."))
                except ValueError:
                    messagebox.showerror("Erreur", f"« {libelle} » doit être un nombre.")
                    return None
            valeurs.append(v)
        return valeurs

    def termine(self):
        self.charger()
        self.vider()
        if self.apres_changement:
            self.apres_changement()

    def ajouter(self):
        valeurs = self.lire_formulaire()
        if valeurs is not None:
            self.f_ajouter(*valeurs)
            self.termine()

    def modifier(self):
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionne une ligne dans le tableau.")
            return
        valeurs = self.lire_formulaire()
        if valeurs is not None:
            self.f_modifier(int(sel[0]), *valeurs)
            self.termine()

    def supprimer(self):
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionne une ligne dans le tableau.")
            return
        if not messagebox.askyesno("Confirmation", "Supprimer cet enregistrement ?"):
            return
        try:
            self.f_supprimer(int(sel[0]))
        except sqlite3.IntegrityError:
            messagebox.showerror("Impossible", "Des consultations sont liées à cet enregistrement.")
            return
        self.termine()


class PageMedecins(PageCRUD):
    """Page Médecins : CRUD + recherche par nom, spécialité et ville."""

    filtres = None   # None = pas de filtre, sinon dict {nom, specialite, ville}

    def __init__(self, parent, apres_changement=None):
        super().__init__(
            parent, "Médecin",
            [("nom", "Nom"), ("prenom", "Prénom"), ("specialite", "Spécialité"),
             ("telephone", "Téléphone"), ("ville", "Ville"), ("tarif", "Tarif (DH)")],
            db.lister_medecins, db.ajouter_medecin, db.modifier_medecin, db.supprimer_medecin,
            numeriques=("tarif",), apres_changement=apres_changement)

        # Barre de recherche, placée entre le formulaire et le tableau
        recherche = ttk.LabelFrame(self, text="Rechercher un médecin", padding=10)
        recherche.pack(fill="x", before=self.table)
        self.rech = {}
        for i, (cle, libelle) in enumerate([("nom", "Nom"), ("specialite", "Spécialité"), ("ville", "Ville")]):
            ttk.Label(recherche, text=libelle + " :").grid(row=0, column=i * 2, sticky="w", padx=5)
            e = ttk.Entry(recherche, width=16)
            e.grid(row=0, column=i * 2 + 1, padx=5)
            e.bind("<Return>", lambda _e: self.rechercher())
            self.rech[cle] = e
        ttk.Button(recherche, text="Rechercher", command=self.rechercher).grid(row=0, column=6, padx=5)
        ttk.Button(recherche, text="Réinitialiser", command=self.reinitialiser).grid(row=0, column=7, padx=5)

    def donnees(self):
        if self.filtres:
            return db.rechercher_medecins(**self.filtres)
        return self.f_lister()

    def rechercher(self):
        self.filtres = {cle: e.get().strip() for cle, e in self.rech.items()}
        self.charger()
        if not self.lignes:
            messagebox.showinfo("Recherche", "Aucun médecin ne correspond à ta recherche.")

    def reinitialiser(self):
        for e in self.rech.values():
            e.delete(0, "end")
        self.filtres = None
        self.charger()


class PageConsultations(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent, padding=10)
        form = ttk.LabelFrame(self, text="Consultation", padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Patient :").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self.cb_patient = ttk.Combobox(form, state="readonly", width=32)
        self.cb_patient.grid(row=0, column=1, padx=5)
        ttk.Label(form, text="Médecin :").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        self.cb_medecin = ttk.Combobox(form, state="readonly", width=32)
        self.cb_medecin.grid(row=1, column=1, padx=5)
        ttk.Label(form, text="Date (AAAA-MM-JJ) :").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        self.date = ttk.Entry(form, width=15)
        self.date.grid(row=2, column=1, sticky="w", padx=5)
        ttk.Label(form, text="Heure (HH:MM) :").grid(row=3, column=0, sticky="w", padx=5, pady=3)
        self.heure = ttk.Entry(form, width=10)
        self.heure.grid(row=3, column=1, sticky="w", padx=5)

        boutons = ttk.Frame(form)
        boutons.grid(row=4, column=0, columnspan=2, pady=8)
        for texte, cmd in [("Réserver", self.reserver), ("Modifier l'horaire", self.modifier_horaire),
                           ("Annuler", lambda: self.statut("Annulée")),
                           ("Marquer terminée", lambda: self.statut("Terminée")),
                           ("Détails", self.afficher_details)]:
            ttk.Button(boutons, text=texte, command=cmd).pack(side="left", padx=5)

        cols = ("patient", "medecin", "specialite", "date", "heure", "statut")
        self.table = ttk.Treeview(self, columns=cols, show="headings", selectmode="browse")
        for c, t in zip(cols, ["Patient", "Médecin", "Spécialité", "Date", "Heure", "Statut"]):
            self.table.heading(c, text=t)
            self.table.column(c, width=120)
        self.table.pack(fill="both", expand=True, pady=10)

        self.charger_choix()
        self.charger()

    def charger_choix(self):
        self.patients = db.lister_patients()
        self.medecins = db.lister_medecins()
        self.cb_patient["values"] = [f"{p[1]} {p[2]}" for p in self.patients]
        self.cb_medecin["values"] = [f"Dr {m[1]} {m[2]} - {m[3]}" for m in self.medecins]

    def charger(self):
        self.table.delete(*self.table.get_children())
        for row in db.lister_consultations():
            self.table.insert("", "end", iid=str(row[0]), values=row[1:])

    def lire_date_heure(self):
        date, heure = self.date.get().strip(), self.heure.get().strip()
        try:
            datetime.strptime(date, "%Y-%m-%d")
            datetime.strptime(heure, "%H:%M")
        except ValueError:
            messagebox.showerror("Erreur", "Format attendu : date AAAA-MM-JJ et heure HH:MM.")
            return None
        return date, heure

    def reserver(self):
        ip, im = self.cb_patient.current(), self.cb_medecin.current()
        if ip < 0 or im < 0:
            messagebox.showerror("Erreur", "Choisis un patient et un médecin.")
            return
        dh = self.lire_date_heure()
        if not dh:
            return
        id_medecin = self.medecins[im][0]
        if not db.creneau_disponible(id_medecin, *dh):
            messagebox.showerror("Indisponible", "Ce médecin a déjà une consultation à ce créneau.")
            return
        db.ajouter_consultation(self.patients[ip][0], id_medecin, *dh)
        self.charger()

    def selection(self):
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning("Attention", "Sélectionne une consultation.")
            return None
        return int(sel[0])

    def statut(self, nouveau):
        id_c = self.selection()
        if id_c and messagebox.askyesno("Confirmation", f"Passer cette consultation en « {nouveau} » ?"):
            db.changer_statut(id_c, nouveau)
            self.charger()

    def modifier_horaire(self):
        id_c = self.selection()
        dh = self.lire_date_heure() if id_c else None
        if dh:
            if db.modifier_horaire(id_c, *dh):
                self.charger()
            else:
                messagebox.showerror("Indisponible", "Ce créneau est déjà pris.")

    def afficher_details(self):
        """Construit des objets Patient, Medecin et Consultation à partir de la base."""
        id_c = self.selection()
        if not id_c:
            return
        d = db.details_consultation(id_c)
        if d is None:
            messagebox.showerror("Erreur", "Consultation introuvable.")
            return
        patient = Patient(d[0], d[1], d[2], d[3])
        medecin = Medecin(d[4], d[5], d[6], d[7], d[8], d[9])
        consultation = Consultation(patient, medecin, d[10], d[11])
        consultation.statut = d[12]
        texte = (f"=== PATIENT ===\n{patient.afficher_informations()}\n\n"
                 f"=== MÉDECIN ===\n{medecin.afficher_informations()}\n\n"
                 f"=== CONSULTATION ===\n{consultation.afficher_informations()}")
        messagebox.showinfo("Détails de la consultation", texte)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PickMyDoc - Gestion des consultations")
        self.geometry("1000x600")

        onglets = ttk.Notebook(self)
        onglets.pack(fill="both", expand=True)

        patients = PageCRUD(
            onglets, "Patient",
            [("nom", "Nom"), ("prenom", "Prénom"), ("telephone", "Téléphone"), ("email", "Email")],
            db.lister_patients, db.ajouter_patient, db.modifier_patient, db.supprimer_patient,
            optionnels=("email",), apres_changement=lambda: consultations.charger_choix())
        medecins = PageMedecins(onglets, apres_changement=lambda: consultations.charger_choix())
        consultations = PageConsultations(onglets)

        onglets.add(patients, text="Patients")
        onglets.add(medecins, text="Médecins")
        onglets.add(consultations, text="Consultations")


if __name__ == "__main__":
    db.creer_base_de_donnees()   # sans effet si les tables existent déjà
    App().mainloop()