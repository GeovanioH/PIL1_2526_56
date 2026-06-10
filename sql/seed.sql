-- =====================================================================
--  Données de test IFRI_MentorLink
-- =====================================================================

-- ---------- Utilisateurs ----------
INSERT INTO utilisateurs (nom, prenom, email, telephone, mot_de_passe, filiere, niveau, bio) VALUES
  ('Dolapé',     'Christ',  'christ.dolape@mentorlink.bj',  '0190000001', '$2b$12$FAKEhashChrist000000000000000000000000000000', 'GL',  'Licence 2', 'Passionné de dev web, j''aide sur Python.'),
  ('Koffi',      'Aristide','aristide.koffi@mentorlink.bj', '0190000002', '$2b$12$FAKEhashArist0000000000000000000000000000000', 'GL',  'Licence 3', 'Mentor en algorithmique et Python.'),
  ('Adjovi',     'Fatima',  'fatima.adjovi@mentorlink.bj',  '0190000003', '$2b$12$FAKEhashFatima000000000000000000000000000000', 'IA',  'Licence 3', 'J''adore les bases de données et le SQL.'),
  ('Hounkpatin', 'Samuel',  'samuel.h@mentorlink.bj',       '0190000004', '$2b$12$FAKEhashSamuel000000000000000000000000000000', 'SI',  'Licence 2', 'Dév web front-end.'),
  ('Gbaguidi',   'Marina',  'marina.g@mentorlink.bj',       '0190000005', '$2b$12$FAKEhashMarina000000000000000000000000000000', 'IM',  'Licence 2', 'Forte en mathématiques.');

-- ---------- Compétences (forces / lacunes) ----------
-- Christ (1) : forces Python, Algo, HTML/CSS ; lacunes SQL, BD
INSERT INTO competences (utilisateur_id, matiere_id, type) VALUES
  (1, 1, 'force'), (1, 2, 'force'), (1, 6, 'force'),
  (1, 4, 'lacune'), (1, 3, 'lacune'),
  -- Aristide (2) : forces Python, Algo
  (2, 1, 'force'), (2, 2, 'force'),
  -- Fatima (3) : forces BD, SQL
  (3, 3, 'force'), (3, 4, 'force'),
  -- Samuel (4) : forces Dév web, HTML/CSS ; lacune Algo
  (4, 5, 'force'), (4, 6, 'force'), (4, 2, 'lacune'),
  -- Marina (5) : force Maths ; lacune Python
  (5, 9, 'force'), (5, 1, 'lacune');

-- ---------- Disponibilités ----------
INSERT INTO disponibilites (utilisateur_id, jour, heure_debut, heure_fin) VALUES
  (1, 'Lundi',    '14:00', '16:00'),
  (1, 'Mercredi', '10:00', '12:00'),
  (2, 'Lundi',    '14:00', '16:00'),
  (2, 'Mercredi', '14:00', '16:00'),
  (3, 'Mardi',    '10:00', '12:00');

-- ---------- Offres & demandes ----------
INSERT INTO offres_mentorat (utilisateur_id, matiere_id, format) VALUES
  (2, 1, 'les_deux'),   -- Aristide propose Python
  (3, 4, 'en_ligne');   -- Fatima propose SQL

INSERT INTO demandes_mentorat (utilisateur_id, matiere_id, format) VALUES
  (1, 4, 'en_ligne'),   -- Christ cherche de l'aide en SQL
  (1, 3, 'les_deux');   -- Christ cherche de l'aide en BD

-- ---------- Réponses ----------
INSERT INTO reponses (offre_id, demande_id, utilisateur_id, statut) VALUES
  (NULL, 1, 3, 'accepte');   -- Fatima répond à la demande SQL de Christ

-- ---------- Matchings (résultats de l'algorithme) ----------
INSERT INTO matchings (mentor_id, mentore_id, score, statut) VALUES
  (2, 1, 0.94, 'en_attente'),   -- Aristide <-> Christ
  (3, 1, 0.88, 'accepte'),      -- Fatima  <-> Christ
  (4, 1, 0.76, 'en_attente');   -- Samuel  <-> Christ

-- ---------- Messagerie ----------
INSERT INTO conversations DEFAULT VALUES;          -- conversation 1 (Christ & Aristide)
INSERT INTO participants_conversation (conversation_id, utilisateur_id) VALUES
  (1, 1), (1, 2);

INSERT INTO messages (conversation_id, expediteur_id, contenu, lu, envoye_a) VALUES
  (1, 2, 'Salut Christ ! J''ai vu ta demande pour Python.', TRUE,  CURRENT_TIMESTAMP - INTERVAL '20 minutes'),
  (1, 1, 'Salut Aristide ! Oui, je galère sur les fonctions.', TRUE, CURRENT_TIMESTAMP - INTERVAL '18 minutes'),
  (1, 2, 'Pas de souci, on fait une session mercredi 14h ?', FALSE, CURRENT_TIMESTAMP - INTERVAL '2 minutes');

-- ---------- Notifications ----------
INSERT INTO notifications (utilisateur_id, type, contenu, lu) VALUES
  (1, 'message',  'Nouveau message d''Aristide Koffi', FALSE),
  (1, 'matching', 'Nouveau mentor compatible : Fatima Adjovi (88%)', FALSE);
