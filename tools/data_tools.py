"""Data-access tool functions for agent tool-calling.

All queries are scoped to the currently active case. The case_id is set on the
gateway at session start — tools don't need to specify it.
"""

from __future__ import annotations

import json
from typing import Any

from data.catalog import DataCatalog
from data.gateway import DataGateway

_gateway: DataGateway | None = None
_catalog: DataCatalog | None = None

_MAX_CHARS = 3000


def init_tools(gateway: DataGateway, catalog: DataCatalog) -> None:
    global _gateway, _catalog
    _gateway = gateway
    _catalog = catalog


def list_available_tables() -> str:
    """List all data tables available for the current case."""
    if _catalog is None:
        return "Data unavailable"
    tables = _catalog.list_tables()
    if _gateway is not None:
        case_id = _gateway.get_case_id()
        if case_id:
            # Show only tables that exist for this case
            case_tables = _gateway.list_tables()
            header = f"Tables for case {case_id}:\n"
            return header + "\n".join(case_tables) if case_tables else header + "No tables available"
    return "\n".join(tables) if tables else "No tables available"


def get_table_schema(table_name: str) -> str:
    """Get the column schema for a specific table."""
    if _catalog is None:
        return "Data unavailable"
    schema = _catalog.get_schema(table_name)
    if schema is None:
        return "Data unavailable"
    return json.dumps(schema, indent=2)


def query_table(
    table_name: str,
    filter_column: str = "",
    filter_value: str = "",
    limit: int = 50,
) -> str:
    """Query a data table for the current case. All data is scoped to the active case."""
    if _gateway is None:
        return "Data unavailable"

    filters: dict[str, Any] | None = None
    if filter_column and filter_value:
        filters = {filter_column: filter_value}

    rows = _gateway.query(table_name, filters=filters, limit=limit)
    if rows is None:
        return f"Data unavailable: table '{table_name}' not found for current case."

    if not rows:
        return f"No rows matching filter in '{table_name}'."

    text = json.dumps(rows, indent=2, default=str)
    if len(text) > _MAX_CHARS:
        text = text[:_MAX_CHARS] + "\n... (truncated)"
    return text
