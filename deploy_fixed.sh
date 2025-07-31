#!/bin/bash
# Script de déploiement automatique pour la version corrigée

echo "🚀 DÉPLOIEMENT DE LA VERSION CORRIGÉE SUR CLOUD RUN"
echo "=" ×60

# Variables
PROJECT_ID="tidy-surge-467623-h2"
SERVICE_NAME="rembg-api"
REGION="europe-west1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME:fixed-v2"

echo "📋 Configuration:"
echo "   Project: $PROJECT_ID"
echo "   Service: $SERVICE_NAME"
echo "   Region: $REGION"
echo "   Image: $IMAGE_NAME"

# 1. Construction de l'image
echo ""
echo "🔨 1. Construction de l'image Docker..."
docker build -f Dockerfile.cloudrun.fixed -t $IMAGE_NAME .

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la construction"
    exit 1
fi

# 2. Push de l'image
echo ""
echo "📤 2. Push de l'image vers Google Container Registry..."
docker push $IMAGE_NAME

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors du push"
    exit 1
fi

# 3. Déploiement
echo ""
echo "🚀 3. Déploiement sur Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --concurrency 1 \
  --max-instances 10 \
  --allow-unauthenticated \
  --port 8080

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors du déploiement"
    exit 1
fi

# 4. Test après déploiement
echo ""
echo "🧪 4. Test du service déployé..."
SERVICE_URL="https://$SERVICE_NAME-262374855257.$REGION.run.app"

echo "   Test endpoint racine..."
curl -s "$SERVICE_URL/" | jq .

echo "   Test warmup..."
curl -s "$SERVICE_URL/warmup" | jq .

echo ""
echo "✅ DÉPLOIEMENT TERMINÉ!"
echo "🌐 URL du service: $SERVICE_URL"
echo ""
echo "📋 Commandes de test:"
echo "   curl $SERVICE_URL/"
echo "   curl $SERVICE_URL/warmup"
echo "   # Test avec image via Postman ou script"
