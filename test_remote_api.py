#!/usr/bin/env python3
"""
Script pour tester l'API distante de suppression d'arrière-plan
"""

import requests
import base64
import io
import os
import shutil

def copy_test_image():
    """Copie l'image de test fournie par l'utilisateur"""
    source_path = "/Users/guillaumeesnault/Downloads/uniqueName_1746368260953_2660.png"
    target_path = "test_image.png"
    
    print(f"� Copie de l'image de test : {source_path}")
    
    if os.path.exists(source_path):
        shutil.copy2(source_path, target_path)
        print(f"✅ Image copiée : {target_path}")
        return target_path
    else:
        print(f"❌ L'image source n'existe pas : {source_path}")
        return None

def test_remote_api(image_path, api_url):
    """Teste l'API distante de suppression d'arrière-plan"""
    
    if not os.path.exists(image_path):
        print(f"❌ L'image {image_path} n'existe pas")
        return None
    
    print(f"🚀 Test de l'API distante : {api_url}")
    
    try:
        # Lecture et encodage de l'image
        with open(image_path, "rb") as img_file:
            files = {
                'image': ('test_image.png', img_file, 'image/png')
            }
            
            print("📤 Envoi de l'image à l'API distante...")
            
            # Appel à l'API distante
            response = requests.post(
                api_url,
                files=files,
                timeout=30  # 30 secondes de timeout
            )
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📊 Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                # Sauvegarde de l'image résultat
                output_path = "result_remote_api.png"
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                print(f"✅ Succès ! Image résultat sauvegardée : {output_path}")
                
                # Vérification de la taille du fichier
                file_size = os.path.getsize(output_path)
                print(f"📏 Taille du fichier résultat : {file_size} bytes")
                
                # Vérification basique du fichier
                if file_size > 0:
                    print(f"🖼️  L'image semble avoir été traitée correctement")
                else:
                    print(f"⚠️  Le fichier résultat est vide")
                
                return output_path
            else:
                print(f"❌ Erreur de l'API : {response.status_code}")
                print(f"📄 Réponse : {response.text[:500]}...")
                return None
                
    except requests.exceptions.Timeout:
        print("⏰ Timeout - L'API a mis trop de temps à répondre")
        return None
    except requests.exceptions.ConnectionError:
        print("🔌 Erreur de connexion - Impossible de joindre l'API")
        return None
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        return None

def main():
    """Fonction principale"""
    print("🎯 Test de l'API distante de suppression d'arrière-plan")
    print("=" * 60)
    
    # URL de l'API distante
    api_url = "https://rembg-api-262374855257.europe-west1.run.app/remove-background"
    
    # Copie de l'image de test
    image_path = copy_test_image()
    
    if image_path:
        # Test de l'API distante
        result = test_remote_api(image_path, api_url)
        
        if result:
            print("\n🎉 Test réussi !")
            print(f"📁 Image originale : {image_path}")
            print(f"📁 Image résultat : {result}")
        else:
            print("\n💥 Échec du test")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
