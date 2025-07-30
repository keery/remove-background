#!/usr/bin/env python3
"""
Script pour enlever le background des images avec rembg
Supporte le traitement par lot et différents modèles
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional
import time

try:
    from rembg import bg, new_session
    from PIL import Image
    import numpy as np
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Installez les dépendances avec:")
    print("pip install rembg[gpu] pillow")
    print("ou")
    print("pip install rembg pillow")
    sys.exit(1)

class BackgroundRemover:
    """Classe pour gérer la suppression de background"""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    # Modèles disponibles avec leurs cas d'usage
    MODELS = {
        'u2net': 'Général - Bon équilibre qualité/vitesse',
        'u2net_human_seg': 'Optimisé pour les personnes',
        'u2net_cloth_seg': 'Optimisé pour les vêtements',
        'isnet-general-use': 'Général - Haute qualité',
        'birefnet-general': 'Général - Très haute qualité (plus lent)',
        'silueta': 'Personnes - Rapide'
    }
    
    def __init__(self, model_name: str = 'u2net'):
        """
        Initialise le removeur de background
        
        Args:
            model_name: Nom du modèle à utiliser
        """
        if model_name not in self.MODELS:
            print(f"⚠️  Modèle '{model_name}' non reconnu. Utilisation de 'u2net'")
            model_name = 'u2net'
        
        self.model_name = model_name
        print(f"🔧 Initialisation du modèle: {model_name}")
        print(f"   Description: {self.MODELS[model_name]}")
        
        try:
            self.session = new_session(model_name)
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation du modèle: {e}")
            print("Tentative avec le modèle par défaut...")
            self.session = new_session('u2net')
    
    def remove_background(self, input_path: str, output_path: str, 
                         add_white_bg: bool = False) -> bool:
        """
        Enlève le background d'une image
        
        Args:
            input_path: Chemin vers l'image d'entrée
            output_path: Chemin vers l'image de sortie
            add_white_bg: Ajouter un fond blanc au lieu de transparent
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            print(f"🔄 Traitement: {os.path.basename(input_path)}")
            
            # Ouvrir l'image
            with open(input_path, 'rb') as input_file:
                input_data = input_file.read()
            
            # Enlever le background
            output_data = bg.remove(input_data, session=self.session)
            
            # Si on veut un fond blanc
            if add_white_bg:
                # Convertir en PIL Image
                image = Image.open(io.BytesIO(output_data)).convert("RGBA")
                
                # Créer un fond blanc
                white_bg = Image.new("RGB", image.size, (255, 255, 255))
                white_bg.paste(image, mask=image.split()[-1])  # Utiliser le canal alpha comme masque
                
                # Sauvegarder en JPEG
                output_path = output_path.replace('.png', '.jpg')
                white_bg.save(output_path, 'JPEG', quality=95)
            else:
                # Sauvegarder directement (PNG avec transparence)
                with open(output_path, 'wb') as output_file:
                    output_file.write(output_data)
            
            print(f"✅ Sauvegardé: {os.path.basename(output_path)}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du traitement de {input_path}: {e}")
            return False
    
    def process_batch(self, input_dir: str, output_dir: str, 
                     add_white_bg: bool = False, 
                     overwrite: bool = False) -> dict:
        """
        Traite un dossier d'images
        
        Args:
            input_dir: Dossier d'entrée
            output_dir: Dossier de sortie
            add_white_bg: Ajouter un fond blanc
            overwrite: Écraser les fichiers existants
            
        Returns:
            dict: Statistiques du traitement
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            print(f"❌ Dossier d'entrée introuvable: {input_dir}")
            return {'success': 0, 'failed': 0, 'skipped': 0}
        
        # Créer le dossier de sortie
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Trouver toutes les images
        image_files = []
        for ext in self.SUPPORTED_FORMATS:
            image_files.extend(input_path.glob(f"*{ext}"))
            image_files.extend(input_path.glob(f"*{ext.upper()}"))
        
        if not image_files:
            print(f"❌ Aucune image trouvée dans {input_dir}")
            return {'success': 0, 'failed': 0, 'skipped': 0}
        
        print(f"📁 Trouvé {len(image_files)} image(s) à traiter")
        
        stats = {'success': 0, 'failed': 0, 'skipped': 0}
        start_time = time.time()
        
        for i, img_file in enumerate(image_files, 1):
            # Définir le nom de sortie
            if add_white_bg:
                output_file = output_path / f"{img_file.stem}_no_bg.jpg"
            else:
                output_file = output_path / f"{img_file.stem}_no_bg.png"
            
            # Vérifier si le fichier existe déjà
            if output_file.exists() and not overwrite:
                print(f"⏭️  Ignoré (existe déjà): {img_file.name}")
                stats['skipped'] += 1
                continue
            
            print(f"[{i}/{len(image_files)}] ", end="")
            
            # Traiter l'image
            if self.remove_background(str(img_file), str(output_file), add_white_bg):
                stats['success'] += 1
            else:
                stats['failed'] += 1
        
        # Afficher les statistiques
        elapsed_time = time.time() - start_time
        print(f"\n📊 Traitement terminé en {elapsed_time:.2f}s")
        print(f"   ✅ Succès: {stats['success']}")
        print(f"   ❌ Échecs: {stats['failed']}")
        print(f"   ⏭️  Ignorés: {stats['skipped']}")
        
        return stats

def list_available_models():
    """Affiche la liste des modèles disponibles"""
    print("🤖 Modèles disponibles:")
    for model, description in BackgroundRemover.MODELS.items():
        print(f"   • {model}: {description}")

def main():
    parser = argparse.ArgumentParser(
        description="Enlever le background des images avec rembg",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument('input', help='Fichier image ou dossier d\'entrée')
    parser.add_argument('-o', '--output', help='Fichier ou dossier de sortie')
    parser.add_argument('-m', '--model', default='u2net', 
                       choices=list(BackgroundRemover.MODELS.keys()),
                       help='Modèle à utiliser (défaut: u2net)')
    parser.add_argument('--white-bg', action='store_true',
                       help='Ajouter un fond blanc au lieu de transparent')
    parser.add_argument('--overwrite', action='store_true',
                       help='Écraser les fichiers existants')
    parser.add_argument('--list-models', action='store_true',
                       help='Lister les modèles disponibles')
    
    args = parser.parse_args()
    
    if args.list_models:
        list_available_models()
        return
    
    # Vérifier les arguments
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Fichier/dossier d'entrée introuvable: {args.input}")
        return
    
    # Déterminer le chemin de sortie
    if args.output:
        output_path = args.output
    else:
        if input_path.is_file():
            # Fichier unique
            suffix = "_no_bg.jpg" if args.white_bg else "_no_bg.png"
            output_path = str(input_path.parent / f"{input_path.stem}{suffix}")
        else:
            # Dossier
            output_path = str(input_path.parent / f"{input_path.name}_no_bg")
    
    print(f"🚀 Démarrage du traitement...")
    print(f"   📥 Entrée: {args.input}")
    print(f"   📤 Sortie: {output_path}")
    print(f"   🤖 Modèle: {args.model}")
    print(f"   🎨 Fond: {'Blanc' if args.white_bg else 'Transparent'}")
    
    # Initialiser le removeur
    remover = BackgroundRemover(args.model)
    
    # Traitement
    if input_path.is_file():
        # Fichier unique
        success = remover.remove_background(args.input, output_path, args.white_bg)
        if success:
            print(f"🎉 Terminé ! Image sauvegardée: {output_path}")
        else:
            print("❌ Échec du traitement")
    else:
        # Dossier
        stats = remover.process_batch(args.input, output_path, args.white_bg, args.overwrite)
        if stats['success'] > 0:
            print(f"🎉 Traitement terminé ! {stats['success']} image(s) traitée(s)")

if __name__ == "__main__":
    main()