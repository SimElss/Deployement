# Explications de l'application
Dans le cadre d’un recrutement, l’application permettra aux postulants de savoir en temps réel où en est leur candidature. Idéalement, le candidat devrait pouvoir choisir la langue (Français / Anglais).

L’application doit être accessible, avec login et mot de passe par le candidat, le secrétariat du Doyen et les membres de la Commission de recrutement.

Chacun des intervenants peut modifier/corriger/ajouter des informations. Dans ce cas, une notification doit être envoyée à chaque intervenant.

Les informations recueillies dans l’application devront être transférables dans un fichier excel ou word.

La confidentialité des données encodées dans l’application doit être strictement respectée.

---

## Routes

### Authentification
- **`GET /fr/login`** : Affiche la page de connexion en français.
- **`POST /fr/login`** : Gère la soumission du formulaire de connexion.
- **`POST /fr/logout`** : Déconnecte l'utilisateur.
- **`GET /fr/register`** : Affiche la page d'inscription.
- **`POST /fr/register`** : Gère la soumission du formulaire d'inscription.
- **`GET /en/login`** : Affiche la page de connexion en anglais.
- **`POST /en/login`** : Gère la soumission du formulaire de connexion en anglais.
- **`POST /en/logout`** : Déconnecte l'utilisateur en anglais.
- **`GET /en/register`** : Affiche la page d'inscription en anglais.
- **`POST /en/register`** : Gère la soumission du formulaire d'inscription en anglais.

### Gestion des dossiers
- **`GET /fr/dossier/{id}`** : Affiche les détails d'un dossier spécifique en français.
- **`POST /fr/dossier/new/add`** : Ajoute un nouveau dossier en français.
- **`GET /fr/modify_detail/{id}`** : Affiche la page pour modifier les détails d'un dossier en français.
- **`POST /fr/modify_detail/{id}`** : Gère la modification des détails d'un dossier en français.
- **`GET /fr/edit_dossier/{id}`** : Affiche la page pour modifier les informations personnelles d'un dossier en français.
- **`POST /fr/edit_dossier/{id}`** : Gère la modification des informations personnelles d'un dossier en français.
- **`GET /en/dossier/{id}`** : Affiche les détails d'un dossier spécifique en anglais.
- **`POST /en/dossier/new/add`** : Ajoute un nouveau dossier en anglais.
- **`GET /en/modify_detail/{id}`** : Affiche la page pour modifier les détails d'un dossier en anglais.
- **`POST /en/modify_detail/{id}`** : Gère la modification des détails d'un dossier en anglais.
- **`GET /en/edit_dossier/{id}`** : Affiche la page pour modifier les informations personnelles d'un dossier en anglais.
- **`POST /en/edit_dossier/{id}`** : Gère la modification des informations personnelles d'un dossier en anglais.

### Gestion des utilisateurs
- **`GET /fr/new_mdp`** : Affiche la page de réinitialisation du mot de passe en français.
- **`POST /fr/new_mdp`** : Gère la soumission du formulaire de réinitialisation du mot de passe en français.
- **`GET /en/new_mdp`** : Affiche la page de réinitialisation du mot de passe en anglais.
- **`POST /en/new_mdp`** : Gère la soumission du formulaire de réinitialisation du mot de passe en anglais.

### Notifications et erreurs
- **`GET /fr/error/{description}/{url}`** : Affiche une page d'erreur avec une description et un lien de redirection en français.
- **`GET /en/error/{description}/{url}`** : Affiche une page d'erreur avec une description et un lien de redirection en anglais.

### Langues
- **`GET /fr/switch_to_en`** : Redirige vers la version anglaise du site.
- **`GET /en/switch_to_fr`** : Redirige vers la version française du site.

---

## Installation en ligne de commande

-Créer l'environnement virtuel : python -m venv ./my-env

### Activer l'environnement

### Sous Linux et MacOS :

source ./my-env/bin/activate

### Sous Windows :

./my-env/Scripts/activate

### Installer les librairies

pip install -r requirements.txt

### Démarrer l'application

python main.py