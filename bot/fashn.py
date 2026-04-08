import base64
import time
import logging
import requests
from config import FASHN_API_KEY

logger = logging.getLogger(__name__)

BASE_URL = "https://api.fashn.ai/v1"

def _b64(img: bytes, mime="jpeg") -> str:
    return f"data:image/{mime};base64," + base64.b64encode(img).decode()

class FashnClient:
    def __init__(self, key: str = FASHN_API_KEY):
        if not key:
            logger.error("FASHN_API_KEY is empty!")
            raise ValueError("FASHN_API_KEY not set")
        self.api_key = key
        self.headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

    def run(self, model_bytes: bytes, garment_bytes: bytes) -> str:
        # Формируем тело запроса в соответствии с документацией
        payload = {
            "model_name": "tryon-v1.6",
            "inputs": {
                "model_image": _b64(model_bytes),
                "garment_image": _b64(garment_bytes),
                "category": "auto",
                "segmentation_free": True,
                "moderation_level": "permissive",
                "garment_photo_type": "auto"
            }
        }
        logger.info("Sending request to FASHN API...")
        response = requests.post(f"{BASE_URL}/run", json=payload, headers=self.headers)
        
        if response.status_code != 200:
            logger.error(f"FASHN API error: {response.status_code} - {response.text}")
            response.raise_for_status()
        
        data = response.json()
        prediction_id = data.get("id")
        if not prediction_id:
            raise RuntimeError("No prediction ID in response")
        logger.info(f"Prediction started, ID: {prediction_id}")
        return prediction_id

    def poll(self, pred_id: str, timeout=60) -> str:
        start_time = time.time()
        while time.time() - start_time < timeout:
            status_response = requests.get(f"{BASE_URL}/status/{pred_id}", headers=self.headers)
            if status_response.status_code != 200:
                logger.error(f"Status check failed: {status_response.status_code}")
                status_response.raise_for_status()
            
            status_data = status_response.json()
            current_status = status_data.get("status")
            logger.info(f"Polling status: {current_status}")
            
            if current_status == "completed":
                output = status_data.get("output")
                if output and isinstance(output, list) and len(output) > 0:
                    result_url = output[0]
                    logger.info(f"Generation completed, result URL: {result_url}")
                    return result_url
                else:
                    raise RuntimeError("FASHN completed but no output found")
            elif current_status == "failed":
                error_msg = status_data.get("error", "Unknown error")
                raise RuntimeError(f"FASHN generation failed: {error_msg}")
            
            time.sleep(3)
        
        raise TimeoutError("FASHN API timed out")
