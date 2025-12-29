"""
Mock Electrical Materials Database
Simulates Airtable/supplier data for the MVP
"""

MATERIALS_DATABASE = [
    {
        "id": "MAT001",
        "name": "Clipsal Double GPO 10A",
        "sku": "CL-GPO-10A",
        "base_cost": 12.50,
        "category": "Power Points",
        "keywords": ["gpo", "outlet", "power point", "clipsal", "double", "socket"]
    },
    {
        "id": "MAT002",
        "name": "LED Downlight 10W Warm White",
        "sku": "LED-DL-10W",
        "base_cost": 25.00,
        "category": "Lighting",
        "keywords": ["led", "downlight", "light", "ceiling", "warm", "10w"]
    },
    {
        "id": "MAT003",
        "name": "2.5mm Twin & Earth Cable (per meter)",
        "sku": "CAB-2.5-TE",
        "base_cost": 3.50,
        "category": "Cables",
        "keywords": ["cable", "2.5mm", "twin", "earth", "wire", "wiring"]
    },
    {
        "id": "MAT004",
        "name": "20A Circuit Breaker",
        "sku": "CB-20A",
        "base_cost": 18.00,
        "category": "Switchboard",
        "keywords": ["breaker", "circuit", "20a", "mcb", "switchboard"]
    },
    {
        "id": "MAT005",
        "name": "4mm Twin & Earth Cable (per meter)",
        "sku": "CAB-4-TE",
        "base_cost": 5.50,
        "category": "Cables",
        "keywords": ["cable", "4mm", "twin", "earth", "wire", "heavy"]
    },
    {
        "id": "MAT006",
        "name": "Clipsal Single GPO 10A",
        "sku": "CL-GPO-S10A",
        "base_cost": 8.50,
        "category": "Power Points",
        "keywords": ["gpo", "outlet", "power point", "clipsal", "single", "socket"]
    },
    {
        "id": "MAT007",
        "name": "Light Switch Single Gang",
        "sku": "SW-1G",
        "base_cost": 6.00,
        "category": "Switches",
        "keywords": ["switch", "light", "single", "gang", "wall"]
    },
    {
        "id": "MAT008",
        "name": "Light Switch Double Gang",
        "sku": "SW-2G",
        "base_cost": 9.50,
        "category": "Switches",
        "keywords": ["switch", "light", "double", "gang", "wall", "two"]
    },
    {
        "id": "MAT009",
        "name": "Smoke Detector 240V",
        "sku": "SD-240V",
        "base_cost": 35.00,
        "category": "Safety",
        "keywords": ["smoke", "detector", "alarm", "fire", "safety", "240v"]
    },
    {
        "id": "MAT010",
        "name": "Ceiling Fan with Light Kit",
        "sku": "FAN-CL",
        "base_cost": 150.00,
        "category": "Fans",
        "keywords": ["fan", "ceiling", "light", "kit", "breeze"]
    },
    {
        "id": "MAT011",
        "name": "RCD Safety Switch 30mA",
        "sku": "RCD-30MA",
        "base_cost": 85.00,
        "category": "Switchboard",
        "keywords": ["rcd", "safety", "switch", "30ma", "protection"]
    },
    {
        "id": "MAT012",
        "name": "Weatherproof GPO IP54",
        "sku": "WP-GPO",
        "base_cost": 28.00,
        "category": "Power Points",
        "keywords": ["weatherproof", "outdoor", "gpo", "ip54", "external"]
    },
    {
        "id": "MAT013",
        "name": "Electrical Junction Box",
        "sku": "JB-STD",
        "base_cost": 4.50,
        "category": "Accessories",
        "keywords": ["junction", "box", "connection", "join"]
    },
    {
        "id": "MAT014",
        "name": "Conduit 20mm (per meter)",
        "sku": "CON-20MM",
        "base_cost": 2.00,
        "category": "Accessories",
        "keywords": ["conduit", "pipe", "20mm", "protection"]
    },
    {
        "id": "MAT015",
        "name": "Pool Pump Isolator Switch",
        "sku": "ISO-POOL",
        "base_cost": 45.00,
        "category": "Switches",
        "keywords": ["pool", "pump", "isolator", "switch", "outdoor"]
    }
]


def search_materials(query: str) -> list:
    """
    Search materials database using keyword matching.
    Returns list of matching materials with relevance scores.
    """
    query_terms = query.lower().split()
    results = []
    
    for material in MATERIALS_DATABASE:
        score = 0
        keywords = material["keywords"]
        name_lower = material["name"].lower()
        
        for term in query_terms:
            # Check keywords
            for keyword in keywords:
                if term in keyword or keyword in term:
                    score += 2
            # Check name
            if term in name_lower:
                score += 1
        
        if score > 0:
            results.append({
                **material,
                "relevance_score": score
            })
    
    # Sort by relevance
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results


def get_material_by_id(material_id: str) -> dict | None:
    """Get a specific material by ID."""
    for material in MATERIALS_DATABASE:
        if material["id"] == material_id:
            return material
    return None


def get_all_materials() -> list:
    """Return all materials in the database."""
    return MATERIALS_DATABASE
