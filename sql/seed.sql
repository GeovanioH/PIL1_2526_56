INSERT INTO utilisateurs (nom, prenom, email, telephone, mot_de_passe, filiere, niveau, bio) VALUES
('Agossou', 'Koffi', 'koffi.agossou@ifri.uac.bj', '+22961000001', '$2b$12$KIX1234567890abcdefghij', 'IA', 'Licence 1', 'Passionné par le machine learning.'),
('Dossou', 'Marlène', 'marlene.dossou@ifri.uac.bj', '+22961000002', '$2b$12$KIX1234567890abcdefghij', 'GL', 'Licence 2', 'Aime le développement web.'),
('Hounkpatin', 'Roméo', 'romeo.hounkpatin@ifri.uac.bj', '+22961000003', '$2b$12$KIX1234567890abcdefghij', 'SI', 'Licence 1', 'Intéressé par les bases de données.'),
('Gbèdji', 'Abigaël', 'abigael.gbedji@ifri.uac.bj', '+22961000004', '$2b$12$KIX1234567890abcdefghij', 'IM', 'Licence 2', 'Créative et passionnée de design.'),
('Sossou', 'Théodore', 'theodore.sossou@ifri.uac.bj', '+22961000005', '$2b$12$KIX1234567890abcdefghij', 'SE&IoT', 'Licence 1', 'Fan des systèmes embarqués.'),
('Ahouandjinou', 'Clarisse', 'clarisse.ahouandjinou@ifri.uac.bj', '+22961000006', '$2b$12$KIX1234567890abcdefghij', 'IA', 'Licence 2', 'Spécialisée en traitement de données.'),
('Loko', 'Fernand', 'fernand.loko@ifri.uac.bj', '+22961000007', '$2b$12$KIX1234567890abcdefghij', 'GL', 'Licence 1', 'Développeur backend motivé.'),
('Vigan', 'Précieuse', 'precieuse.vigan@ifri.uac.bj', '+22961000008', '$2b$12$KIX1234567890abcdefghij', 'SI', 'Licence 2', 'Intéressée par la sécurité informatique.'),
('Azonhiho', 'Patrick', 'patrick.azonhiho@ifri.uac.bj', '+22961000009', '$2b$12$KIX1234567890abcdefghij', 'IM', 'Licence 1', 'Passionné de multimédia.'),
('Zinsou', 'Déborah', 'deborah.zinsou@ifri.uac.bj', '+22961000010', '$2b$12$KIX1234567890abcdefghij', 'SE&IoT', 'Licence 2', 'Aime les projets IoT.'),
('Hounsou', 'Gilles', 'gilles.hounsou@ifri.uac.bj', '+22961000011', '$2b$12$KIX1234567890abcdefghij', 'IA', 'Licence 1', 'Curieux et rigoureux.'),
('Adéoti', 'Nadège', 'nadege.adeoti@ifri.uac.bj', '+22961000012', '$2b$12$KIX1234567890abcdefghij', 'GL', 'Licence 2', 'Aime le clean code.'),
('Tohoun', 'Wilfrid', 'wilfrid.tohoun@ifri.uac.bj', '+22961000013', '$2b$12$KIX1234567890abcdefghij', 'SI', 'Licence 1', 'Motivé par les réseaux.'),
('Akpovi', 'Laeticia', 'laeticia.akpovi@ifri.uac.bj', '+22961000014', '$2b$12$KIX1234567890abcdefghij', 'IM', 'Licence 2', 'Passionnée de communication digitale.'),
('Dègla', 'Bertin', 'bertin.degla@ifri.uac.bj', '+22961000015', '$2b$12$KIX1234567890abcdefghij', 'SE&IoT', 'Licence 1', 'Aime bidouiller les circuits.');

