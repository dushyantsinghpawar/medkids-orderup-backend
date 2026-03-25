# Valid diet preferences and restrictions
VALID_DIET_PREFERENCES = {
    "vegan",
    "vegetarian",
    "pescatarian",
    "keto",
    "paleo",
    "gluten-free",
    "dairy-free",
    "nut-free",
    "kosher",
    "halal",
    "organic",
    "low-sugar",
}

def parse_diet_preferences(raw_input):
    """Parse comma-separated string to list and validate."""
    if not raw_input:
        return []
    
    items = [item.strip().lower() for item in raw_input.split(",") if item.strip()]
    
    invalid_items = [item for item in items if item not in VALID_DIET_PREFERENCES]
    if invalid_items:
        raise ValueError(f"Invalid diet preferences: {', '.join(invalid_items)}")
    
    return items
