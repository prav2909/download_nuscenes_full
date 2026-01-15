import requests
import os
import hashlib
from tqdm import tqdm
import tarfile
import json
import sys

# ================= CONFIGURATION =================
USER_EMAIL = "USERNAME"
PASSWORD = "PASSWORD"
OUTPUT_DIR = "OUT_DIR"
REGION = 'us'  # 'us' or 'asia'
DELETE_AFTER_EXTRACT = True  # Set to True to save disk space
# =================================================

DOWNLOAD_FILES = {
    "v1.0-trainval_meta.tgz": "537d3954ec34e5bcb89a35d4f6fb0d4a",
    "v1.0-trainval01_blobs.tgz": "cbf32d2ea6996fc599b32f724e7ce8f2",
    "v1.0-trainval02_blobs.tgz": "aeecea4878ec3831d316b382bb2f72da",
    "v1.0-trainval03_blobs.tgz": "595c29528351060f94c935e3aaf7b995",
    "v1.0-trainval04_blobs.tgz": "b55eae9b4aa786b478858a3fc92fb72d",
    "v1.0-trainval05_blobs.tgz": "1c815ed607a11be7446dcd4ba0e71ed0",
    "v1.0-trainval06_blobs.tgz": "7273eeea36e712be290472859063a678",
    "v1.0-trainval07_blobs.tgz": "46674d2b2b852b7a857d2c9a87fc755f",
    "v1.0-trainval08_blobs.tgz": "37524bd4edee2ab99678909334313adf",
    "v1.0-trainval09_blobs.tgz": "a7fcd6d9c0934e4052005aa0b84615c0",
    "v1.0-trainval10_blobs.tgz": "31e795f2c13f62533c727119b822d739",
}

def get_id_token(username, password):
    print("Authenticating with nuScenes...")
    headers = {"Content-Type": "application/x-amz-json-1.1", "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth"}
    payload = json.dumps({
        "AuthFlow": "USER_PASSWORD_AUTH",
        "ClientId": "7fq5jvs5ffs1c50hd3toobb3b9",
        "AuthParameters": {"USERNAME": username, "PASSWORD": password}
    })
    res = requests.post("https://cognito-idp.us-east-1.amazonaws.com/", headers=headers, data=payload)
    if res.status_code == 200:
        return res.json()["AuthenticationResult"]["IdToken"]
    print(f"Auth Failed: {res.text}")
    return None

def get_fresh_url(filename, token):
    api_url = f'https://o9k5xn5546.execute-api.us-east-1.amazonaws.com/v1/archives/v1.0/{filename}?region={REGION}&project=nuScenes'
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    res = requests.get(api_url, headers=headers)
    return res.json().get('url') if res.status_code == 200 else None

def check_md5(filepath, expected_md5):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest() == expected_md5

def main():
    token = get_id_token(USER_EMAIL, PASSWORD)
    if not token: sys.exit(1)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for filename, expected_md5 in DOWNLOAD_FILES.items():
        save_path = os.path.join(OUTPUT_DIR, filename)
        
        # 1. Verification
        if os.path.exists(save_path):
            print(f"Verifying existing {filename}...")
            if check_md5(save_path, expected_md5):
                print("Already downloaded and verified. Proceeding to extraction...")
            else:
                print("MD5 mismatch. Re-downloading...")
                os.remove(save_path)

        # 2. Download (if needed)
        if not os.path.exists(save_path):
            url = get_fresh_url(filename, token)
            if not url:
                print(f"Error: Failed to get link for {filename}. Session might have expired.")
                token = get_id_token(USER_EMAIL, PASSWORD) # Try one re-auth
                url = get_fresh_url(filename, token)
                if not url: continue

            print(f"Downloading {filename}...")
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(save_path, 'wb') as f, tqdm(total=total_size, unit='iB', unit_scale=True, desc=filename) as pbar:
                for data in response.iter_content(chunk_size=1024*1024):
                    f.write(data)
                    pbar.update(len(data))
            
            if not check_md5(save_path, expected_md5):
                print(f"CRITICAL: {filename} MD5 verification failed after download!")
                continue

        # 3. Extraction
        print(f"Extracting {filename} to {OUTPUT_DIR}...")
        try:
            with tarfile.open(save_path, "r:gz") as tar:
                tar.extractall(path=OUTPUT_DIR)
            print(f"Successfully extracted {filename}.")
            
            if DELETE_AFTER_EXTRACT:
                os.remove(save_path)
                print(f"Deleted {filename} to save space.")
        except Exception as e:
            print(f"Extraction failed for {filename}: {e}")

    print("\nProcessing Complete!")

if __name__ == "__main__":
    main()