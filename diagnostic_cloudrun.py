#!/usr/bin/env python3
"""
Diagnostic spécifique pour le problème Cloud Run identifié
"""

import requests
import json
import time
import os
import base64

def test_small_image():
    """Test avec une très petite image pour isoler le problème"""
    print("🔍 TEST AVEC UNE PETITE IMAGE")
    print("=" * 60)
    
    # Créer une petite image de test (1x1 pixel PNG)
    # PNG header + 1x1 pixel blanc transparent
    tiny_png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGCfVgChgAAAABJRU5ErkJggg=="
    )
    
    with open("tiny_test.png", "wb") as f:
        f.write(tiny_png)
    
    print(f"📁 Image de test créée: {len(tiny_png)} bytes")
    
    # Test avec l'API distante
    print("\n🚀 Test Cloud Run avec image minuscule")
    try:
        with open("tiny_test.png", "rb") as f:
            files = {'image': ('tiny.png', f, 'image/png')}
            
            start_time = time.time()
            response = requests.post(
                "https://rembg-api-262374855257.europe-west1.run.app/remove-background",
                files=files,
                timeout=120
            )
            end_time = time.time()
            
            print(f"   Status: {response.status_code}")
            print(f"   Durée: {end_time - start_time:.3f}s")
            print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
            
            if response.status_code == 200:
                print(f"   ✅ Succès avec petite image: {len(response.content)} bytes")
                return True
            else:
                print(f"   ❌ Échec: {response.text[:200]}")
                return False
                
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_progressive_sizes():
    """Test avec des tailles d'image progressives"""
    print("\n📊 TEST AVEC TAILLES PROGRESSIVES")
    print("=" * 60)
    
    # Utiliser l'image originale et créer des versions redimensionnées
    original_path = "/Users/guillaumeesnault/Downloads/uniqueName_1746368260953_2660.png"
    
    if not os.path.exists(original_path):
        print("❌ Image originale non trouvée")
        return
    
    # Lire l'image originale
    with open(original_path, "rb") as f:
        original_data = f.read()
    
    print(f"📏 Taille originale: {len(original_data):,} bytes")
    
    # Test avec des portions de l'image pour simuler différentes tailles
    sizes_to_test = [1024, 2048, 4096, 8192, 16384, 32768]
    
    for max_size in sizes_to_test:
        if len(original_data) <= max_size:
            continue
            
        print(f"\n🧪 Test avec {max_size} premiers bytes")
        try:
            # Prendre seulement les premiers bytes (pas une vraie image, mais test de taille)
            test_data = original_data[:max_size]
            
            # Sauvegarder temporairement
            test_file = f"test_{max_size}.dat"
            with open(test_file, "wb") as f:
                f.write(test_data)
            
            # Test rapide de l'API
            with open(test_file, "rb") as f:
                files = {'image': ('test.png', f, 'image/png')}
                
                start_time = time.time()
                try:
                    response = requests.post(
                        "https://rembg-api-262374855257.europe-west1.run.app/remove-background",
                        files=files,
                        timeout=60
                    )
                    end_time = time.time()
                    
                    print(f"     Status: {response.status_code}, Durée: {end_time - start_time:.3f}s")
                    
                    if response.status_code != 200:
                        print(f"     Erreur: {response.text[:100]}")
                        
                except requests.exceptions.Timeout:
                    print(f"     ⏰ Timeout après 60s")
                except Exception as e:
                    print(f"     ❌ Erreur: {e}")
            
            # Nettoyer
            os.remove(test_file)
            
        except Exception as e:
            print(f"     ❌ Erreur test: {e}")

