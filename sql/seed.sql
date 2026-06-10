-- ============================================================
--  IFRI_MentorLink — Données de test (seed)
--  À exécuter APRÈS schema.sql sur une base vide.
--
--  IDs matieres de référence :
--   1 Python | 2 Algorithmique | 3 Bases de données | 4 SQL
--   5 Dév web | 6 HTML/CSS | 7 Java | 8 POO
--   9 Mathématiques | 10 Statistiques | 11 Réseaux | 12 Anglais
-- ============================================================

-- ── UTILISATEURS ──────────────────────────────────────────────
-- Les hash bcrypt ci-dessous sont FACTICES (démo uniquement).
-- En production ils sont générés par l'API (passlib/bcrypt).

INSERT INTO users (nom, prenom, email, telephone, mot_de_passe, filiere, niveau, bio) VALUES
    ('Dolapé',     'Christ',   'christ.dolape@mentorlink.bj',  '0190000001',
     '$2b$12$FAKEhashChrist00000000000000000000000000000',
     'GL', 'Licence 2', 'Passionné de dev web, je propose de l''aide sur Python et Algo.'),

    ('Koffi',      'Aristide', 'aristide.koffi@mentorlink.bj', '0190000002',
     '$2b$12$FAKEhashAristide000000000000000000000000000',
     'GL', 'Licence 3', 'Mentor confirmé en Algorithmique et Python.'),

    ('Adjovi',     'Fatima',   'fatima.adjovi@mentorlink.bj',  '0190000003',
     '$2b$12$FAKEhashFatima0000000000000000000000000000',
     'IA', 'Licence 3', 'Spécialiste bases de données et SQL.'),

    ('Hounkpatin', 'Samuel',   'samuel.h@mentorlink.bj',       '0190000004',
     '$2b$12$FAKEhashSamuel0000000000000000000000000000',
     'SI', 'Licence 2', 'Développeur front-end, fort en HTML/CSS et JS.'),

    ('Gbaguidi',   'Marina',   'marina.g@mentorlink.bj',       '0190000005',
     '$2b$12$FAKEhashMarina0000000000000000000000000000',
     'IM', 'Licence 2', 'Forte en mathématiques, cherche de l''aide en Python.');

-- ── COMPÉTENCES (forces / lacunes) ────────────────────────────

INSERT INTO competences (utilisateur_id, matiere_id, type) VALUES
    -- Christ (1) : forces Python, Algo, HTML/CSS ; lacunes SQL, BD
    (1, 1, 'force'),
    (1, 2, 'force'),
    (1, 6, 'force'),
    (1, 4, 'lacune'),
    (1, 3, 'lacune'),

    -- Aristide (2) : forces Python, Algorithmique
    (2, 1, 'force'),
    (2, 2, 'force'),

    -- Fatima (3) : forces BD, SQL
    (3, 3, 'force'),
    (3, 4, 'force'),

    -- Samuel (4) : forces Dév web, HTML/CSS ; lacune Algorithmique
    (4, 5, 'force'),
    (4, 6, 'force'),
    (4, 2, 'lacune'),

    -- Marina (5) : force Mathématiques ; lacune Python
    (5, 9, 'force'),
    (5, 1, 'lacune');

-- ── DISPONIBILITÉS ────────────────────────────────────────────

INSERT INTO disponibilites (utilisateur_id, jour, heure_debut, heure_fin) VALUES
    (1, 'Lundi',    '14:00', '16:00'),
    (1, 'Mercredi', '10:00', '12:00'),
    (2, 'Lundi',    '14:00', '16:00'),
    (2, 'Mercredi', '14:00', '16:00'),
    (3, 'Mardi',    '10:00', '12:00'),
    (4, 'Jeudi',    '08:00', '10:00'),
    (5, 'Vendredi', '15:00', '17:00');

-- ── OFFRES DE MENTORAT ────────────────────────────────────────

