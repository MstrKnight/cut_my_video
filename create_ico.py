#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour convertir un fichier PNG en fichier ICO avec plusieurs tailles
"""

from PIL import Image
import os

def create_ico_from_png(png_path, ico_path, sizes=[16, 24, 32, 48, 64, 128, 256]):
    """
    Convertit un fichier PNG en fichier ICO avec plusieurs tailles
    
    Args:
        png_path (str): Chemin vers le fichier PNG source
        ico_path (str): Chemin vers le fichier ICO à créer
        sizes (list): Liste des tailles d'icônes à inclure
    """
    img = Image.open(png_path)
    
    # Convertir en mode RGBA si ce n'est pas déjà le cas
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Créer des versions redimensionnées
    resized_images = []
    for size in sizes:
        resized = img.resize((size, size), Image.LANCZOS)
        resized_images.append(resized)
    
    # Sauvegarder en ICO avec toutes les tailles
    resized_images[0].save(
        ico_path, 
        format='ICO',
        sizes=[(img.width, img.height) for img in resized_images],
        append_images=resized_images[1:]
    )
    print(f"Fichier ICO créé avec succès: {ico_path}")
    print(f"Tailles incluses: {sizes}")

if __name__ == "__main__":
    # Chemins des fichiers source et destination
    png_path = os.path.join('assets', 'icon.png')
    ico_path = os.path.join('assets', 'icon.ico')
    
    create_ico_from_png(png_path, ico_path)
