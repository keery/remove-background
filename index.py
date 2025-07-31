from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import io
import os
from pathlib import Path
from typing import Optional
import base64
import logging

try:
    from rembg import remove as bg, new_session
    from PIL import Image
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    raise

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Background Removal API",
    description="API pour supprimer le background des images avec rembg",
    version="1.0.0"
)

# Configuration CORS pour permettre les appels depuis votre NestJS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez vos domaines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BackgroundRemovalService:
    """Service pour gérer la suppression de background"""
    
    MODELS = {
        'u2net': 'Général - Bon équilibre qualité/vitesse',
        'u2net_human_seg': 'Optimisé pour les personnes',
        'u2net_cloth_seg': 'Optimisé pour les vêtements',
        'isnet-general-use': 'Général - Haute qualité',
        'birefnet-general': 'Général - Très haute qualité (plus lent)',
        'silueta': 'Personnes - Rapide'
    }
    
    def __init__(self):
        self.sessions = {}
        # Pré-charger le modèle par défaut
        self.get_session('u2net')
    
    def get_session(self, model_name: str = 'u2net'):
        """Récupère ou crée une session pour un modèle"""
        if model_name not in self.sessions:
            try:
                logger.info(f"Initialisation du modèle: {model_name}")
                self.sessions[model_name] = new_session(model_name)
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation du modèle {model_name}: {e}")
                # Fallback vers u2net
                if model_name != 'u2net':
                    self.sessions[model_name] = self.get_session('u2net')
                else:
                    raise
        return self.sessions[model_name]
    
    def remove_background(self, image_data: bytes, model_name: str = 'u2net', 
                         white_background: bool = False) -> bytes:
        """
        Supprime le background d'une image
        
        Args:
            image_data: Données de l'image en bytes
            model_name: Modèle à utiliser
            white_background: Ajouter un fond blanc au lieu de transparent
            
        Returns:
            bytes: Image processée
        """
        try:
            session = self.get_session(model_name)
            
            # Supprimer le background
            output_data = bg(image_data, session=session)
            
            if white_background:
                # Ajouter un fond blanc
                image = Image.open(io.BytesIO(output_data)).convert("RGBA")
                white_bg = Image.new("RGB", image.size, (255, 255, 255))
                white_bg.paste(image, mask=image.split()[-1])
                
                # Convertir en bytes
                output_buffer = io.BytesIO()
                white_bg.save(output_buffer, format='JPEG', quality=95)
                return output_buffer.getvalue()
            else:
                return output_data
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur de traitement: {str(e)}")

# Instance globale du service
bg_service = BackgroundRemovalService()

@app.get("/")
async def root():
    """Point de santé de l'API"""
    return {
        "message": "Background Removal API",
        "status": "running",
        "models": list(BackgroundRemovalService.MODELS.keys())
    }

@app.get("/health")
async def health():
    """Health check pour Google Cloud Run"""
    return {"status": "healthy"}

@app.get("/models")
async def list_models():
    """Liste les modèles disponibles"""
    return {
        "models": BackgroundRemovalService.MODELS
    }

@app.post("/remove-background")
async def remove_background_endpoint(
    image: UploadFile = File(..., description="Image à traiter"),
    model: str = Query('u2net', description="Modèle à utiliser"),
    white_bg: bool = Query(False, description="Ajouter un fond blanc"),
    format: str = Query('png', description="Format de sortie (png/jpeg)")
):
    """
    Supprime le background d'une image uploadée
    """
    # Vérifier le type de fichier
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image")
    
    # Vérifier le modèle
    if model not in BackgroundRemovalService.MODELS:
        raise HTTPException(
            status_code=400, 
            detail=f"Modèle '{model}' non supporté. Modèles disponibles: {list(BackgroundRemovalService.MODELS.keys())}"
        )
    
    try:
        # Lire l'image
        image_data = await image.read()
        logger.info(f"Traitement d'une image de {len(image_data)} bytes avec le modèle {model}")
        
        # Traiter l'image
        result_data = bg_service.remove_background(
            image_data, 
            model_name=model,
            white_background=white_bg
        )
        
        # Déterminer le type de contenu
        if white_bg or format.lower() == 'jpeg':
            media_type = "image/jpeg"
            filename = "result.jpg"
        else:
            media_type = "image/png"
            filename = "result.png"
        
        return Response(
            content=result_data,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/remove-background-base64")
async def remove_background_base64(
    request: dict,
):
    """
    Supprime le background d'une image encodée en base64
    
    Body: {
        "image": "base64_string",
        "model": "u2net",
        "white_bg": false
    }
    """
    try:
        # Extraire les paramètres
        image_b64 = request.get('image')
        model = request.get('model', 'u2net')
        white_bg = request.get('white_bg', False)
        
        if not image_b64:
            raise HTTPException(status_code=400, detail="Image base64 manquante")
        
        # Décoder l'image
        try:
            image_data = base64.b64decode(image_b64)
        except Exception:
            raise HTTPException(status_code=400, detail="Format base64 invalide")
        
        # Traiter l'image
        result_data = bg_service.remove_background(
            image_data,
            model_name=model,
            white_background=white_bg
        )
        
        # Encoder le résultat en base64
        result_b64 = base64.b64encode(result_data).decode('utf-8')
        
        return {
            "success": True,
            "image": result_b64,
            "model_used": model,
            "white_background": white_bg
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du traitement base64: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)