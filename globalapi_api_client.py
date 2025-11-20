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

