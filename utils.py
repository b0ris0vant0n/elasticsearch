def build_category_map(categories):
    category_map = {}
    for category in categories:
        category_id = category.get("id")
        category_name = category.text
        category_map[category_id] = category_name
    return category_map


def get_category_path(category_id, category_map):
    path = []
    current_id = category_id
    while current_id in category_map:
        category = category_map[current_id]
        path.append(category["name"])
        current_id = category["parent_id"]
    return path[::-1]


def parse_offer(offer_elem, category_map):
    category_id = int(offer_elem.findtext("categoryId"))
    category_path = get_category_path(category_id, category_map)

    category_lvl_1 = category_path[0] if len(category_path) > 0 else None
    category_lvl_2 = category_path[1] if len(category_path) > 1 else None
    category_lvl_3 = category_path[2] if len(category_path) > 2 else None
    category_remaining = "/".join(category_path[3:]) if len(category_path) > 3 else None

    product_data = {
        "uuid": offer_elem.get("id"),
        "description": offer_elem.findtext("description"),
        "brand": offer_elem.findtext("vendor"),
        "title": offer_elem.findtext("name"),
        "barcode": offer_elem.findtext("barcode") or '',
        "category_id": category_id,
        "category_lvl_1": category_lvl_1,
        "category_lvl_2": category_lvl_2,
        "category_lvl_3": category_lvl_3,
        "category_remaining": category_remaining,
        "currency": offer_elem.findtext("currencyId"),
        "first_image_url": offer_elem.findtext("picture"),
        "price_before_discounts": float(offer_elem.findtext("oldprice") or 0.0),
        "price_after_discounts": float(offer_elem.findtext("price") or 0.0),
    }
    return product_data
