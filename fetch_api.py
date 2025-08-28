import os
import requests
from typing import Dict, Any, Optional, Tuple

BASE_URL = "https://v1.motorapi.dk"

#Load api keyen fra miljøvariabel eller config.py
try:
    from config import API_KEY as CONFIG_API_KEY
except ImportError:
    CONFIG_API_KEY = None

#Prøv først miljøvariabel, så config fil
API_KEY = os.getenv("MOTORAPI_KEY") or CONFIG_API_KEY
if not API_KEY:
    raise RuntimeError("No MotorAPI key found. Set env var MOTORAPI_KEY or add config.py with API_KEY='...'")

#Fælles headers til alle requests
HEADERS = {
    "X-AUTH-TOKEN": API_KEY,
    "Accept": "application/json",
    "User-Agent": "dk-plate-reader/1.0",
}

#requesthåndtering med fejlcheck
def _safe_get(session: requests.Session, url: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        r = session.get(url, timeout=8)
        if r.status_code == 200:
            return r.json(), None
        if r.status_code == 404:
            return None, "404 Not Found"
        return None, f"{r.status_code}: {r.text[:200]}"
    except requests.RequestException as e:
        return None, str(e)

#Hent data for et reg nummer og returner som dict
def query_vehicle_data(reg: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"registration": reg}
    with requests.Session() as s:
        s.headers.update(HEADERS)

        for endpoint, key in [
            (f"{BASE_URL}/vehicles/{reg}", "vehicle"),
            (f"{BASE_URL}/vehicles/{reg}/environment", "environment"),
            (f"{BASE_URL}/vehicles/{reg}/equipment", "equipment"),
        ]:
            data, err = _safe_get(s, endpoint)
            if err:
                result[f"{key}_error"] = err
            else:
                result[key] = data
    return result
