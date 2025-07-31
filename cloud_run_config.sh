# Configuration Cloud Run recommandée pour rembg

# 1. Mémoire insuffisante
gcloud run services update rembg-api \
  --memory=4Gi \
  --region=europe-west1

# 2. Timeout trop court  
gcloud run services update rembg-api \
  --timeout=300 \
  --region=europe-west1

# 3. Concurrence trop élevée (rembg utilise beaucoup de mémoire)
gcloud run services update rembg-api \
  --concurrency=1 \
  --region=europe-west1

# 4. CPU insuffisant
gcloud run services update rembg-api \
  --cpu=2 \
  --region=europe-west1

# 5. Commande complète recommandée
gcloud run services update rembg-api \
  --memory=4Gi \
  --timeout=300 \
  --concurrency=1 \
  --cpu=2 \
  --port=8080 \
  --region=europe-west1

# 6. Vérifier la configuration actuelle
gcloud run services describe rembg-api --region=europe-west1

# 7. Voir les logs d'erreur
gcloud logs read --service-name=rembg-api --region=europe-west1 --limit=50