INSERT INTO competences (utilisateur_id, matiere, type) VALUES
(1, 'Python', 'force'),
(1, 'Algorithmique', 'force'),
(1, 'SQL', 'lacune'),
(2, 'Développement web', 'force'),
(2, 'SQL', 'force'),
(2, 'Python', 'lacune'),
(3, 'SQL', 'force'),
(3, 'Algorithmique', 'lacune'),
(4, 'Design UI/UX', 'force'),
(4, 'Python', 'lacune'),
(5, 'Électronique', 'force'),
(5, 'Développement web', 'lacune'),
(6, 'Python', 'force'),
(6, 'Machine Learning', 'force'),
(6, 'Développement web', 'lacune'),
(7, 'Développement web', 'force'),
(7, 'SQL', 'lacune'),
(8, 'Réseaux', 'force'),
(8, 'SQL', 'force'),
(9, 'Multimédia', 'force'),
(9, 'Algorithmique', 'lacune'),
(10, 'IoT', 'force'),
(10, 'Python', 'force'),
(11, 'Algorithmique', 'force'),
(11, 'Développement web', 'lacune'),
(12, 'Développement web', 'force'),
(12, 'Python', 'force'),
(13, 'Réseaux', 'force'),
(13, 'Python', 'lacune'),
(14, 'Design UI/UX', 'force'),
(14, 'SQL', 'lacune'),
(15, 'Électronique', 'force'),
(15, 'Algorithmique', 'lacune');

INSERT INTO disponibilites (utilisateur_id, jour, heure_debut, heure_fin) VALUES
(1, 'lundi', '14:00', '16:00'),
(1, 'mercredi', '10:00', '12:00'),
(2, 'mardi', '15:00', '17:00'),
(2, 'jeudi', '14:00', '16:00'),
(3, 'lundi', '16:00', '18:00'),
(4, 'mercredi', '14:00', '16:00'),
(5, 'vendredi', '10:00', '12:00'),
(6, 'lundi', '14:00', '16:00'),
(6, 'mardi', '10:00', '12:00'),
(7, 'jeudi', '16:00', '18:00'),
(8, 'mercredi', '08:00', '10:00'),
(9, 'vendredi', '14:00', '16:00'),
(10, 'lundi', '10:00', '12:00'),
(11, 'mardi', '14:00', '16:00'),
(12, 'mercredi', '16:00', '18:00'),
(13, 'jeudi', '10:00', '12:00'),
(14, 'vendredi', '08:00', '10:00'),
(15, 'lundi', '16:00', '18:00');

INSERT INTO offres_mentorat (utilisateur_id, matiere, format) VALUES
(1, 'Python', 'en_ligne'),
(2, 'Développement web', 'presentiel'),
(2, 'SQL', 'les_deux'),
(6, 'Python', 'en_ligne'),
(6, 'Machine Learning', 'en_ligne'),
(8, 'Réseaux', 'presentiel'),
(10, 'Python', 'les_deux'),
(12, 'Développement web', 'presentiel');

INSERT INTO demandes_mentorat (utilisateur_id, matiere, format) VALUES
(1, 'SQL', 'en_ligne'),
(3, 'Algorithmique', 'presentiel'),
(4, 'Python', 'en_ligne'),
(5, 'Développement web', 'les_deux'),
(7, 'SQL', 'presentiel'),
(9, 'Algorithmique', 'en_ligne'),
(11, 'Développement web', 'en_ligne'),
(13, 'Python', 'les_deux'),
(14, 'SQL', 'presentiel'),
(15, 'Algorithmique', 'en_ligne');

INSERT INTO matchings (mentor_id, mentore_id, score, statut) VALUES
(2, 1, 85.0, 'accepte'),
(1, 4, 78.5, 'en_attente'),
(6, 5, 72.0, 'accepte'),
(8, 7, 80.0, 'en_attente'),
(12, 11, 90.0, 'accepte');

INSERT INTO conversations DEFAULT VALUES;
INSERT INTO conversations DEFAULT VALUES;
INSERT INTO conversations DEFAULT VALUES;

INSERT INTO participants_conversation (conversation_id, utilisateur_id) VALUES
(1, 2), (1, 1),
(2, 6), (2, 5),
(3, 12), (3, 11);

INSERT INTO messages (conversation_id, expediteur_id, contenu) VALUES
(1, 2, 'Salut Koffi ! Je peux t''aider en SQL quand tu veux.'),
(1, 1, 'Super merci Marlène ! On peut commencer mercredi ?'),
(1, 2, 'Oui parfait, je suis dispo de 14h à 16h.'),
(2, 6, 'Bonjour Théodore, on peut travailler sur le développement web ensemble.'),
(2, 5, 'Merci Clarisse ! J''en ai vraiment besoin.'),
(3, 12, 'Gilles, je peux t''expliquer les bases du développement web.'),
(3, 11, 'Avec plaisir Nadège, merci beaucoup !');