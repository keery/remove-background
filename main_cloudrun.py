#!/usr/bin/env python3
"""
Version Cloud Run optimisée du main.py
"""

import os
import gc
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import io
import logging

# Configuration du logging pour Cloud Run
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Background Removal API",
    description="API pour supprimer le background des images avec rembg - Cloud Run Optimized",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import lazy pour économiser la mémoire au démarrage
def lazy_import_rembg():
    """Import rembg seulement quand nécessaire"""
    try:
        from rembg import remove as bg, new_session
        from PIL import Image
        return bg, new_session, Image
    except ImportError as e:
        logger.error(f"Erreur d'import rembg: {e}")
        raise HTTPException(status_code=500, detail="Service indisponible")

class CloudRunBackgroundRemovalService:
    """Service optimisé pour Cloud Run"""
    
    def __init__(self):
        self.session_cache = {}
        self.bg = None
        self.new_session = None
        self.Image = None
    
    def _ensure_imports(self):
        """S'assurer que les imports sont faits"""
        if self.bg is None:
            self.bg, self.new_session, self.Image = lazy_import_rembg()
    
    def get_session(self, model_name: str = 'u2net'):
        """Récupère une session de manière lazy"""
        self._ensure_imports()
        
        if model_name not in self.session_cache:
            try:
                logger.info(f"Initialisation du modèle: {model_name}")
                self.session_cache[model_name] = self.new_session(model_name)
                logger.info(f"Modèle {model_name} initialisé avec succès")
            except Exception as e:
                logger.error(f"Erreur initialisation modèle {model_name}: {e}")
                raise HTTPException(status_code=500, detail=f"Erreur modèle: {str(e)}")
        
        return self.session_cache[model_name]
    
    def remove_background(self, image_data: bytes, model_name: str = 'u2net'):
        """Supprime le background avec gestion mémoire optimisée"""
        try:
            self._ensure_imports()
            
            # Libérer la mémoire avant traitement
            gc.collect()
            
            session = self.get_session(model_name)
            logger.info(f"Début traitement image: {len(image_data)} bytes")
            
            # Traitement
            result = self.bg(image_data, session=session)
            
            # Libérer la mémoire après traitement
            gc.collect()
            
            logger.info(f"Traitement terminé: {len(result)} bytes")
            return result
            
        except Exception as e:
            logger.error(f"Erreur traitement: {e}")
            # Force garbage collection en cas d'erreur
            gc.collect()
            raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# Instance globale
bg_service = CloudRunBackgroundRemovalService()

@app.get("/")
async def root():
    """Point de santé de l'API"""
    return {
        "message": "Background Removal API",
        "status": "running",
        "models": ["u2net", "u2net_human_seg", "u2net_cloth_seg", "isnet-general-use", "birefnet-general", "silueta"],
        "cloud_run_optimized": True
    }

@app.get("/health")
async def health():
    """Health check pour Google Cloud Run"""
    return {"status": "healthy", "memory_usage": "optimized"}

@app.post("/remove-background")
async def remove_background_endpoint(
    image: UploadFile = File(..., description="Image à traiter"),
    model: str = Query('u2net', description="Modèle à utiliser")
):
    """Supprime le background - version Cloud Run optimisée"""
    
    # Vérifications
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image")
    
    try:
        # Lecture de l'image
        image_data = await image.read()
        
        # Limitation de taille pour Cloud Run
        max_size = 10 * 1024 * 1024  # 10MB
        if len(image_data) > max_size:
            raise HTTPException(status_code=400, detail="Image trop grande (max 10MB)")
        
        logger.info(f"Traitement image: {len(image_data)} bytes, modèle: {model}")
        
        # Traitement
        result_data = bg_service.remove_background(image_data, model)
        
        return Response(
            content=result_data,
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=result.png"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur endpoint: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
