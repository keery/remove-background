#!/usr/bin/env python3
"""
Test script pour débugger l'API avec les nouvelles validations
"""

import requests
import sys
from PIL import Image
import io

def create_test_image():
    """Créer une image simple pour les tests"""
    # Créer une image simple 100x100 rouge
    img = Image.new('RGB', (100, 100), color='red')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    return buffer.getvalue()

def test_api():
    url = "http://localhost:8000/remove-background"
    
    # Créer une image de test
    image_data = create_test_image()
    print(f"📸 Image de test créée: {len(image_data)} bytes")
    
    # Test 1: Sans fond blanc
    print("\n🧪 Test 1: Sans fond blanc")
    files = {'image': ('test.jpg', image_data, 'image/jpeg')}
    data = {'white_bg': 'false'}
    
    try:
        response = requests.post(url, files=files, data=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Succès: {len(response.content)} bytes retournés")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Avec fond blanc 
    print("\n🧪 Test 2: Avec fond blanc")
    files = {'image': ('test.jpg', image_data, 'image/jpeg')}
    data = {'white_bg': 'true'}
    
    try:
        response = requests.post(url, files=files, data=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Succès: {len(response.content)} bytes retournés")
            # Sauvegarder pour vérifier
            with open('test_result_debug.jpg', 'wb') as f:
                f.write(response.content)
            print("💾 Résultat sauvé dans test_result_debug.jpg")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_api()
