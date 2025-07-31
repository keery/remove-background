#!/usr/bin/env python3
"""
Version Cloud Run CORRIGÉE - Résout le problème de crash
"""

import os
import gc
import logging
import traceback
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import io

# Configuration logging pour Cloud Run
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Background Removal API - Cloud Run Fixed",
    description="API optimisée pour Google Cloud Run",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SafeBackgroundRemovalService:
    """Service avec gestion d'erreur robuste pour Cloud Run"""
    
    def __init__(self):
        self.session_cache = {}
        self.rembg_imports = None
        logger.info("Service initialisé - imports lazy")
    
    def _safe_import_rembg(self):
        """Import sécurisé de rembg avec gestion d'erreur complète"""
        if self.rembg_imports is not None:
            return self.rembg_imports
        
        try:
            logger.info("Début import rembg...")
            from rembg import remove as bg, new_session
            from PIL import Image
            
            self.rembg_imports = (bg, new_session, Image)
            logger.info("✅ Import rembg réussi")
            return self.rembg_imports
            
        except Exception as e:
            logger.error(f"❌ Erreur import rembg: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, 
                detail=f"Erreur d'initialisation du service: {str(e)}"
            )
    
    def _safe_get_session(self, model_name: str = 'u2net'):
        """Création sécurisée de session avec gestion mémoire"""
        if model_name in self.session_cache:
            return self.session_cache[model_name]
        
        try:
            logger.info(f"Initialisation du modèle {model_name}...")
            
            # Import sécurisé
            bg, new_session, Image = self._safe_import_rembg()
            
            # Libération mémoire avant chargement
            gc.collect()
            
            # Création session
            session = new_session(model_name)
            self.session_cache[model_name] = session
            
            logger.info(f"✅ Modèle {model_name} initialisé")
            return session
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation modèle {model_name}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Libération mémoire en cas d'erreur
            gc.collect()
            
            raise HTTPException(
                status_code=500,
                detail=f"Erreur initialisation modèle {model_name}: {str(e)}"
            )
    
    def safe_remove_background(self, image_data: bytes, model_name: str = 'u2net') -> bytes:
        """Suppression background avec gestion d'erreur complète"""
        try:
            logger.info(f"Début traitement - Image: {len(image_data)} bytes, Modèle: {model_name}")
            
            # Vérification taille image
            max_size = 10 * 1024 * 1024  # 10MB
            if len(image_data) > max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"Image trop grande ({len(image_data)} bytes). Maximum: {max_size} bytes"
                )
            
            # Import sécurisé
            bg, new_session, Image = self._safe_import_rembg()
            
            # Session sécurisée
            session = self._safe_get_session(model_name)
            
            # Libération mémoire avant traitement
            gc.collect()
            
            logger.info("Début du traitement rembg...")
            
            # Traitement avec timeout implicite
            result = bg(image_data, session=session)
            
            logger.info(f"✅ Traitement terminé - Résultat: {len(result)} bytes")
            
            # Libération mémoire après traitement
            gc.collect()
            
            return result
            
        except HTTPException:
            # Re-raise les HTTPException
            raise
        except Exception as e:
            logger.error(f"❌ Erreur traitement: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Libération mémoire forcée en cas d'erreur
            gc.collect()
            
            raise HTTPException(
                status_code=500,
                detail=f"Erreur de traitement: {str(e)}"
            )

# Instance globale avec gestion d'erreur
try:
    bg_service = SafeBackgroundRemovalService()
    logger.info("✅ Service global initialisé")
except Exception as e:
    logger.error(f"❌ Erreur initialisation service global: {e}")
    bg_service = None

@app.get("/")
async def root():
    """Point de santé avec diagnostic"""
    return {
        "message": "Background Removal API - Cloud Run Fixed",
        "status": "running",
        "service_available": bg_service is not None,
        "models": ["u2net", "u2net_human_seg", "u2net_cloth_seg", "isnet-general-use", "birefnet-general", "silueta"],
        "version": "2.0.0-fixed"
    }

@app.get("/health")
async def health():
    """Health check détaillé pour Cloud Run"""
    try:
        # Test basique du service
        service_ok = bg_service is not None
        
        return {
            "status": "healthy",
            "service_initialized": service_ok,
            "memory_management": "optimized"
        }
    except Exception as e:
        logger.error(f"Erreur health check: {e}")
        return {
            "status": "degraded",
            "error": str(e)
        }

@app.get("/warmup")
async def warmup():
    """Endpoint de warmup pour pré-charger le modèle"""
    try:
        if bg_service is None:
            raise HTTPException(status_code=500, detail="Service non initialisé")
        
        logger.info("Début warmup...")
        
        # Pré-charger le modèle par défaut
        bg_service._safe_get_session('u2net')
        
        return {
            "status": "warmed_up",
            "model_loaded": "u2net"
        }
    except Exception as e:
        logger.error(f"Erreur warmup: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur warmup: {str(e)}")

@app.post("/remove-background")
async def remove_background_endpoint(
    image: UploadFile = File(..., description="Image à traiter"),
    model: str = Query('u2net', description="Modèle à utiliser")
):
    """Endpoint principal - version sécurisée"""
    
    # Vérifications préliminaires
    if bg_service is None:
        raise HTTPException(status_code=500, detail="Service non disponible")
    
    if not image.content_type or not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image")
    
    # Modèles supportés
    supported_models = ["u2net", "u2net_human_seg", "u2net_cloth_seg", "isnet-general-use", "birefnet-general", "silueta"]
    if model not in supported_models:
        raise HTTPException(
            status_code=400,
            detail=f"Modèle '{model}' non supporté. Modèles disponibles: {supported_models}"
        )
    
    try:
        # Lecture image
        logger.info(f"Lecture image: {image.filename}")
        image_data = await image.read()
        
        logger.info(f"Image reçue: {len(image_data)} bytes")
        
        # Traitement sécurisé
        result_data = bg_service.safe_remove_background(image_data, model)
        
        # Réponse
        return Response(
            content=result_data,
            media_type="image/png",
            headers={
                "Content-Disposition": "attachment; filename=result.png",
                "X-Processing-Model": model
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur endpoint: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8080))
    
    logger.info(f"Démarrage serveur sur port {port}")
    
    # Configuration uvicorn optimisée pour Cloud Run
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )
