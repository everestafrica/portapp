import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
PORT_BASE_URL = "https://api.getport.io/v1"
PORT_TOKEN = os.getenv("PORT_TOKEN")


def get_blueprint_entities(identifier: str) -> dict:
    url = f"{PORT_BASE_URL}/blueprints/{identifier}/entities"
    headers = {"Authorization": PORT_TOKEN}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def update_entity(blueprint_identifier: str, entity_identifier: str, data: dict) -> None:
    url = f"{PORT_BASE_URL}/blueprints/{blueprint_identifier}/entities/{entity_identifier}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": PORT_TOKEN,
    }
    response = requests.patch(url, headers=headers, json=data)
    response.raise_for_status()
    print(f"Updated entity {entity_identifier} with data: {data}")


def main() -> None:
    eol_frameworks = []
    active_frameworks = []

    # Fetch framework entities and categorize them
    framework_blueprint_data = get_blueprint_entities("framework")
    for entity in framework_blueprint_data["entities"]:
        identifier = entity["identifier"]
        state = entity["properties"]["state"]
        if state == "Active":
            active_frameworks.append(identifier)
        elif state == "EOL":
            eol_frameworks.append(identifier)

    # Fetch service entities and update the number of EOL packages
    service_blueprint_data = get_blueprint_entities("service")
    for entity in service_blueprint_data["entities"]:
        identifier = entity["identifier"]
        used_frameworks = entity.get("relations", {}).get("used_frameworks", [])
        eol_package_count = len(
            [fw for fw in used_frameworks if fw in eol_frameworks]
        )
        update_entity(
            "service",
            identifier,
            {"properties": {"number_of_eol_packages": eol_package_count}},
        )


if __name__ == "__main__":
    main()
