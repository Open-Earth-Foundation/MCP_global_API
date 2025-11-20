"""
MCP Server for CityCatalyst Global API
Exposes tools to interact with the CityCatalyst Global API endpoints.
Transport: STDIO (default - subprocess via stdin/stdout)

Requirements:
    pip install fastmcp httpx
"""
from fastmcp import FastMCP
from globalapi_api_client import get_health, get_city_emissions as get_city_emissions_api, get_city_area, get_catalogue, get_gpc_reference_numbers_by_source as get_gpc_reference_numbers_by_source_api

# Create the MCP server instance
mcp = FastMCP("CityCatalyst Global API")


@mcp.tool()
def health_check() -> dict:
    """
    Check the health of the CityCatalyst Global API service.
    Tests the database connection and returns service status.
    
    Returns:
        dict: Health status information
    """
    import sys
    print(f"\n>>> [MCP SERVER] Tool called: health_check", file=sys.stderr)
    try:
        result = get_health()
        print(f"    Result: {result}", file=sys.stderr)
        return result
    except Exception as e:
        print(f"    Error: {e}", file=sys.stderr)
        raise


@mcp.tool()
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
    import sys
    print(f"\n>>> [MCP SERVER] Tool called: get_city_emissions", file=sys.stderr)
    print(f"    Parameters: source={source}, city={city}, year={year}, gpc_reference_number={gpc_reference_number}, gwp={gwp}", file=sys.stderr)
    try:
        result = get_city_emissions_api(source=source, city=city, year=year, gpc_reference_number=gpc_reference_number, gwp=gwp)
        print(f"    Result: Total CO2eq (100yr) = {result}", file=sys.stderr)
        return result
    except Exception as e:
        print(f"    Error: {e}", file=sys.stderr)
        raise


@mcp.tool()
def get_city_area_tool(locode: str) -> dict:
    """
    Get the area of a city by its locode.
    Retrieve the area of a city in square kilometers.
    
    Args:
        locode: Unique identifier for the city (e.g., "BR SER" for São Paulo)
    
    Returns:
        dict: City area information in square kilometers
    """
    import sys
    print(f"\n>>> [MCP SERVER] Tool called: get_city_area", file=sys.stderr)
    print(f"    Parameters: locode={locode}", file=sys.stderr)
    try:
        result = get_city_area(locode=locode)
        print(f"    Result: {result}", file=sys.stderr)
        return result
    except Exception as e:
        print(f"    Error: {e}", file=sys.stderr)
        raise


@mcp.tool()
def get_data_catalogue(format: str = None) -> dict:
    """
    Get the data catalogue from CityCatalyst Global API.
    Retrieves the list of available datasources.
    
    Args:
        format: Optional format parameter. Supports "csv" for CSV format.
    
    Returns:
        dict: Catalogue data with list of datasources
    """
    import sys
    print(f"\n>>> [MCP SERVER] Tool called: get_data_catalogue", file=sys.stderr)
    print(f"    Parameters: format={format}", file=sys.stderr)
    try:
        result = get_catalogue(format=format)
        print(f"    Result: Retrieved catalogue data", file=sys.stderr)
        return result
    except Exception as e:
        print(f"    Error: {e}", file=sys.stderr)
        raise


@mcp.tool()
def get_gpc_refs_by_source(source: str) -> list:
    """
    Get all GPC reference numbers covered by a particular source.
    Filters the catalogue data to find all GPC reference numbers for the specified source.
    
    Args:
        source: Data source name (e.g., "SEEG")
    
    Returns:
        list: List of unique GPC reference numbers for the specified source, sorted alphabetically
    """
    import sys
    print(f"\n>>> [MCP SERVER] Tool called: get_gpc_refs_by_source", file=sys.stderr)
    print(f"    Parameters: source={source}", file=sys.stderr)
    try:
        result = get_gpc_reference_numbers_by_source_api(source=source)
        print(f"    Result: Found {len(result)} GPC reference numbers", file=sys.stderr)
        return result
    except Exception as e:
        print(f"    Error: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    # Run the MCP server using the default STDIO transport
    import sys
    print("=" * 60, file=sys.stderr)
    print("MCP SERVER STARTING - CityCatalyst Global API", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Transport: STDIO (stdin/stdout)", file=sys.stderr)
    print(f"Available tools: health_check, get_city_emissions, get_city_area, get_catalogue, get_gpc_refs_by_source", file=sys.stderr)
    print(f"API Base URL: https://ccglobal.openearth.dev", file=sys.stderr)
    print(f"Waiting for client requests...", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    mcp.run()

