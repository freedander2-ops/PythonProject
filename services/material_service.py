from data.materials import MATERIALS

def calculate_material_needs(category: str, subtype: str, area: float) -> dict:
    """Бизнес-логика расчета материалов"""
    if category not in MATERIALS or subtype not in MATERIALS[category]:
        return None

    params = MATERIALS[category][subtype]

    result = {
        "category": category,
        "subtype": subtype,
        "area": area,
        "waste_percent": params["waste"],
        "total_count": 0
    }

    if category == "плитка":
        count_per_m2 = 1 / params["size"]
        result["total_count"] = area * count_per_m2 * (1 + params["waste"] / 100)
    else:
        result["total_count"] = area * params["count"] * (1 + params["waste"] / 100)

    return result
