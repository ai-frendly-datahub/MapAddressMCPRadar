#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from typing import Any


TOOLS = [
    {
        "name": "navermap_geocode",
        "title": "Naver Map Geocode",
        "description": "Return deterministic Naver geocode fixture results.",
        "inputSchema": {"type": "object", "additionalProperties": True},
    },
    {
        "name": "navermap_reverse_geocode",
        "title": "Naver Map Reverse Geocode",
        "description": "Return deterministic Naver reverse geocode fixture results.",
        "inputSchema": {"type": "object", "additionalProperties": True},
    },
    {
        "name": "navermap_get_directions",
        "title": "Naver Map Directions",
        "description": "Return deterministic Naver directions fixture results.",
        "inputSchema": {"type": "object", "additionalProperties": True},
    },
    {
        "name": "navermap_get_static_map",
        "title": "Naver Map Static Map",
        "description": "Return deterministic Naver static map fixture results.",
        "inputSchema": {"type": "object", "additionalProperties": True},
    },
]


RESULTS: dict[str, dict[str, Any]] = {
    "navermap_geocode": {
        "title": "Naver Map geocode fixture",
        "url": "https://example.test/mapaddress/navermap/geocode-fixture",
        "summary": "Fixture-only Naver geocode result for collector normalization.",
        "address": "fixture-address-001",
        "source": "fixture",
    },
    "navermap_reverse_geocode": {
        "title": "Naver Map reverse-geocode fixture",
        "url": "https://example.test/mapaddress/navermap/reverse-geocode-fixture",
        "summary": "Fixture-only Naver reverse geocode result for collector normalization.",
        "address": "fixture-address-002",
        "source": "fixture",
    },
    "navermap_get_directions": {
        "title": "Naver Map directions fixture",
        "url": "https://example.test/mapaddress/navermap/directions-fixture",
        "summary": "Fixture-only Naver directions result for collector normalization.",
        "address": "fixture-route-001",
        "source": "fixture",
    },
    "navermap_get_static_map": {
        "title": "Naver Map static-map fixture",
        "url": "https://example.test/mapaddress/navermap/static-map-fixture",
        "summary": "Fixture-only Naver static map result for collector normalization.",
        "address": "fixture-static-001",
        "source": "fixture",
    },
}


def write_message(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def response_for(message: dict[str, Any]) -> dict[str, Any] | None:
    request_id = message.get("id")
    method = message.get("method")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "fake-flor3z-navermap-mcp", "version": "0.0.0"},
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = message.get("params") if isinstance(message.get("params"), dict) else {}
        tool_name = params.get("name")
        result = RESULTS.get(tool_name)
        if result is None:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"isError": True, "content": [{"type": "text", "text": f"Unsupported tool: {tool_name}"}]},
            }
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                "structuredContent": result,
            },
        }
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"Unsupported method: {method}"},
    }


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(message, dict):
            continue
        response = response_for(message)
        if response is not None:
            write_message(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
