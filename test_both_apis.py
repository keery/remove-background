#!/usr/bin/env python3
"""
Script pour tester les APIs de suppression d'arrière-plan (locale et distante)
"""

import requests
import os
import shutil

def copy_test_image():
    """Copie l'image de test fournie par l'utilisateur"""
    source_path = "/Users/guillaumeesnault/Downloads/uniqueName_1746368260953_2660.png"
    target_path = "test_image.png"
    
    print(f"📁 Copie de l'image de test : {source_path}")
    
    if os.path.exists(source_path):
        shutil.copy2(source_path, target_path)
        print(f"✅ Image copiée : {target_path}")
        return target_path
    else:
        print(f"❌ L'image source n'existe pas : {source_path}")
        return None

def test_api(image_path, api_url, api_name="API"):
    """Teste une API de suppression d'arrière-plan"""
    
    if not os.path.exists(image_path):
        print(f"❌ L'image {image_path} n'existe pas")
        return None
    
    print(f"\n🚀 Test de {api_name} : {api_url}")
    
    try:
        # Lecture et encodage de l'image
        with open(image_path, "rb") as img_file:
            files = {
                'image': ('test_image.png', img_file, 'image/png')
            }
            
            print(f"📤 Envoi de l'image à {api_name}...")
            
            # Appel à l'API
            response = requests.post(
                api_url,
                files=files,
                timeout=60  # 60 secondes de timeout pour l'API distante
            )
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📊 Content-Type: {response.headers.get('content-type', 'Unknown')}")
            
            if response.status_code == 200:
                # Sauvegarde de l'image résultat
                safe_name = api_name.lower().replace(" ", "_")
                output_path = f"result_{safe_name}.png"
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                print(f"✅ Succès ! Image résultat sauvegardée : {output_path}")
                
                # Vérification de la taille du fichier
                file_size = os.path.getsize(output_path)
                print(f"📏 Taille du fichier résultat : {file_size:,} bytes")
                
                # Vérification basique du fichier
                if file_size > 1000:  # Au moins 1KB
                    print(f"🖼️  L'image semble avoir été traitée correctement")
                else:
                    print(f"⚠️  Le fichier résultat semble petit ({file_size} bytes)")
                
                return output_path
            else:
                print(f"❌ Erreur de {api_name} : {response.status_code}")
                print(f"📄 Réponse : {response.text[:500]}...")
                return None
                
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout - {api_name} a mis trop de temps à répondre")
        return None
    except requests.exceptions.ConnectionError:
        print(f"🔌 Erreur de connexion - Impossible de joindre {api_name}")
        return None
    except Exception as e:
        print(f"❌ Erreur inattendue avec {api_name} : {e}")
        return None

def main():
    """Fonction principale"""
    print("🎯 Test des APIs de suppression d'arrière-plan")
    print("=" * 60)
    
    # Copie de l'image de test
    image_path = copy_test_image()
    
    if not image_path:
        print("❌ Impossible de préparer l'image de test")
        return
    
    # Test de l'API locale d'abord
    local_result = test_api(
        image_path, 
        "http://localhost:8080/remove-background", 
        "API Locale"
    )
    
    # Test de l'API distante
    remote_result = test_api(
        image_path,
        "https://rembg-api-262374855257.europe-west1.run.app/remove-background",
        "API Distante"
    )
    
    # Résumé
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    if local_result:
        print(f"✅ API Locale : SUCCÈS - {local_result}")
    else:
        print("❌ API Locale : ÉCHEC")
    
    if remote_result:
        print(f"✅ API Distante : SUCCÈS - {remote_result}")
    else:
        print("❌ API Distante : ÉCHEC")
    
    print(f"📁 Image originale : {image_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
