"""
API client for CityCatalyst Global API
Base URL: https://ccglobal.openearth.dev
"""
import httpx

BASE_URL = "https://ccglobal.openearth.dev"


def get_health() -> dict:
    """
    Check the health of the CityCatalyst Global API service.
    
    Returns:
        dict: Health status information
    """
    response = httpx.get(f"{BASE_URL}/health", timeout=10.0)
    response.raise_for_status()
    return response.json()


def get_city_emissions(source: str, city: str, year: str, gpc_reference_number: str, gwp: str = "ar5") -> str:
    """
    Get total CO2eq emissions from CityCatalyst Global API.
    
    Args:
        source: Data source (e.g., "SEEG")
        city: City identifier (e.g., "BR SER")
        year: Year (e.g., "2022")
        gpc_reference_number: GPC reference number (e.g., "II.1.1")
        gwp: Global Warming Potential standard (default: "ar5")
    
    Returns:
        str: Total CO2eq emissions (100yr) value
    """
    import urllib.parse
    
    # URL encode the city parameter
    city_encoded = urllib.parse.quote(city)
    
    # Build the URL path
    path = f"/api/v1/source/{source}/city/{city_encoded}/{year}/{gpc_reference_number}"
    params = {"gwp": gwp}
    
    response = httpx.get(f"{BASE_URL}{path}", params=params, timeout=10.0)
    response.raise_for_status()
    data = response.json()
    
    # Extract and return total CO2eq emissions
    total_co2eq = data.get("totals", {}).get("emissions", {}).get("co2eq_100yr")
    
    return total_co2eq


def get_city_area(locode: str) -> dict:
    """
    Get the area of a city by its locode.
    
    Args:
        locode: Unique identifier for the city
    
    Returns:
        dict: City area in square kilometers
    """
    response = httpx.get(f"{BASE_URL}/api/v0/cityboundary/city/{locode}/area", timeout=10.0)
    response.raise_for_status()
    return response.json()


def get_catalogue(format: str = None) -> dict:
    """
    Get the data catalogue from CityCatalyst Global API.
    
    Args:
        format: Optional format parameter (e.g., "csv")
    
    Returns:
        dict: Catalogue data with list of datasources
    """
    params = {"format": format} if format else {}
    response = httpx.get(f"{BASE_URL}/api/v0/catalogue", params=params, timeout=10.0)
    response.raise_for_status()
    return response.json()


def get_gpc_reference_numbers_by_source(source: str) -> list:
    """
    Get all GPC reference numbers covered by a particular source.
    
    Args:
        source: Data source name (e.g., "SEEG" or "SEEGv2023")
    
    Returns:
        list: List of unique GPC reference numbers for the specified source, sorted alphabetically
    """
    catalogue = get_catalogue()
    
    # Extract GPC reference numbers for the specified source
    gpc_refs = set()
    
    # The catalogue has a "datasources" list
    if isinstance(catalogue, dict) and "datasources" in catalogue:
        for datasource in catalogue["datasources"]:
            # Match by various possible source identifiers
            datasource_name = datasource.get("datasource_name", "")
            publisher_id = datasource.get("publisher_id", "")
            api_endpoint = datasource.get("api_endpoint", "")
            
            # Check if source matches any of these fields (case-insensitive)
            source_upper = source.upper()
            if (source_upper in datasource_name.upper() or 
                source_upper in publisher_id.upper() or 
                source_upper in api_endpoint.upper() or
                f"/source/{source}/" in api_endpoint or
                f"/source/{source_upper}/" in api_endpoint):
                
                # Extract gpc_reference_number if present
                if "gpc_reference_number" in datasource and datasource["gpc_reference_number"]:
                    gpc_refs.add(datasource["gpc_reference_number"])
    
    return sorted(list(gpc_refs))

