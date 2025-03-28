import requests
import time
import os
import sys

from influxdbgraphs.log import get_logger

logger = get_logger("setup_grafana")

INTERNAL_GRAFANA_HOST = os.getenv("INTERNAL_GRAFANA_HOST", "influxdbgraphs/grafana")
INTERNAL_GRAFANA_PORT = os.getenv("INTERNAL_GRAFANA_PORT", "3000")
GRAFANA_URL = f"http://{INTERNAL_GRAFANA_HOST}:{INTERNAL_GRAFANA_PORT}"
GRAFANA_USER = os.getenv("GRAFANA_USER", "admin")
GRAFANA_PASSWORD = os.getenv("GRAFANA_PASSWORD", "admin")
MAX_RETRIES = 30
RETRY_INTERVAL = 5
API_KEY_NAME = "panel-service"
API_KEY_ROLE = "Admin"
ENV_FILE_PATH = os.getenv("ENV_FILE_PATH", "./panel_service.env")
KEY_VAR_NAME = "GRAFANA_API_KEY"


def wait_for_grafana():
    logger.info("Waiting for Grafana to be available...")
    for i in range(MAX_RETRIES):
        try:
            response = requests.get(f"{GRAFANA_URL}/api/health")
            if response.status_code == 200:
                logger.info("Grafana is up and running!")
                return True
        except requests.exceptions.RequestException:
            pass

        logger.info(
            f"Attempt {i+1}/{MAX_RETRIES}: Grafana not ready, retrying in {RETRY_INTERVAL} seconds..."
        )
        time.sleep(RETRY_INTERVAL)

    logger.error("Grafana did not become available within the timeout period.")
    return False


def delete_existing_api_key():
    logger.info(f"Checking for existing API key '{API_KEY_NAME}'...")
    headers = {"Content-Type": "application/json"}
    auth = (GRAFANA_USER, GRAFANA_PASSWORD)

    try:
        # Get all API keys
        response = requests.get(
            f"{GRAFANA_URL}/api/auth/keys", headers=headers, auth=auth
        )

        if response.status_code == 200:
            keys = response.json()
            for key in keys:
                if key.get("name") == API_KEY_NAME:
                    key_id = key.get("id")
                    logger.info(f"Found existing API key '{API_KEY_NAME}' with id {key_id}. Deleting...")

                    # Delete the existing key
                    delete_response = requests.delete(
                        f"{GRAFANA_URL}/api/auth/keys/{key_id}", auth=auth
                    )

                    if delete_response.status_code == 200:
                        logger.info(f"Successfully deleted existing API key '{API_KEY_NAME}'")
                        return True
                    else:
                        logger.error(f"Failed to delete existing API key. Status code: {delete_response.status_code}")
                        logger.error(f"Response: {delete_response.text}")
                        return False

            logger.info(f"No existing API key named '{API_KEY_NAME}' found.")
            return True
        else:
            logger.error(f"Failed to get API keys. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking for existing API keys: {e}")
        return False


def create_api_key():
    logger.info(f"Creating API key '{API_KEY_NAME}'...")

    headers = {"Content-Type": "application/json"}
    auth = (GRAFANA_USER, GRAFANA_PASSWORD)
    data = {
        "name": API_KEY_NAME,
        "role": API_KEY_ROLE,
        "secondsToLive": 10 * 365 * 24 * 60 * 60,  # 10 years
    }

    try:
        response = requests.post(
            f"{GRAFANA_URL}/api/auth/keys", headers=headers, auth=auth, json=data
        )

        if response.status_code == 200:
            key = response.json().get("key")
            logger.info("API key created successfully!")
            return key
        else:
            logger.error(f"Failed to create API key. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating API key: {e}")
        return None


def update_env_file(api_key):
    try:
        os.makedirs(os.path.dirname(ENV_FILE_PATH), exist_ok=True)

        # Check if the key already exists
        if not os.path.exists(ENV_FILE_PATH):
            logger.info(f"Creating new env file at {ENV_FILE_PATH}")
            with open(ENV_FILE_PATH, "w") as f:
                f.write(f"{KEY_VAR_NAME}={api_key}\n")
            return True

        with open(ENV_FILE_PATH, "r") as f:
            lines = f.readlines()

        key_exists = False
        for i, line in enumerate(lines):
            if line.startswith(f"{KEY_VAR_NAME}="):
                lines[i] = f"{KEY_VAR_NAME}={api_key}\n"
                key_exists = True
                break

        if not key_exists:
            lines.append(f"{KEY_VAR_NAME}={api_key}\n")

        with open(ENV_FILE_PATH, "w") as f:
            f.writelines(lines)

        logger.info(f"Updated {ENV_FILE_PATH} with the new API key.")
        return True
    except Exception as e:
        logger.error(f"Error updating env file: {e}")
        return False


def check_existing_key_from_env():
    """Check if we already have a valid key in the env file"""
    if not os.path.exists(ENV_FILE_PATH):
        logger.info("No environment file found.")
        return None

    try:
        with open(ENV_FILE_PATH, "r") as f:
            for line in f:
                if line.startswith(f"{KEY_VAR_NAME}="):
                    key = line.strip().split("=", 1)[1]
                    logger.info("Found existing API key in environment file.")

                    # Validate key with a test request
                    try:
                        headers = {"Authorization": f"Bearer {key}"}
                        response = requests.get(f"{GRAFANA_URL}/api/org", headers=headers)
                        if response.status_code == 200:
                            logger.info("Existing API key is valid.")
                            return key
                        else:
                            logger.info("Existing API key is invalid.")
                    except requests.exceptions.RequestException:
                        logger.info("Could not validate existing API key.")

                    return None
    except Exception as e:
        logger.error(f"Error reading env file: {e}")

    return None


def main():
    if not wait_for_grafana():
        sys.exit(1)

    # First check if we have a valid key already
    existing_key = check_existing_key_from_env()
    if existing_key:
        logger.info("Using existing API key.")
        return

    # If no valid key exists, create a new one (after deleting any existing one)
    delete_existing_api_key()
    api_key = create_api_key()
    if not api_key:
        sys.exit(1)

    if update_env_file(api_key):
        logger.info("Setup completed successfully!")
    else:
        logger.error("Failed to update environment file.")
        sys.exit(1)


if __name__ == "__main__":
    main()
