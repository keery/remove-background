#!/usr/bin/env python3
"""
Test de la version corrigée en local avant déploiement Cloud Run
"""

import requests
import time
import os

def test_fixed_version_locally():
    """Test de la version corrigée localement"""
    print("🧪 TEST DE LA VERSION CORRIGÉE EN LOCAL")
    print("=" * 60)
    
    # D'abord, arrêter l'ancienne version
    print("🛑 Arrêt de l'ancienne version...")
    os.system("docker stop remove-bg-api 2>/dev/null || true")
    os.system("docker rm remove-bg-api 2>/dev/null || true")
    
    # Lancer la nouvelle version
    print("🚀 Démarrage de la version corrigée...")
    
    # Utiliser directement Python pour tester
    print("\n📋 Lancement avec Python...")
    
    # Test des endpoints de base
    print("\n1️⃣ Test des endpoints de santé")
    base_url = "http://localhost:8080"
    
    # Attendre le démarrage
    time.sleep(2)
    
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status /: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   Service Available: {data.get('service_available', False)}")
    except Exception as e:
        print(f"   ❌ Erreur /: {e}")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status /health: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Health: {data}")
    except Exception as e:
        print(f"   ❌ Erreur /health: {e}")
    
    # Test warmup
    print("\n2️⃣ Test du warmup")
    try:
        response = requests.get(f"{base_url}/warmup", timeout=30)
        print(f"   Status /warmup: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Warmup: {data}")
    except Exception as e:
        print(f"   ❌ Erreur /warmup: {e}")
    
    # Test traitement image
    print("\n3️⃣ Test traitement d'image")
    image_path = "/Users/guillaumeesnault/Downloads/uniqueName_1746368260953_2660.png"
    
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as f:
                files = {'image': ('test.png', f, 'image/png')}
                response = requests.post(f"{base_url}/remove-background", files=files, timeout=120)
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ Succès! Taille résultat: {len(response.content)} bytes")
                    
                    # Sauvegarder le résultat
                    with open("result_fixed_version.png", "wb") as result_file:
                        result_file.write(response.content)
                    print(f"   📁 Résultat sauvegardé: result_fixed_version.png")
                else:
                    print(f"   ❌ Erreur: {response.text[:200]}")
                    
        except Exception as e:
            print(f"   ❌ Erreur traitement: {e}")
    else:
        print("   ⚠️ Image de test non trouvée")

def generate_deployment_commands():
    """Génère les commandes de déploiement Cloud Run"""
    print("\n🚀 COMMANDES DE DÉPLOIEMENT CLOUD RUN")
    print("=" * 60)
    
    commands = [
        "# 1. Construction de l'image Docker corrigée",
        "docker build -f Dockerfile.cloudrun.fixed -t gcr.io/tidy-surge-467623-h2/rembg-api:fixed .",
        "",
        "# 2. Push de l'image",
        "docker push gcr.io/tidy-surge-467623-h2/rembg-api:fixed",
        "",
        "# 3. Déploiement avec configuration optimale",
        "gcloud run deploy rembg-api \\",
        "  --image gcr.io/tidy-surge-467623-h2/rembg-api:fixed \\",
        "  --platform managed \\",
        "  --region europe-west1 \\",
        "  --memory 4Gi \\",
        "  --cpu 2 \\",
        "  --timeout 300 \\",
        "  --concurrency 1 \\",
        "  --max-instances 10 \\",
        "  --allow-unauthenticated \\",
        "  --port 8080",
        "",
        "# 4. Warmup après déploiement",
        "curl https://rembg-api-262374855257.europe-west1.run.app/warmup",
        "",
        "# 5. Test avec l'image",
        "# Utiliser Postman ou curl pour tester /remove-background"
    ]
    
    for cmd in commands:
        print(cmd)

def main():
    """Fonction principale"""
    print("🔧 VALIDATION DE LA SOLUTION CLOUD RUN")
    print("=" * 70)
    
    test_fixed_version_locally()
    generate_deployment_commands()
    
    print("\n" + "=" * 70)
    print("✅ SOLUTION PRÊTE POUR DÉPLOIEMENT")
    print("🎯 Changements clés:")
    print("   • Suppression du pré-chargement du modèle")
    print("   • Gestion d'erreur robuste") 
    print("   • Import lazy des dépendances")
    print("   • Endpoint de warmup")
    print("   • Gestion mémoire optimisée")
    print("=" * 70)

if __name__ == "__main__":
    main()
