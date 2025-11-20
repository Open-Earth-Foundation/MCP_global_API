# CityCatalyst Global API - MCP Server

MCP server that exposes tools to interact with the [CityCatalyst Global API](https://ccglobal.openearth.dev).

## Setup

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install MCP server in Cursor:**
   ```bash
   fastmcp install cursor globalapi_mcp_server.py
   ```

## Project Structure

```
MCP_global_API/
├── gloablapi_mcp_server.py          # Main MCP server with tool definitions
├── globalapi_api_client.py          # API client functions
├── requirements.txt       
└── README.md             
```

## Available Tools

- **health_check()** - Check the health of the CityCatalyst Global API service
- **get_city_emissions(source, city, year, gpc_reference_number, gwp="ar5")** - Get total CO2eq emissions for a city from CityCatalyst Global API

## Adding New Tools

1. Add API client function in `globalapi_client.py`
2. Add MCP tool decorator in `globalapi_mcp_server.py` that calls the client function


## Test Prompts

* Check the health of the CityCatalyst Global API service
* Get city emissions for source SEEG, city BR SER, year 2022, and GPC reference number II.1.1


