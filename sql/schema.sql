-- ============================================================
--  IFRI_MentorLink — Schéma PostgreSQL final (v2)
--  Base de données fraîche — exécuter une seule fois.
-- ============================================================

-- ── RÉFÉRENTIEL DES MATIÈRES ──────────────────────────────────
-- Table normalisée : évite les doublons de chaîne dans les autres tables.

CREATE TABLE IF NOT EXISTS matieres (
    id   SERIAL PRIMARY KEY,
    nom  VARCHAR(100) UNIQUE NOT NULL
);

INSERT INTO matieres (nom) VALUES
    ('Programmation Python'),
    ('Algorithmique'),
    ('Bases de données'),
    ('SQL'),
    ('Développement web'),
    ('HTML/CSS'),
    ('Java'),
    ('POO'),
    ('Mathématiques'),
    ('Statistiques'),
    ('Réseaux'),
    ('Anglais');

-- ── MODULE 1 : GESTION DES COMPTES ET PROFILS ─────────────────

CREATE TABLE IF NOT EXISTS users (
    id                  SERIAL PRIMARY KEY,
    nom                 VARCHAR(100) NOT NULL,
    prenom              VARCHAR(100) NOT NULL,
    email               VARCHAR(150) UNIQUE NOT NULL,
    telephone           VARCHAR(20)  UNIQUE NOT NULL,
    mot_de_passe        VARCHAR(255) NOT NULL,        -- hash bcrypt
    filiere             VARCHAR(50),
    niveau              VARCHAR(20),
    bio                 TEXT,
    photo_profil        VARCHAR(255),
    -- Refresh token (renouvellement silencieux du JWT)
    refresh_token       VARCHAR(500),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Forces ET lacunes d'un utilisateur par matière
-- type = 'force'  → matière maîtrisée (peut mentorer)
-- type = 'lacune' → matière où l'utilisateur a besoin d'aide
CREATE TABLE IF NOT EXISTS competences (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    matiere_id      INT NOT NULL REFERENCES matieres(id),
    type            VARCHAR(10) NOT NULL CHECK (type IN ('force', 'lacune')),
    UNIQUE (utilisateur_id, matiere_id)
);

-- Créneaux de disponibilité habituels (normalisés, pas stockés en JSON)
CREATE TABLE IF NOT EXISTS disponibilites (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    jour            VARCHAR(20) NOT NULL,
    heure_debut     TIME NOT NULL,
    heure_fin       TIME NOT NULL
);

-- Réinitialisation du mot de passe (token à usage unique, 1h de validité)
CREATE TABLE IF NOT EXISTS reinitialisations_mdp (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token           VARCHAR(255) UNIQUE NOT NULL,
    expire_a        TIMESTAMP NOT NULL,
    utilise         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── MODULE 2 : MISE EN CORRESPONDANCE ─────────────────────────

-- Offres de mentorat : "je propose de l'aide sur cette matière"
CREATE TABLE IF NOT EXISTS offres_mentorat (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    matiere_id      INT NOT NULL REFERENCES matieres(id),
    description     TEXT,
    format          VARCHAR(20) CHECK (format IN ('presentiel', 'en_ligne', 'les_deux')),
    -- Statut du cycle de vie de l'offre
    statut          VARCHAR(20) NOT NULL DEFAULT 'ouverte'
                    CHECK (statut IN ('ouverte', 'en_cours', 'cloturee')),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Demandes de mentorat : "je cherche de l'aide sur cette matière"
CREATE TABLE IF NOT EXISTS demandes_mentorat (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    matiere_id      INT NOT NULL REFERENCES matieres(id),
    description     TEXT,
    format          VARCHAR(20) CHECK (format IN ('presentiel', 'en_ligne', 'les_deux')),
    statut          VARCHAR(20) NOT NULL DEFAULT 'ouverte'
                    CHECK (statut IN ('ouverte', 'en_cours', 'cloturee')),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Réponses à une offre OU à une demande (jamais les deux simultanément)
-- La contrainte CHECK garantit l'exclusivité via XOR booléen.
CREATE TABLE IF NOT EXISTS reponses (
    id              SERIAL PRIMARY KEY,
    offre_id        INT REFERENCES offres_mentorat(id)   ON DELETE CASCADE,
    demande_id      INT REFERENCES demandes_mentorat(id) ON DELETE CASCADE,
    utilisateur_id  INT NOT NULL REFERENCES users(id)    ON DELETE CASCADE,
    message         TEXT,
    statut          VARCHAR(20) NOT NULL DEFAULT 'en_attente'
                    CHECK (statut IN ('en_attente', 'accepte', 'refuse')),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Un utilisateur répond une seule fois à une même offre
    UNIQUE (offre_id, utilisateur_id),
    -- Un utilisateur répond une seule fois à une même demande
    UNIQUE (demande_id, utilisateur_id),
    -- Exactement l'un des deux doit être renseigné (XOR)
    CHECK ((offre_id IS NOT NULL) <> (demande_id IS NOT NULL))
);

-- Résultats de l'algorithme de matching (paires mentor ↔ mentoré + score)
CREATE TABLE IF NOT EXISTS matchings (
    id          SERIAL PRIMARY KEY,
    mentor_id   INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mentore_id  INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score       FLOAT NOT NULL CHECK (score BETWEEN 0 AND 100),
    statut      VARCHAR(20) NOT NULL DEFAULT 'en_attente'
                CHECK (statut IN ('en_attente', 'accepte', 'refuse')),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Un matching unique par paire
    UNIQUE (mentor_id, mentore_id)
);

-- ── MODULE 3 : MESSAGERIE ─────────────────────────────────────

CREATE TABLE IF NOT EXISTS conversations (
    id          SERIAL PRIMARY KEY,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table de liaison : qui participe à quelle conversation
CREATE TABLE IF NOT EXISTS participants_conversation (
    id               SERIAL PRIMARY KEY,
    conversation_id  INT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    utilisateur_id   INT NOT NULL REFERENCES users(id)         ON DELETE CASCADE,
    UNIQUE (conversation_id, utilisateur_id)
);

-- Messages textuels avec marqueur lu/non-lu
CREATE TABLE IF NOT EXISTS messages (
    id               SERIAL PRIMARY KEY,
    conversation_id  INT  NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    expediteur_id    INT  NOT NULL REFERENCES users(id)         ON DELETE CASCADE,
    contenu          TEXT NOT NULL,
    lu               BOOLEAN   DEFAULT FALSE,
    envoye_a         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── NOTIFICATIONS PERSISTANTES ────────────────────────────────
-- Stockées en base même quand l'utilisateur est déconnecté.
-- type : 'message' | 'reponse' | 'matching'

CREATE TABLE IF NOT EXISTS notifications (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type            VARCHAR(30) NOT NULL
                    CHECK (type IN ('message', 'reponse', 'matching')),
    contenu         TEXT NOT NULL,
    reference_id    INT,          -- ID de la ressource liée (conversation, offre…)
    lu              BOOLEAN   DEFAULT FALSE,
    cree_a          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── INDEX ─────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_competences_utilisateur    ON competences(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_disponibilites_utilisateur ON disponibilites(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_offres_matiere             ON offres_mentorat(matiere_id);
CREATE INDEX IF NOT EXISTS idx_offres_statut              ON offres_mentorat(statut);
CREATE INDEX IF NOT EXISTS idx_demandes_matiere           ON demandes_mentorat(matiere_id);
CREATE INDEX IF NOT EXISTS idx_demandes_statut            ON demandes_mentorat(statut);
CREATE INDEX IF NOT EXISTS idx_reponses_offre             ON reponses(offre_id);
CREATE INDEX IF NOT EXISTS idx_reponses_demande           ON reponses(demande_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation      ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_lu                ON messages(lu);
CREATE INDEX IF NOT EXISTS idx_notifications_utilisateur  ON notifications(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_notifications_lu           ON notifications(lu);
CREATE INDEX IF NOT EXISTS idx_matchings_mentor           ON matchings(mentor_id);
CREATE INDEX IF NOT EXISTS idx_matchings_mentore          ON matchings(mentore_id);
