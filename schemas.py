metadata_schema = {
    "type": "object",
    "properties": {
        "size": {"type": "integer", "minimum": 0},
        "length": {"type": "integer", "minimum": 0},
    },
    "required": ["size", "length"],
}
