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

    def run(self, model_bytes: bytes, garment_bytes: bytes, category="auto") -> str:
        body = {
            "model_image":   _b64(model_bytes),
            "garment_image": _b64(garment_bytes),
            "category":      category,
            "mode":          "balanced",
            "output_format": "jpeg",
        }
        logger.info(f"Sending to FASHN API: category={category}, model_image size={len(body['model_image'])}, garment_image size={len(body['garment_image'])}")
        
        try:
            r = requests.post(f"{BASE_URL}/run", json=body, headers=self.headers, timeout=30)
            logger.info(f"FASHN response status: {r.status_code}")
            if r.status_code != 200:
                logger.error(f"FASHN error response body: {r.text}")
            r.raise_for_status()
            data = r.json()
            logger.info(f"FASHN run successful, prediction_id={data['id']}")
            return data["id"]
        except requests.exceptions.RequestException as e:
            logger.exception("FASHN API request failed")
            raise

    def poll(self, pred_id: str, timeout=60) -> str:
        t0 = time.time()
        while time.time() - t0 < timeout:
            try:
                r = requests.get(f"{BASE_URL}/status/{pred_id}", headers=self.headers, timeout=15)
                if r.status_code != 200:
                    logger.error(f"FASHN status error {r.status_code}: {r.text}")
                    r.raise_for_status()
                data = r.json()
                status = data.get("status")
                logger.info(f"Polling {pred_id}: status={status}")
                if status == "completed":
                    output = data.get("output")
                    if output and isinstance(output, list) and len(output) > 0:
                        return output[0]
                    else:
                        raise RuntimeError("FASHN completed but no output")
                elif status == "failed":
                    error_msg = data.get("error", "Unknown error")
                    raise RuntimeError(f"FASHN failed: {error_msg}")
                time.sleep(3)
            except requests.exceptions.RequestException as e:
                logger.exception("FASHN polling error")
                raise
        raise TimeoutError("FASHN timed out")
