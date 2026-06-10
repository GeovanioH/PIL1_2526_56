# IFRI_MentorLink

Plateforme web de **mentorat entre étudiants de l'IFRI**. Elle met en relation des mentors (étudiants forts dans une matière) et des mentorés (qui ont des lacunes), grâce à un **algorithme de matching**, un **tableau d'annonces** (offres / demandes) et une **messagerie en temps réel**.

---

## Technologies utilisées

| Côté | Techno |
|------|--------|
| **Backend** | Python · FastAPI · SQLAlchemy (ORM) |
| **Base de données** | PostgreSQL |
| **Frontend** | HTML · Tailwind CSS · JavaScript (Lucide pour les icônes) |
| **Authentification** | JWT (token) |
| **Temps réel** | WebSocket (messagerie) |

---

## Structure du projet

```
ifri_mentorlink/
├── backend/              # L'API 
│   ├── app/
│   │   ├── models/       # Les tables décrites en Python (SQLAlchemy)
│   │   ├── routers/      # Les routes de l'API (auth, users, offres…)
│   │   ├── schemas/      # Validation des données entrantes/sortantes
│   │   ├── services/     # Sécurité (JWT) + algorithme de matching
│   │   └── database.py   # Connexion à PostgreSQL
│   ├── main.py           # Point d'entrée : lance l'API + crée les tables
│   ├── requirements.txt  # Liste des bibliothèques Python à installer
│   └── .env.example      # Modèle de configuration (à copier en .env)
├── frontend/             # Le site web (les pages que l'utilisateur voit)
│   ├── index.html        # Accueil + inscription / connexion
│   ├── completer-profil.html
│   ├── dashboard.html
│   ├── matching.html     # Mentors compatibles
│   ├── offres.html       # Offres & demandes de mentorat
│   ├── profil.html
│   ├── chat.html         # Messagerie
│   └── assets/
│       ├── js/api.js     # Couche d'appel à l'API (token, fetch…)
│       └── img/          # Images, logo, icônes
└── docs/                 # Documents (architecture, guides…)
```

>  **Note importante :** les tables de la base ne sont **pas** créées avec un fichier `.sql`. Elles sont décrites en Python dans `backend/app/models/` et créées **automatiquement** au démarrage du serveur par SQLAlchemy .

---

## Prérequis

1. **[Python 3.11+](https://www.python.org/downloads/)**
2. **[PostgreSQL](https://www.postgresql.org/download/)** 
3. **[Git](https://git-scm.com/downloads)** — pour cloner le projet.

---

## Installation & lancement

### 1. Cloner le projet
```bash
git clone <url-du-dépôt-github>
cd ifri_mentorlink
```

### 2. Créer la base de données (une seule fois)
La base doit exister **avant** de lancer le backend. Deux options :

- **Avec pgAdmin** : clic droit sur *Databases* → *Create* → *Database…* → nom : `ifrimentorlink`.
- **En ligne de commande** :
  ```bash
  psql -U postgres -c "CREATE DATABASE ifrimentorlink;"
  ```

### 3. Configurer le backend
```bash
cd backend

# a) Installer les bibliothèques Python
python -m pip install -r requirements.txt

# b) Créer le fichier de configuration .env à partir du modèle
#    Windows :
copy .env.example .env
#    Mac/Linux :
#    cp .env.example .env
```
Puis **ouvrir `.env`** et l'adapter à votre PC :
```env
DATABASE_URL=postgresql+psycopg2://postgres:VOTRE_MOT_DE_PASSE@localhost:5432/ifrimentorlink
SECRET_KEY=une_cle_secrete_longue_et_aleatoire
ALGORITHM=HS256
```
> Le dernier mot après `/` (`ifrimentorlink`) **doit être identique** au nom de la base créée à l'étape 2. Et `VOTRE_MOT_DE_PASSE` est celui de PostgreSQL.

### 4. Lancer le backend (terminal n°1)
```bash
cd backend
python -m uvicorn main:app --reload
```
- L'API tourne sur **http://localhost:8000**
- Documentation interactive (Swagger) : **http://localhost:8000/docs**
- Au premier démarrage, les 9 tables sont créées automatiquement.

### 5. Lancer le frontend (terminal n°2)
```bash
cd frontend
python -m http.server 5500
```
- Ouvrir le site : **http://localhost:5500/index.html**

> Ouvrir le frontend via ce serveur (`http://localhost:5500`), **pas** en double-cliquant le fichier (`file://...`), sinon les appels à l'API peuvent être bloqués.

---
---

## Comptes de test

Vous pouvez créer ton propre compte via *Inscription*, ou utiliser ceux déjà en base (si tu pars de la même base) :

| Email | Mot de passe |
|-------|--------------|
| `christ@ifri.bj` | `motdepasse123` |
| `aristide@ifri.bj` | `motdepasse123` |

La connexion accepte l'**email OU le numéro de téléphone**.

---

##  Aperçu des routes de l'API

| Domaine | Routes principales |
|---------|--------------------|
| **Auth** | `POST /auth/register`, `POST /auth/login`, `/refresh`, `/logout`, `/forgot-password`, `/reset-password` |
| **Profil** | `GET /users/me`, `PUT /users/me`, `GET /users/{id}` |
| **Matching** | `GET /matching/` (mentors triés par score de compatibilité) |
| **Offres** | `GET/POST /offres/`, `PUT/DELETE /offres/{id}`, `POST /offres/{id}/repondre` |
| **Demandes** | `GET/POST /demandes/`, `PUT/DELETE /demandes/{id}`, `POST /demandes/{id}/repondre` |
| **Messagerie** | `GET/POST /conversations/`, `GET/POST /conversations/{id}/messages`, WebSocket `/conversations/ws/{id}?token=` |
| **Notifications** | `GET /users/me/notifications` |

 La liste complète et testable est sur **http://localhost:8000/docs**.

---

## Problèmes fréquents

| Message d'erreur | Cause | Solution |
|------------------|-------|----------|
| `database "..." does not exist` | base pas créée, ou nom ≠ `.env` | refaire `CREATE DATABASE` / corriger le nom dans `.env` |
| `password authentication failed` | mauvais mot de passe dans `.env` | mettre le bon mot de passe PostgreSQL |
| `ModuleNotFoundError` | dépendances non installées | `python -m pip install -r requirements.txt` |
| Le site s'ouvre mais reste vide / « Session expirée » | le backend n'est pas lancé | lancer aussi le terminal du backend (étape 4) |
| `psql : commande introuvable` | PostgreSQL pas dans le PATH | utiliser pgAdmin, ou le chemin complet vers `psql.exe` |

---


