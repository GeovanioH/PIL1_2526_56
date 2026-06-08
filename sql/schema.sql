
--  Base de données IFRI_MentorLink (PostgreSQL)

CREATE TABLE IF NOT EXISTS  matieres (
    id  SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL
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

--  MODULE 1:Gestion des comptes et profils

-- Table centrale : un utilisateur de l'application
CREATE TABLE IF NOT EXISTS    users (
    id            SERIAL PRIMARY KEY,
    nom           VARCHAR(100) NOT NULL,
    prenom        VARCHAR(100) NOT NULL,
    email         VARCHAR(150) UNIQUE NOT NULL,
    telephone     VARCHAR(20)  UNIQUE NOT NULL,
    mot_de_passe  VARCHAR(255) NOT NULL,          
    filiere       VARCHAR(50),
    niveau        VARCHAR(20),
    bio           TEXT,
    photo_profil  VARCHAR(255),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Forces ET lacunes 
-- type = 'force': matière que je maîtrise
-- type = 'lacune': matière où l'utilisateur a besoin d'aide
CREATE TABLE IF NOT EXISTS  competences (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INT NOT NULL REFERENCES   users(id) ON DELETE CASCADE,
    matiere_id      INT NOT NULL REFERENCES matieres(id),
    type            VARCHAR(10) NOT NULL CHECK (type IN ('force', 'lacune')),
    UNIQUE (utilisateur_id, matiere_id)  
);

-- Créneaux de disponibilité habituels
CREATE TABLE IF NOT EXISTS  disponibilites (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INT NOT NULL REFERENCES   users(id) ON DELETE CASCADE,
    jour            VARCHAR(20) NOT NULL,
    heure_debut     TIME NOT NULL,
    heure_fin       TIME NOT NULL
);

-- Réinitialisation du mot de passe
CREATE TABLE IF NOT EXISTS  reinitialisations_mdp (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INT NOT NULL REFERENCES   users(id) ON DELETE CASCADE,
    token           VARCHAR(255) NOT NULL,
    expire_a        TIMESTAMP NOT NULL,
    utilise         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--  MODULE 2: la Mise en correspondance (matching)

-- Offres de mentorat (j'aide sur une matiere)
CREATE TABLE IF NOT EXISTS  offres_mentorat (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INT NOT NULL REFERENCES   users(id) ON DELETE CASCADE,
    matiere_id      INT NOT NULL REFERENCES matieres(id),
    format          VARCHAR(20) CHECK (format IN ('presentiel', 'en_ligne', 'les_deux')),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Demandes de mentorat (je cherche de l'aide sur une matière)
CREATE TABLE IF NOT EXISTS  demandes_mentorat (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INT NOT NULL REFERENCES   users(id) ON DELETE CASCADE,
    matiere_id      INT NOT NULL REFERENCES matieres(id),
    format          VARCHAR(20) CHECK (format IN ('presentiel', 'en_ligne', 'les_deux')),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Réponses à une offre OU à une demande (pas les deux en meme temps)
CREATE TABLE IF NOT EXISTS  reponses (
    id              SERIAL PRIMARY KEY,
    offre_id        INT REFERENCES offres_mentorat(id)   ON DELETE CASCADE,
    demande_id      INT REFERENCES demandes_mentorat(id) ON DELETE CASCADE,
    utilisateur_id  INT NOT NULL REFERENCES   users(id) ON DELETE CASCADE,
    statut          VARCHAR(20) DEFAULT 'en_attente' CHECK (statut IN ('en_attente', 'accepte', 'refuse')),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK ((offre_id IS NOT NULL) <> (demande_id IS NOT NULL))  -- l'un ou l'autre, pas les deux
);

-- Résultats de l'algorithme de matching (paires + score)
CREATE TABLE IF NOT EXISTS  matchings (
    id          SERIAL PRIMARY KEY,
    mentor_id   INT NOT NULL REFERENCES   users(id) ON DELETE CASCADE,
    mentore_id  INT NOT NULL REFERENCES   users(id) ON DELETE CASCADE,
    score       FLOAT NOT NULL,
    statut      VARCHAR(20) DEFAULT 'en_attente' CHECK (statut IN ('en_attente', 'accepte', 'refuse')),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



--  MODULE 3: gestion de laMessagerie

CREATE TABLE IF NOT EXISTS  conversations (
    id          SERIAL PRIMARY KEY,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Qui participe à quelle conversation (un même user une seule fois)
CREATE TABLE IF NOT EXISTS  participants_conversation (
    id               SERIAL PRIMARY KEY,
    conversation_id  INT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    utilisateur_id   INT NOT NULL REFERENCES   users(id) ON DELETE CASCADE,
    UNIQUE (conversation_id, utilisateur_id)
);

-- Messages (avec statut lu/non-lu)
CREATE TABLE IF NOT EXISTS  messages (
    id               SERIAL PRIMARY KEY,
    conversation_id  INT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    expediteur_id    INT NOT NULL REFERENCES   users(id) ON DELETE CASCADE,
    contenu          TEXT NOT NULL,
    lu               BOOLEAN DEFAULT FALSE,
    envoye_a         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications 
CREATE TABLE IF NOT EXISTS  notifications (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INT NOT NULL REFERENCES   users(id) ON DELETE CASCADE,
    type            VARCHAR(30) CHECK (type IN ('message', 'reponse', 'matching')),
    contenu         TEXT,
    lu              BOOLEAN DEFAULT FALSE,
    cree_a          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index utiles

CREATE INDEX idx_competences_utilisateur ON competences(utilisateur_id);
CREATE INDEX idx_disponibilites_utilisateur ON disponibilites(utilisateur_id);
CREATE INDEX idx_offres_matiere ON offres_mentorat(matiere_id);
CREATE INDEX idx_demandes_matiere ON demandes_mentorat(matiere_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_notifications_utilisateur ON notifications(utilisateur_id);
