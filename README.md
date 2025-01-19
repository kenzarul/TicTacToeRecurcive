<p align="center">
    <em>Le Tic-Tac-Toe Récursif est une variante avancée du jeu classique, où des sous-grilles sont imbriquées dans une grille principale.
        Ce projet sert pour le jeu multijoueur ou solo, fait avec Django.</em>
</p>

---

## TABLEAU DES MATIERS

- [Tableau des Matiers](#tableau-des-matiers)
- [Aperçu](#Aperçu)
  - [Page principale](#page-principale)
  - [Mode Multijoueur](#mode-multijoueur)
  - [Mode Solo](#mode-solo)
- [Comment jouer ?](#comment-jouer)
- [Installation de Dev](#installation-de-dev)
  - [Installation et Exécuter en local](#installation-et-exécuter-en-local)
- [Technologies utilisées](#Technologies-utilisées)

## Aperçu

<note>

**Remarque**: `Le jeu est encore en cours de développement, vous pourriez voir des bugs.`

</note>

### Page principale
Choisir entre le mode solo ou multijoueur

### Mode Multijoueur
Joueur contre autre joueur en ligne. 
Un joueur est capable de créer un mot de passe par aléatoire ou écrit par lui-même, 
créant une salle en ligne permettant à un autre joueur d'y joindre avec le même mot de passe.

### Mode Solo
Joueur contre IA avec choix de difficulté (débutant, intermédiaire, expert).


## Comment jouer?

### **Mode Solo**

1. Depuis la page principale, cliquez sur **"Single Player"**.  
2. Choisissez un niveau de difficulté :  
   - **Débutant** : L’IA joue de manière aléatoire avec quelques coups stratégiques.  
   - **Intermédiaire** : L’IA applique des stratégies basiques pour bloquer l’adversaire. 
   - **Expert** : L’IA utilise un algorithme avancé pour évaluer les meilleures options.
3. Commencez à jouer contre l'ordinateur.  

---

### **Mode Multijoueur**

1. Depuis la page principale, cliquez sur **"Multi Player"**.  
2. Si vous êtes l’hôte :  
   - Cliquez sur **"Créer un Code"** pour générer un code unique.  
   - Partagez ce code avec vos amis.  
3. Si vous rejoignez une partie :  
   - Entrez le code de la partie partagé par l’hôte dans le champ prévu à cet effet.  
   - Cliquez sur **"Rejoindre"** pour entrer dans le lobby d’attente.  
4. Une fois tous les joueurs dans le lobby, la partie commence automatiquement.  

---
## Installation de Dev

### Installation et Exécuter en local

1. **Créer un environnement virtuel** 
```
python -m venv venv_name
```
2. **Activer l’environnement virtuel** 
   - Sur Windows  
        ```
        venv_name\scripts\activate.bat
        ```
   - Sur Linux,Mac  
        ```
        source venv_name/bin/activate
        ```
3. **Installer les dépendances**
```
pip install -r requirements.txt

```
4. Configurer le fichier `.env`
   - Assurez-vous que le fichier .env contient les valeurs suivantes :
```
DJANGO_SETTINGS_MODULE=core.settings.dev
SECRET_KEY=votre_cle_secrete
```
5. Lancer le serveur Django
```
python manage.py runserver
```
6. Ouvrir le projet dans votre navigateur
Accédez à `localhost:8000`.

## Technologies utilisées

 - Python : Langage principal pour la logique du jeu et les fonctionnalités backend. 
 - Django : Framework web pour développer l’interface utilisateur.
 - GitHub : Pour la gestion du code source et pour assurer qu’on peut modifier des code sources en même temps.
 - Langage de programmation de web : HTML est utilisé pour la structure d'une page web, CSS pour le style et la mise en page, et JavaScript pour le scripting et l'interactivité sur le web.
 - Docker : Pour containeriser l’application et assurer la portabilité.
 - Base de données (SQL) : Stockage des données du jeu (scores, utilisateurs, logs).