"""
API client for CityCatalyst Global API
Base URL is configurable via the GLOBALAPI_BASE_URL environment variable.
"""
import os

import httpx

BASE_URL = os.getenv("GLOBALAPI_BASE_URL", "https://ccglobal.openearth.dev").rstrip("/")


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
        format: Optional format parameter (e.g., "csv"). When "csv", returns raw text.
    
    Returns:
        dict or str: Catalogue data with list of datasources, or CSV text if format="csv"
    """
    params = {"format": format} if format else {}
    response = httpx.get(f"{BASE_URL}/api/v0/catalogue", params=params, timeout=10.0)
    response.raise_for_status()
    if format and str(format).lower() == "csv":
        # Endpoint returns CSV when format=csv; surface the raw text instead of JSON parsing.
        return response.text
    return response.json()


def get_cities_by_country(country_code: str) -> dict:
    """
    Get a list of cities (locodes) for a given country.

    Args:
        country_code: ISO alpha-2 country code (e.g., "BR", "AR")

    Returns:
        dict: Response from the /api/v0/ccra/city/{country_code} endpoint.
    """
    response = httpx.get(f"{BASE_URL}/api/v0/ccra/city/{country_code}", timeout=10.0)
    response.raise_for_status()
    return response.json()


def list_available_country_codes(prefer_iso2: bool = True) -> list[str]:
    """
    Derive available country codes from the catalogue.

    Args:
        prefer_iso2: When True, return only 2-letter codes; otherwise include any codes seen.

    Returns:
        Sorted list of unique country codes present in catalogue datasources.
    """
    catalogue = get_catalogue()
    datasources = catalogue.get("datasources", []) if isinstance(catalogue, dict) else []
    codes = set()
    for ds in datasources:
        loc = str(ds.get("geographical_location", "")).strip()
        if not loc:
            continue
        # Some entries might have mixed or longer strings; optionally filter to ISO2 length
        if prefer_iso2 and len(loc) == 2:
            codes.add(loc.upper())
        elif not prefer_iso2:
            codes.add(loc.upper())
    return sorted(codes)


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


def list_datasources(filter_text: str | None = None) -> list[dict]:
    """
    List datasources from the catalogue with key metadata for discovery.

    Args:
        filter_text: Optional case-insensitive filter applied to publisher_id,
            datasource_name, or api_endpoint.

    Returns:
        list of dicts: Each entry contains publisher_id (source), gpc_reference_number,
        start/end/latest years, spatial_resolution, geographical_location,
        and api_endpoint.
    """
    catalogue = get_catalogue()
    datasources = catalogue.get("datasources", []) if isinstance(catalogue, dict) else []
    results: list[dict] = []
    needle = filter_text.lower() if filter_text else None

    for ds in datasources:
        publisher_id = ds.get("publisher_id", "")
        datasource_name = ds.get("datasource_name", "")
        api_endpoint = ds.get("api_endpoint", "")
        if needle:
            blob = f"{publisher_id} {datasource_name} {api_endpoint}".lower()
            if needle not in blob:
                continue

        results.append(
            {
                "publisher_id": publisher_id,
                "datasource_name": datasource_name,
                "gpc_reference_number": ds.get("gpc_reference_number"),
                "start_year": ds.get("start_year"),
                "end_year": ds.get("end_year"),
                "latest_accounting_year": ds.get("latest_accounting_year"),
                "spatial_resolution": ds.get("spatial_resolution"),
                "geographical_location": ds.get("geographical_location"),
                "api_endpoint": api_endpoint,
            }
        )

    return results


def get_source_years(source: str) -> dict | None:
    """
    Get year coverage for a datasource by matching catalogue entries.

    Args:
        source: Source identifier (matches publisher_id, datasource_name, or api_endpoint).

    Returns:
        dict with start_year, end_year, latest_accounting_year, and gpc_reference_number,
        or None if no match is found.
    """
    catalogue = get_catalogue()
    datasources = catalogue.get("datasources", []) if isinstance(catalogue, dict) else []
    source_upper = source.upper()

    for ds in datasources:
        publisher_id = str(ds.get("publisher_id", ""))
        datasource_name = str(ds.get("datasource_name", ""))
        api_endpoint = str(ds.get("api_endpoint", ""))
        if (
            source_upper in publisher_id.upper()
            or source_upper in datasource_name.upper()
            or source_upper in api_endpoint.upper()
        ):
            return {
                "publisher_id": publisher_id,
                "datasource_name": datasource_name,
                "gpc_reference_number": ds.get("gpc_reference_number"),
                "start_year": ds.get("start_year"),
                "end_year": ds.get("end_year"),
                "latest_accounting_year": ds.get("latest_accounting_year"),
                "geographical_location": ds.get("geographical_location"),
            }

    return None

