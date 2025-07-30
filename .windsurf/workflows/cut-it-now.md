---
description: application de découpe vidéo (Python + GUI)
---

🧩 Objectif
Créer une application Python simple avec une interface graphique (Tkinter ou PyQt), qui permet :

de sélectionner une vidéo locale,

de choisir en combien de parties égales la découper,

de lancer la découpe,

le tout compilable en .exe sans dépendances externes visibles (FFmpeg intégré).

Glisser-déposer de la vidéo

Support d’autres formats

Choix de la qualité ou du codec

Option de découper selon la taille (Mo) ou la durée (minutes)

🛠️ Fonctionnalités
Interface graphique

Bouton pour sélectionner une vidéo locale (.mp4, .mov, etc.).

Champ ou slider pour choisir le nombre de parties à générer.

Bouton "Lancer la découpe".

Affichage de l’avancement et messages de succès ou d’erreur.

Découpe de la vidéo

Utilisation de FFmpeg pour découper la vidéo en n parties de durée égale.

Gestion propre des noms des fichiers de sortie.

Encapsulation de FFmpeg

FFmpeg inclus dans le dossier de l’application, appelé en subprocess sans installation système.

Compatible avec la compilation vers .exe (PyInstaller ou cx_Freeze).

🧱 Structure des fichiers
plaintext
Copier
Modifier
video_cutter/
├── assets/
│   └── ffmpeg.exe         # FFmpeg binaire encapsulé
├── main.py                # Script principal avec GUI
├── utils.py               # Fonctions d'aide (temps, découpe, etc.)
├── requirements.txt       # Dépendances (minimales)
├── README.md              # Instructions
└── plan.md                # Ce fichier
🧑‍💻 Technologies
Python 3.10+

Tkinter (ou PyQt5 si design plus poussé)

FFmpeg (local, via subprocess)

PyInstaller (ou cx_Freeze) pour création de .exe standalone

🚧 Étapes de développement
1. Interface utilisateur (Tkinter)
filedialog pour choisir une vidéo

Entry ou Spinbox pour nombre de parties

Button pour découper

Label pour messages d’état

2. Fonction de découpe
Lire la durée de la vidéo (ffmpeg -i)

Calculer la durée de chaque segment

Boucle pour lancer autant de commandes ffmpeg que de segments

3. Gestion des fichiers
Création d’un sous-dossier de sortie

Nommage des fichiers : video_part_1.mp4, video_part_2.mp4, etc.

4. Intégration FFmpeg
Placer ffmpeg.exe dans assets/

Utiliser subprocess avec le chemin local

Ne pas dépendre de l’installation globale de FFmpeg

5. Compilation .exe
Ajouter un fichier .spec pour PyInstaller

Inclure ffmpeg.exe comme fichier binaire

Vérifier que l'exe fonctionne sans Python ni FFmpeg installés

🧪 Exemple de ligne de commande FFmpeg
bash
Copier
Modifier
ffmpeg -i input.mp4 -ss [start_time] -t [duration] -c copy output_part_X.mp4
📦 Compilation en .exe (PyInstaller)
Commande :

bash
Copier
Modifier
pyinstaller --onefile --add-binary "assets/ffmpeg.exe;assets" main.py