INSERT INTO offres_mentorat (utilisateur_id, matiere_id, description, format, statut) VALUES
    -- Aristide propose de l'aide en Python
    (2, 1, 'Je peux aider sur les fonctions, listes, POO en Python.', 'les_deux', 'ouverte'),
    -- Fatima propose de l'aide en SQL
    (3, 4, 'Requêtes SELECT, jointures, sous-requêtes, optimisation.', 'en_ligne', 'ouverte'),
    -- Fatima propose aussi en BD
    (3, 3, 'Modélisation relationnelle, normalisation, MCD/MLD.', 'les_deux', 'ouverte');

-- ── DEMANDES DE MENTORAT ──────────────────────────────────────

INSERT INTO demandes_mentorat (utilisateur_id, matiere_id, description, format, statut) VALUES
    -- Christ cherche de l'aide en SQL
    (1, 4, 'Je galère sur les jointures et les agrégations.', 'en_ligne', 'ouverte'),
    -- Christ cherche aussi de l'aide en BD
    (1, 3, 'Besoin d''aide pour la normalisation (1NF, 2NF, 3NF).', 'les_deux', 'ouverte'),
    -- Samuel cherche de l'aide en Algorithmique
    (4, 2, 'Tri, récursivité, complexité — j''ai besoin d''un mentor.', 'presentiel', 'ouverte');

-- ── RÉPONSES ──────────────────────────────────────────────────
-- Fatima répond à la demande SQL de Christ (demande_id = 1)
INSERT INTO reponses (offre_id, demande_id, utilisateur_id, message, statut) VALUES
    (NULL, 1, 3, 'Je peux t''aider ! Je suis dispo mardi matin.', 'accepte');

-- Aristide répond à la demande SQL de Christ (offre_id = 1 = son offre Python)
-- (il répond via son offre Python à la demande SQL de Christ — offre ciblant ses lacunes algo)
INSERT INTO reponses (offre_id, demande_id, utilisateur_id, message, statut) VALUES
    (NULL, 3, 2, 'Je t''aide en Algo, disponible lundi 14h.', 'en_attente');

-- ── MATCHINGS (résultats de l'algorithme) ─────────────────────

INSERT INTO matchings (mentor_id, mentore_id, score, statut) VALUES
    (2, 1, 94.0, 'en_attente'),   -- Aristide ↔ Christ  (Python/Algo vs lacunes Python/Algo)
    (3, 1, 88.0, 'accepte'),      -- Fatima   ↔ Christ  (SQL/BD vs lacunes SQL/BD)
    (3, 4, 72.0, 'en_attente');   -- Fatima   ↔ Samuel  (BD/SQL, dispo partielle)

-- ── MESSAGERIE ────────────────────────────────────────────────

-- Conversation 1 : Christ (1) & Aristide (2)
INSERT INTO conversations DEFAULT VALUES;

INSERT INTO participants_conversation (conversation_id, utilisateur_id) VALUES
    (1, 1),
    (1, 2);

INSERT INTO messages (conversation_id, expediteur_id, contenu, lu, envoye_a) VALUES
    (1, 2, 'Salut Christ ! J''ai vu ta demande, je peux t''aider en Python.',
     TRUE,  CURRENT_TIMESTAMP - INTERVAL '20 minutes'),
    (1, 1, 'Super Aristide ! J''ai du mal avec les fonctions récursives.',
     TRUE,  CURRENT_TIMESTAMP - INTERVAL '18 minutes'),
    (1, 2, 'Pas de souci, on fait une session mercredi à 14h ?',
     FALSE, CURRENT_TIMESTAMP - INTERVAL '2 minutes');

-- ── NOTIFICATIONS ─────────────────────────────────────────────

INSERT INTO notifications (utilisateur_id, type, contenu, reference_id, lu) VALUES
    (1, 'message',  'Nouveau message d''Aristide Koffi', 1,    FALSE),
    (1, 'reponse',  'Fatima Adjovi a répondu à votre demande SQL', 1, FALSE),
    (1, 'matching', 'Nouveau mentor compatible : Fatima Adjovi (88%)', NULL, FALSE),
    (2, 'reponse',  'Christ Dolapé a répondu à votre offre Python', 1, FALSE);