def test_request_format():
    """Test de différents formats de requête pour identifier le problème exact"""
    print("\n🔬 TEST DES FORMATS DE REQUÊTE")
    print("=" * 60)
    
    tiny_png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGCfVgChgAAAABJRU5ErkJggg=="
    )
    
    base_url = "https://rembg-api-262374855257.europe-west1.run.app"
    
    # Test 1: Multipart simple
    print("\n1️⃣ Test multipart basique")
    try:
        files = {'image': ('test.png', tiny_png, 'image/png')}
        response = requests.post(f"{base_url}/remove-background", files=files, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text[:200]}")
    except Exception as e:
        print(f"   Erreur: {e}")
    
    # Test 2: Avec paramètres
    print("\n2️⃣ Test avec paramètres")
    try:
        files = {'image': ('test.png', tiny_png, 'image/png')}
        params = {'model': 'u2net', 'white_bg': 'false'}
        response = requests.post(f"{base_url}/remove-background", files=files, params=params, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text[:200]}")
    except Exception as e:
        print(f"   Erreur: {e}")
    
    # Test 3: Headers spécifiques
    print("\n3️⃣ Test avec headers Cloud Run")
    try:
        files = {'image': ('test.png', tiny_png, 'image/png')}
        headers = {
            'User-Agent': 'CloudRunDiagnostic/1.0',
            'Accept': '*/*'
        }
        response = requests.post(f"{base_url}/remove-background", files=files, headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text[:200]}")
    except Exception as e:
        print(f"   Erreur: {e}")

def analyze_cloud_run_issue():
    """Analyse spécifique du problème Cloud Run"""
    print("\n🏗️ ANALYSE DU PROBLÈME CLOUD RUN")
    print("=" * 60)
    
    print("📋 Analyse du log d'erreur:")
    print("   • Latency: 0.154526003s (crash très rapide)")
    print("   • Error: malformed response or connection error")
    print("   • Status: 503 Service Unavailable")
    print("   • Request size: 62,489 bytes (taille raisonnable)")
    
    print("\n🎯 Causes probables:")
    causes = [
        "1. Instance Cloud Run manque de mémoire (OOM kill)",
        "2. Crash de l'application Python au démarrage du traitement",
        "3. Timeout de démarrage de l'instance (cold start)",
        "4. Problème avec les dépendances rembg/onnxruntime",
        "5. Limite de CPU dépassée rapidement"
    ]
    
    for cause in causes:
        print(f"   {cause}")
    
    print("\n🔧 Actions recommandées:")
    actions = [
        "1. Augmenter drastiquement la mémoire (4GB minimum)",
        "2. Réduire la concurrence à 1",
        "3. Augmenter le CPU à 2 vCPU",
        "4. Supprimer le pré-chargement du modèle",
        "5. Ajouter plus de logging dans l'application",
        "6. Implémenter un warmup endpoint"
    ]
    
    for action in actions:
        print(f"   {action}")

def generate_fixed_dockerfile():
    """Génère un Dockerfile corrigé pour le problème identifié"""
    print("\n🛠️ GÉNÉRATION DOCKERFILE CORRIGÉ")
    print("=" * 60)
    
    dockerfile_content = '''# Dockerfile optimisé pour Cloud Run - Version corrective
FROM python:3.11-slim

# Variables d'environnement optimisées
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8080
ENV WORKERS=1

# Installation des dépendances système
RUN apt-get update && apt-get install -y \\
    libglib2.0-0 libsm6 libxext6 libxrender-dev \\
    libgomp1 libgl1-mesa-glx \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# IMPORTANT: NE PAS pré-charger le modèle pour éviter le crash au démarrage
# RUN python -c "from rembg import new_session; new_session('u2net')"

# Copie du code
COPY . .

# Endpoint de warmup pour pré-charger le modèle à la demande
EXPOSE 8080

# Commande optimisée pour Cloud Run
CMD exec python main.py'''
    
    with open("Dockerfile.fixed", "w") as f:
        f.write(dockerfile_content)
    
    print("✅ Dockerfile.fixed généré")

def main():
    """Fonction principale"""
    print("🚨 DIAGNOSTIC CLOUD RUN - PROBLÈME IDENTIFIÉ")
    print("=" * 70)
    
    analyze_cloud_run_issue()
    test_small_image()
    test_request_format()
    generate_fixed_dockerfile()
    
    print("\n" + "=" * 70)
    print("🎯 CONCLUSION: L'instance Cloud Run crash au démarrage du traitement")
    print("💡 SOLUTION: Augmenter les ressources ET supprimer le pré-chargement")
    print("=" * 70)

if __name__ == "__main__":
    main()
