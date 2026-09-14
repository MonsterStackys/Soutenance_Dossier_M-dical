from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import AuditLog, User
from consultations.models import Constante, Consultation, LigneOrdonnance, Ordonnance, RendezVous
from patients.models import Patient


class Command(BaseCommand):
    help = "Remplit la base avec des comptes de test et quelques dossiers fictifs."

    def handle(self, *args, **options):
        self.stdout.write("Initialisation des données de démonstration…")
        users = self._users()
        patients = self._patients(users["reception"])
        self._clinique(users, patients)
        self._rendez_vous(users, patients)
        self._audit_demo(users)
        self.stdout.write(self.style.SUCCESS("Terminé. Comptes :"))
        self.stdout.write("  admin / Admin123!     (ADMIN)")
        self.stdout.write("  medecin / Medecin123! (MEDECIN)")
        self.stdout.write("  infirmier / Infirmier123! (INFIRMIER)")
        self.stdout.write("  reception / Reception123! (RECEPTIONNISTE)")

    def _users(self):
        specs = [
            ("admin", "Admin123!", User.Role.ADMIN, True, True, "Kouassi", "Awa"),
            ("medecin", "Medecin123!", User.Role.MEDECIN, False, True, "N'Diaye", "Mamadou"),
            ("infirmier", "Infirmier123!", User.Role.INFIRMIER, False, True, "Traoré", "Fatou"),
            ("reception", "Reception123!", User.Role.RECEPTIONNISTE, False, False, "Diallo", "Aminata"),
        ]
        created = {}
        for username, password, role, superuser, staff, last, first in specs:
            user, is_new = User.objects.get_or_create(
                username=username,
                defaults={
                    "role": role,
                    "first_name": first,
                    "last_name": last,
                    "email": f"{username}@poste-sante.local",
                    "is_staff": staff or superuser,
                    "is_superuser": superuser,
                },
            )
            user.role = role
            user.is_staff = staff or superuser
            user.is_superuser = superuser
            user.set_password(password)
            user.save()
            key = "reception" if username == "reception" else username
            created[key] = user
            flag = "créé" if is_new else "mis à jour"
            self.stdout.write(f"  - {username} ({flag})")
        return created

    def _patients(self, reception):
        if Patient.objects.exists():
            self.stdout.write("Patients déjà présents : on ne recrée pas les dossiers.")
            return list(Patient.objects.all())

        data = [
            ("Bamba", "Issa", date(1988, 3, 12), "M", "O+", "0701020304", "Quartier Commerce", "HTA", "", "Pénicilline"),
            ("Koné", "Awa", date(1995, 7, 21), "F", "A+", "0702030405", "Cité des Infirmiers", "Asthme", "Appendicectomie 2014", ""),
            ("Ouattara", "Yao", date(2012, 1, 5), "M", "B+", "0703040506", "Village Nord", "", "", ""),
            ("Soro", "Mariam", date(1964, 11, 30), "F", "O-", "0704050607", "Derrière la mosquée", "Diabète type 2", "Césarienne 1998", "AINS"),
            ("Touré", "Abdoulaye", date(2001, 9, 18), "M", "AB+", "0705060708", "Campement", "Paludisme à répétition", "", ""),
            ("Cissé", "Adjoua", date(1978, 4, 2), "F", "A-", "0706070809", "Route de la gare", "", "Hernie inguinale 2020", ""),
            ("Yao", "Koffi", date(1955, 6, 14), "M", "B-", "0707080910", "Ancien marché", "BPCO, HTA", "", "Iode"),
            ("Fofana", "Nafissatou", date(2018, 12, 9), "F", "O+", "0708091011", "Cité scolaire", "", "", ""),
        ]
        patients = []
        for nom, prenom, naissance, genre, gs, tel, adresse, am, ac, al in data:
            p = Patient(
                nom=nom,
                prenom=prenom,
                date_naissance=naissance,
                genre=genre,
                groupe_sanguin=gs,
                telephone=tel,
                adresse=adresse,
                antecedent_medicaux=am,
                antecedent_chirurgicaux=ac,
                allergies=al,
                created_by=reception,
            )
            p.save()
            patients.append(p)
        self.stdout.write(f"  {len(patients)} patients créés.")
        return patients

    def _clinique(self, users, patients):
        if Consultation.objects.exists():
            self.stdout.write("Consultations déjà présentes : skip clinique.")
            return

        infirmier = users["infirmier"]
        medecin = users["medecin"]
        now = timezone.now()

        # Constantes du jour + hier
        scenarios = [
            (0, "128/82", 37.2, 78.0, 172.0, 76, "Repos 5 min"),
            (0, "110/70", 36.8, 62.5, 165.0, 72, ""),
            (1, "145/90", 38.4, 54.0, 148.0, 98, "Fièvre"),
            (2, "100/65", 37.0, 28.0, 132.0, 88, "Enfant"),
            (3, "150/95", 36.6, 81.0, 158.0, 80, "HTA connue"),
            (4, "118/76", 39.1, 68.0, 175.0, 102, "Accès fébrile"),
        ]
        constantes = []
        for idx, (p_i, ta, temp, poids, taille, fc, notes) in enumerate(scenarios):
            c = Constante.objects.create(
                patient=patients[p_i],
                date=now - timedelta(hours=idx),
                tension_arterielle=ta,
                temperature=temp,
                poids=poids,
                taille=taille,
                frequence_cardiaque=fc,
                pris_par=infirmier,
                notes=notes,
            )
            constantes.append(c)

        consults = [
            (0, 0, "Céphalées et vertiges", "Céphalées pulsatiles, phosphènes", "HTA non contrôlée", "Amlodipine, régime hyposodé, contrôle J7"),
            (1, 1, "Toux et dyspnée", "Toux sèche nocturne, sibilants", "Crise d'asthme légère", "Ventoline, éviter allergènes"),
            (4, 5, "Fièvre et frissons", "Fièvre 39, céphalées, nausées", "Accès palustre simple (suspicion)", "TDR + CTA 3 jours, paracétamol"),
            (3, 4, "Suivi diabète", "Polyurie, soif", "Diabète type 2 déséquilibré", "Renforcer règles hygiéno-diététiques, bilan"),
        ]
        for p_i, c_i, motif, sympt, diag, cat in consults:
            cons = Consultation.objects.create(
                patient=patients[p_i],
                medecin=medecin,
                constante=constantes[c_i],
                motif=motif,
                symptomes=sympt,
                diagnostic=diag,
                conduite_a_tenir=cat,
                date_consultation=now - timedelta(minutes=30 * (p_i + 1)),
            )
            ordn = Ordonnance.objects.create(consultation=cons)
            if p_i == 0:
                LigneOrdonnance.objects.create(
                    ordonnance=ordn,
                    medicament_nom="Amlodipine 5 mg",
                    posologie="1 comprimé le matin",
                    duree_traitement="30 jours",
                )
                LigneOrdonnance.objects.create(
                    ordonnance=ordn,
                    medicament_nom="Paracétamol 1 g",
                    posologie="1 comprimé si douleur, max 3/j",
                    duree_traitement="5 jours",
                )
            elif p_i == 1:
                LigneOrdonnance.objects.create(
                    ordonnance=ordn,
                    medicament_nom="Salbutamol 100 µg",
                    posologie="2 bouffées si crise",
                    duree_traitement="À la demande",
                )
            elif p_i == 4:
                LigneOrdonnance.objects.create(
                    ordonnance=ordn,
                    medicament_nom="Artéméther / Luméfantrine",
                    posologie="Selon poids, matin et soir",
                    duree_traitement="3 jours",
                )
                LigneOrdonnance.objects.create(
                    ordonnance=ordn,
                    medicament_nom="Paracétamol 500 mg",
                    posologie="1 comprimé x 3 / jour",
                    duree_traitement="3 jours",
                )
            else:
                LigneOrdonnance.objects.create(
                    ordonnance=ordn,
                    medicament_nom="Metformine 500 mg",
                    posologie="1 comprimé matin et soir pendant le repas",
                    duree_traitement="30 jours",
                )
        self.stdout.write("  Constantes, consultations et ordonnances créées.")

    def _rendez_vous(self, users, patients):
        if RendezVous.objects.exists() or not patients:
            return
        medecin = users["medecin"]
        now = timezone.now()
        RendezVous.objects.create(
            patient=patients[0],
            medecin=medecin,
            date_heure=now + timedelta(days=1, hours=2),
            motif="Contrôle tension artérielle",
        )
        RendezVous.objects.create(
            patient=patients[3] if len(patients) > 3 else patients[0],
            medecin=medecin,
            date_heure=now + timedelta(days=2, hours=3),
            motif="Suivi diabète",
        )
        self.stdout.write("  Rendez-vous de démonstration créés.")

    def _audit_demo(self, users):
        if AuditLog.objects.filter(efface_le__isnull=False).exists():
            return
        ancien = AuditLog.objects.create(
            utilisateur=users["reception"],
            action="patients:creer",
            description="Commande de démonstration déjà sortie du journal quotidien",
            methode="POST",
            chemin="/patients/nouveau/",
        )
        AuditLog.objects.filter(pk=ancien.pk).update(
            created_at=timezone.now() - timedelta(hours=30),
            efface_le=timezone.now() - timedelta(hours=5),
        )
        self.stdout.write("  Exemple de commande effacée (récupérable) créé.")

