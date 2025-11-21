"""
MCP Server for CityCatalyst Global API
Exposes tools to interact with the CityCatalyst Global API endpoints.
Transport: STDIO (default - subprocess via stdin/stdout)

Requirements:
    pip install fastmcp httpx
"""
import argparse
import asyncio
import os
import sys

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse
from globalapi_api_client import (
    get_health,
    get_city_emissions as get_city_emissions_api,
    get_city_area,
    get_catalogue,
    get_gpc_reference_numbers_by_source as get_gpc_reference_numbers_by_source_api,
    list_datasources,
    get_source_years,
    get_cities_by_country,
    list_available_country_codes,
)

# Create the MCP server instance
mcp = FastMCP("CityCatalyst Global API")
API_BASE_URL = os.getenv("GLOBALAPI_BASE_URL", "https://ccglobal.openearth.dev").rstrip("/")
SERVICE_NAME = "CityCatalyst Global API MCP"


@mcp.custom_route("/", methods=["GET"])
async def root(_: Request) -> JSONResponse:
    """Lightweight root/health endpoint for Kubernetes and load balancer checks."""
    return JSONResponse(
        {
            "status": "ok",
            "service": SERVICE_NAME,
            "base_url": API_BASE_URL,
            "transport": os.getenv("MCP_TRANSPORT", "http"),
        }
    )


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


@mcp.tool()
def list_datasource_meta(filter_text: str = None) -> list:
    """
    List datasource metadata from the catalogue.
    Use this to discover valid sources, their coverage years, and GPC numbers.

    Args:
        filter_text: Optional substring to filter by source name or endpoint.

    Returns:
        list: Catalogue entries with publisher_id, gpc reference, year range, and endpoints.
    """
    import sys
    print(f"\n>>> [MCP SERVER] Tool called: list_datasource_meta", file=sys.stderr)
    print(f"    Parameters: filter_text={filter_text}", file=sys.stderr)
    try:
        result = list_datasources(filter_text=filter_text)
        print(f"    Result count: {len(result)}", file=sys.stderr)
        return result
    except Exception as e:
        print(f"    Error: {e}", file=sys.stderr)
        raise


@mcp.tool()
def get_source_coverage(source: str) -> dict:
    """
    Get year coverage and GPC reference number for a datasource.
    
    Args:
        source: Source identifier (matches publisher_id, datasource_name, or api_endpoint).
    
    Returns:
        dict: Coverage info including start_year, end_year, latest_accounting_year, gpc_reference_number.
    """
    import sys
    print(f"\n>>> [MCP SERVER] Tool called: get_source_coverage", file=sys.stderr)
    print(f"    Parameters: source={source}", file=sys.stderr)
    try:
        result = get_source_years(source=source)
        print(f"    Result: {result}", file=sys.stderr)
        return result or {}
    except Exception as e:
        print(f"    Error: {e}", file=sys.stderr)
        raise


@mcp.tool()
def list_cities_by_country(country_code: str) -> dict:
    """
    List locodes/cities for a given country using the CCRA cities endpoint.

    Args:
        country_code: ISO alpha-2 country code (e.g., "BR", "AR").

    Returns:
        dict: City list with locodes and names for the country.
    """
    import sys
    print(f"\n>>> [MCP SERVER] Tool called: list_cities_by_country", file=sys.stderr)
    print(f"    Parameters: country_code={country_code}", file=sys.stderr)
    try:
        result = get_cities_by_country(country_code=country_code)
        if isinstance(result, dict):
            count = len(result.get("cities", [])) if "cities" in result else len(result)
        else:
            count = None
        print(f"    Result count: {count}", file=sys.stderr)
        return result
    except Exception as e:
        print(f"    Error: {e}", file=sys.stderr)
        raise


@mcp.tool()
def list_country_codes(prefer_iso2: bool = True) -> list:
    """
    List available country codes present in the catalogue.

    Args:
        prefer_iso2: If True, return only 2-letter ISO-like codes; otherwise include all.

    Returns:
        list: Sorted unique country codes derived from catalogue datasources.
    """
    import sys
    print(f"\n>>> [MCP SERVER] Tool called: list_country_codes", file=sys.stderr)
    print(f"    Parameters: prefer_iso2={prefer_iso2}", file=sys.stderr)
    try:
        result = list_available_country_codes(prefer_iso2=prefer_iso2)
        print(f"    Result count: {len(result)}", file=sys.stderr)
        return result
    except Exception as e:
        print(f"    Error: {e}", file=sys.stderr)
        raise


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments/environment for server transport settings."""
    parser = argparse.ArgumentParser(
        description="Run CityCatalyst Global API MCP server"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "streamable-http", "sse"],
        default=os.getenv("MCP_TRANSPORT", "http"),
        help="Transport to run the MCP server on (default: http)",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("MCP_HOST", os.getenv("HOST", "0.0.0.0")),
        help="Host to bind when using HTTP/SSE transports (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("MCP_PORT") or os.getenv("PORT") or "8000"),
        help="Port to bind when using HTTP/SSE transports (default: PORT env or 8000)",
    )
    parser.add_argument(
        "--path",
        default=os.getenv("MCP_PATH", "/mcp"),
        help="Endpoint path for HTTP/SSE transports (default: /mcp or /sse)",
    )
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Suppress startup banner",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    transport = args.transport
    host = args.host
    port = args.port
    path = args.path
    show_banner = not args.no_banner

    banner_prefix = "=" * 60
    print(banner_prefix, file=sys.stderr)
    print(f"MCP SERVER STARTING - {SERVICE_NAME}", file=sys.stderr)
    print(banner_prefix, file=sys.stderr)

    tool_list = ", ".join(
        [
            "health_check",
            "get_city_emissions",
            "get_city_area_tool",
            "get_data_catalogue",
            "get_gpc_refs_by_source",
            "list_datasource_meta",
            "get_source_coverage",
            "list_cities_by_country",
            "list_country_codes",
        ]
    )

    if transport == "stdio":
        print("Transport: STDIO (stdin/stdout)", file=sys.stderr)
        print("Hint: For network clients, start with --transport http", file=sys.stderr)
        print(f"Available tools: {tool_list}", file=sys.stderr)
        print(f"API Base URL: {API_BASE_URL}", file=sys.stderr)
        print("Waiting for client requests...", file=sys.stderr)
        print(banner_prefix, file=sys.stderr)
        mcp.run(show_banner=show_banner)
    else:
        path_display = path or (
            "/mcp" if transport in ("http", "streamable-http") else "/sse"
        )
        print(
            f"Transport: {transport.upper()} over http://{host}:{port}{path_display}",
            file=sys.stderr,
        )
        print(f"Available tools: {tool_list}", file=sys.stderr)
        print(f"API Base URL: {API_BASE_URL}", file=sys.stderr)
        print("Waiting for client requests...", file=sys.stderr)
        print(banner_prefix, file=sys.stderr)
        asyncio.run(
            mcp.run_http_async(
                transport=transport,
                host=host,
                port=port,
                path=path,
                show_banner=show_banner,
            )
        )

