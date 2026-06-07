
CREATE TABLE utilisateurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    telephone VARCHAR(20),
    mot_de_passe_hashe TEXT NOT NULL,
    filiere VARCHAR(100),
    niveau VARCHAR(50),
    bio TEXT,
    photo TEXT
);

CREATE TABLE competences (
    id SERIAL PRIMARY KEY,
    utilisateur_id INTEGER REFERENCES utilisateurs(id) ON DELETE CASCADE,
    matiere VARCHAR(100) NOT NULL,
    type VARCHAR(10) CHECK (type IN ('force', 'lacune')) NOT NULL
);

CREATE TABLE disponibilites (
    id SERIAL PRIMARY KEY,
    utilisateur_id INTEGER REFERENCES utilisateurs(id) ON DELETE CASCADE,
    creneau TEXT NOT NULL -- Exemple: "Lundi 14h-16h"
);

CREATE TABLE offres_mentorat (
    id SERIAL PRIMARY KEY,
    utilisateur_id INTEGER REFERENCES utilisateurs(id) ON DELETE CASCADE,
    matiere VARCHAR(100) NOT NULL,
    format VARCHAR(20) CHECK (format IN ('présentiel', 'en ligne', 'les deux')) NOT NULL
);

CREATE TABLE demandes_mentorat (
    id SERIAL PRIMARY KEY,
    utilisateur_id INTEGER REFERENCES utilisateurs(id) ON DELETE CASCADE,
    matiere VARCHAR(100) NOT NULL
);

CREATE TABLE reponses (
    id SERIAL PRIMARY KEY,
    utilisateur_id INTEGER REFERENCES utilisateurs(id) ON DELETE CASCADE,
    offre_id INTEGER REFERENCES offres_mentorat(id),
    demande_id INTEGER REFERENCES demandes_mentorat(id),
    statut VARCHAR(20) DEFAULT 'en_attente' CHECK (statut IN ('en_attente', 'accepte', 'refuse'))
);

CREATE TABLE matchings (
    id SERIAL PRIMARY KEY,
    mentor_id INTEGER REFERENCES utilisateurs(id) ON DELETE CASCADE,
    mentore_id INTEGER REFERENCES utilisateurs(id) ON DELETE CASCADE,
    score NUMERIC(5,2), -- Score de compatibilité
    date_match TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    matching_id INTEGER REFERENCES matchings(id) ON DELETE SET NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE participants_conversation (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    utilisateur_id INTEGER REFERENCES utilisateurs(id) ON DELETE CASCADE
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    expediteur_id INTEGER REFERENCES utilisateurs(id) ON DELETE SET NULL,
    texte TEXT NOT NULL,
    date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);