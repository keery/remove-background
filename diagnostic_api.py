#!/usr/bin/env python3
"""
Diagnostic approfondi de l'API distante Google Cloud Run
"""

import requests
import json
import time
import os
import shutil

def test_api_connectivity():
    """Test de base de connectivité"""
    print("🔍 DIAGNOSTIC DE L'API DISTANTE")
    print("=" * 60)
    
    base_url = "https://rembg-api-262374855257.europe-west1.run.app"
    
    # Test 1: Ping simple
    print("\n1️⃣ Test de connectivité de base")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        if response.status_code == 200:
            print(f"   Body: {response.text}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 2: Health check
    print("\n2️⃣ Test du health check")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Body: {response.text}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 3: Documentation
    print("\n3️⃣ Test de la documentation")
    try:
        response = requests.get(f"{base_url}/docs", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 4: Liste des modèles
    print("\n4️⃣ Test de la liste des modèles")
    try:
        response = requests.get(f"{base_url}/models", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Models: {response.text}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def test_different_methods():
    """Test différentes méthodes d'envoi d'image"""
    print("\n🧪 TEST DE DIFFÉRENTES MÉTHODES D'ENVOI")
    print("=" * 60)
    
    image_path = "/Users/guillaumeesnault/Downloads/uniqueName_1746368260953_2660.png"
    if not os.path.exists(image_path):
        print("❌ Image de test non trouvée")
        return
    
    base_url = "https://rembg-api-262374855257.europe-west1.run.app"
    
    # Méthode 1: multipart/form-data avec 'image'
    print("\n1️⃣ Test avec multipart/form-data (champ 'image')")
    try:
        with open(image_path, "rb") as f:
            files = {'image': ('test.png', f, 'image/png')}
            response = requests.post(f"{base_url}/remove-background", files=files, timeout=60)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
            if response.status_code != 200:
                print(f"   Error: {response.text[:500]}")
            else:
                print(f"   Success: {len(response.content)} bytes received")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Méthode 2: multipart/form-data avec 'file'
    print("\n2️⃣ Test avec multipart/form-data (champ 'file')")
    try:
        with open(image_path, "rb") as f:
            files = {'file': ('test.png', f, 'image/png')}
            response = requests.post(f"{base_url}/remove-background", files=files, timeout=60)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
            if response.status_code != 200:
                print(f"   Error: {response.text[:500]}")
            else:
                print(f"   Success: {len(response.content)} bytes received")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Méthode 3: Base64 via JSON
    print("\n3️⃣ Test avec base64 JSON")
    try:
        import base64
        with open(image_path, "rb") as f:
            image_data = f.read()
            image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        payload = {
            "image": image_b64,
            "model": "u2net",
            "white_bg": False
        }
        
        response = requests.post(
            f"{base_url}/remove-background-base64",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
        if response.status_code != 200:
            print(f"   Error: {response.text[:500]}")
        else:
            result = response.json()
            if result.get('success'):
                print(f"   Success: Base64 response received")
            else:
                print(f"   Failed: {result}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def analyze_our_api():
    """Analyse notre API locale pour comparaison"""
    print("\n📊 ANALYSE DE NOTRE API LOCALE (RÉFÉRENCE)")
    print("=" * 60)
    
    try:
        # Test de notre API locale
        response = requests.get("http://localhost:8080/", timeout=5)
        print(f"API Locale Status: {response.status_code}")
        print(f"API Locale Response: {response.json()}")
        
        # Vérifier les différences dans la réponse
        if response.status_code == 200:
            data = response.json()
            print(f"Models disponibles localement: {data.get('models', [])}")
    except Exception as e:
        print(f"❌ Erreur API locale: {e}")

def suggest_cloud_run_fixes():
    """Suggestions de corrections pour Google Cloud Run"""
    print("\n🔧 SUGGESTIONS DE CONFIGURATION GOOGLE CLOUD RUN")
    print("=" * 60)
    
    suggestions = [
        "1. Vérifier que le service est déployé et en cours d'exécution",
        "2. Augmenter la mémoire allouée (minimum 2GB pour rembg)",
        "3. Augmenter le timeout (minimum 300s pour traitement d'images)",
        "4. Vérifier les variables d'environnement (PORT=8080)",
        "5. Vérifier que l'image Docker est compatible avec Cloud Run",
        "6. Regarder les logs Cloud Run pour les erreurs de démarrage",
        "7. Vérifier les permissions IAM",
        "8. S'assurer que l'allocation CPU est suffisante",
        "9. Vérifier la concurrence (max 1 pour éviter les conflits mémoire)"
    ]
    
    for suggestion in suggestions:
        print(f"   {suggestion}")
    
    print("\n📋 COMMANDES UTILES GCLOUD:")
    print("   gcloud run services describe rembg-api --region=europe-west1")
    print("   gcloud run services update rembg-api --memory=4Gi --timeout=300 --region=europe-west1")
    print("   gcloud logs read --service-name=rembg-api --region=europe-west1")

def main():
    """Fonction principale de diagnostic"""
    test_api_connectivity()
    test_different_methods()
    analyze_our_api()
    suggest_cloud_run_fixes()
    
    print("\n" + "=" * 60)
    print("🏁 DIAGNOSTIC TERMINÉ")
    print("=" * 60)

if __name__ == "__main__":
    main()
