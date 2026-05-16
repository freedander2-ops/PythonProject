from data.prices import PRICES

def calculate_estimate(work_name: str, area: float) -> dict:
    """Бизнес-логика расчета сметы"""
    if work_name not in PRICES:
        return None

    work_data = PRICES[work_name]
    total_work = area * work_data["work_price"]

    result = {
        "work_name": work_name,
        "area": area,
        "unit": work_data["unit"],
        "price_per_unit": work_data["work_price"],
        "total_price": total_work,
        "material_info": None
    }

    if work_data["material"] != "-":
        mat_total = area * work_data["usage"]
        result["material_info"] = {
            "name": work_data["material"],
            "amount": mat_total
        }

    return result

def find_similar_works(query: str, limit: int = 3) -> list:
    """Поиск похожих названий работ"""
    query = query.lower()
    return [w for w in PRICES if query in w][:limit]
