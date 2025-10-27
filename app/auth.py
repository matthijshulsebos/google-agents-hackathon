import os
import json
import base64
from typing import Optional

CREDS_ENV_PATH = "GOOGLE_APPLICATION_CREDENTIALS"
CREDS_ENV_JSON = "GOOGLE_APPLICATION_CREDENTIALS_JSON"
CREDS_ENV_B64 = "GOOGLE_APPLICATION_CREDENTIALS_BASE64"
CREDS_TMP_PATH = "/tmp/adc.json"


def _pick_json_in_dir(dir_path: str) -> Optional[str]:
    try:
        candidates = [
            os.path.join(dir_path, f)
            for f in os.listdir(dir_path)
            if f.lower().endswith(".json") and os.path.isfile(os.path.join(dir_path, f))
        ]
        if not candidates:
            return None
        # Prefer filenames containing common keywords
        preferred = [p for p in candidates if any(k in os.path.basename(p).lower() for k in ["key", "cred", "service", "account"])]
        if preferred:
            return preferred[0]
        return candidates[0]
    except Exception:
        return None


def setup_adc_from_env() -> Optional[str]:
    """
    Ensure Application Default Credentials are available by inspecting environment variables.

    Priority:
    1) If GOOGLE_APPLICATION_CREDENTIALS points to an existing file, keep as-is.
       - If it points to a directory, attempt to locate a single JSON file within and use that.
       - If it points to a non-existent path or unusable location, unset it and continue.
    2) If GOOGLE_APPLICATION_CREDENTIALS_JSON has raw JSON, write to /tmp/adc.json and set path env.
    3) If GOOGLE_APPLICATION_CREDENTIALS_BASE64 has base64-encoded JSON, decode, write to /tmp/adc.json and set path env.

    Returns the effective credentials file path, or None if not configured.
    """
    # Case 1: explicit path provided
    path = os.getenv(CREDS_ENV_PATH)
    if path:
        if os.path.isfile(path):
            return path
        if os.path.isdir(path):
            picked = _pick_json_in_dir(path)
            if picked and os.path.isfile(picked):
                os.environ[CREDS_ENV_PATH] = picked
                return picked
            else:
                print(f"[WARN] {CREDS_ENV_PATH} points to a directory with no usable JSON: '{path}'")
                os.environ.pop(CREDS_ENV_PATH, None)
        else:
            # Not a file and not a directory (or does not exist)
            print(f"[WARN] {CREDS_ENV_PATH} points to a non-existent or invalid path: '{path}'")
            os.environ.pop(CREDS_ENV_PATH, None)

    # Case 2: raw JSON
    raw_json = os.getenv(CREDS_ENV_JSON)
    if raw_json:
        try:
            obj = json.loads(raw_json)
            with open(CREDS_TMP_PATH, "w") as f:
                json.dump(obj, f)
            os.environ[CREDS_ENV_PATH] = CREDS_TMP_PATH
            return CREDS_TMP_PATH
        except Exception as e:
            print(f"[WARN] Failed to use {CREDS_ENV_JSON}: {e}")

    # Case 3: base64 JSON
    b64 = os.getenv(CREDS_ENV_B64)
    if b64:
        try:
            data = base64.b64decode(b64)
            obj = json.loads(data.decode("utf-8"))
            with open(CREDS_TMP_PATH, "w") as f:
                json.dump(obj, f)
            os.environ[CREDS_ENV_PATH] = CREDS_TMP_PATH
            return CREDS_TMP_PATH
        except Exception as e:
            print(f"[WARN] Failed to use {CREDS_ENV_B64}: {e}")

    # If we reach here, no usable creds provided.
    return None
