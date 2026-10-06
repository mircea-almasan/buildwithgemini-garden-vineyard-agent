import datetime
import os
from zoneinfo import ZoneInfo
from typing import Dict, Any, List, Optional
from google.cloud import firestore

# Firestore project is configured through the environment.
FIRESTORE_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

if not FIRESTORE_PROJECT_ID:
    raise ValueError(
        "GOOGLE_CLOUD_PROJECT is not configured. Set it in your .env file."
    )

GCS_ASSETS_BUCKET = "garden-vineyard-assets-gva"
GCS_BASE_URL = f"https://storage.googleapis.com/{GCS_ASSETS_BUCKET}"


def get_firestore_client() -> firestore.Client:
    """Returns a Firestore client initialized with the configured project ID."""
    return firestore.Client(project=FIRESTORE_PROJECT_ID)


def list_inventory_items(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches inventory items from the property_inventory Firestore collection.

    Args:
        category: Optional filter for 'Vineyard', 'Orchard', or 'Garden'. If omitted, returns all items.

    Returns:
        List of dictionaries representing plant/vineyard/orchard inventory items.
    """
    db = get_firestore_client()
    collection_ref = db.collection("property_inventory")
    
    if category and category.strip():
        query_ref = collection_ref.where("category", "==", category.strip().capitalize())
        docs = query_ref.stream()
    else:
        docs = collection_ref.stream()

    items = []
    for doc in docs:
        data = doc.to_dict()
        items.append(data)
    return items


def get_inventory_item(item_id: str) -> Dict[str, Any]:
    """Gets details of a specific inventory item by ID.

    Args:
        item_id: Unique identifier of the inventory item (e.g., 'vine-cab-01', 'orchard-gala-01', 'garden-tomato-01').

    Returns:
        Dictionary with item attributes or error message if not found.
    """
    db = get_firestore_client()
    doc_ref = db.collection("property_inventory").document(item_id)
    doc = doc_ref.get()

    if doc.exists:
        return doc.to_dict()
    return {"error": f"Item with ID '{item_id}' not found in property_inventory."}


def add_or_update_inventory_item(
    item_id: str,
    name: str,
    category: str,
    variety: str,
    location: str,
    planting_date: str,
    soil_notes: str,
    status: str,
    notes: str,
    image_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Adds a new plant/vine/tree or updates an existing inventory item in Firestore.

    Args:
        item_id: Unique identifier (e.g. 'vine-pinot-03', 'garden-lettuce-01').
        name: Human readable name of the plot/bed/trees.
        category: 'Vineyard', 'Orchard', or 'Garden'.
        variety: Specific variety name (e.g. 'Pinot Noir', 'Burlat Cherry').
        location: Specific property location or row number.
        planting_date: Planting date in YYYY-MM-DD format.
        soil_notes: Soil composition and pH notes.
        status: Current health/phenological status.
        notes: General notes or care instructions.
        image_url: Optional public URL of a visual diagram or photo.

    Returns:
        Dictionary indicating operation result.
    """
    db = get_firestore_client()
    item_data = {
        "id": item_id,
        "name": name,
        "category": category.capitalize(),
        "variety": variety,
        "location": location,
        "planting_date": planting_date,
        "soil_notes": soil_notes,
        "status": status,
        "notes": notes,
        "image_url": image_url or f"{GCS_BASE_URL}/grape_pruning.png" if category.capitalize() == "Vineyard" else f"{GCS_BASE_URL}/orchard_layout.png",
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    doc_ref = db.collection("property_inventory").document(item_id)
    doc_ref.set(item_data, merge=True)

    return {"success": True, "message": f"Item '{name}' ({item_id}) saved to Firestore successfully.", "item": item_data}


def log_action_for_item(
    item_id: str, action: str, date: str, details: Optional[str] = None
) -> Dict[str, Any]:
    """Logs an agricultural action (pruning, fertilizing, spraying, irrigation, harvesting) for an inventory item.

    Args:
        item_id: Unique identifier of the inventory item.
        action: Type of action performed (e.g. 'Pruning', 'Spraying', 'Irrigation', 'Fertilizing', 'Harvesting').
        date: Date of action in YYYY-MM-DD format.
        details: Optional additional notes about the action.

    Returns:
        Confirmation dictionary.
    """
    db = get_firestore_client()
    doc_ref = db.collection("property_inventory").document(item_id)
    doc = doc_ref.get()

    if not doc.exists:
        return {"error": f"Cannot log action. Item '{item_id}' does not exist."}

    last_action = {"action": action, "date": date, "details": details or ""}
    doc_ref.update({"last_action": last_action})

    return {
        "success": True,
        "message": f"Logged action '{action}' on {date} for item '{item_id}'.",
        "last_action": last_action,
    }


def get_weather_forecast(location: str) -> Dict[str, Any]:
    """Fetches weather forecast and agricultural risk warnings (frost, spray window, drought) in metric units.

    Args:
        location: City or vineyard location string.

    Returns:
        Dictionary containing metric weather data (°C, mm, km/h) and agricultural warnings.
    """
    loc_lower = location.lower()
    if "bordeaux" in loc_lower or "france" in loc_lower or "europe" in loc_lower:
        return {
            "location": location,
            "temp_current_c": 18.5,
            "temp_min_c": 7.0,
            "temp_max_c": 22.0,
            "rainfall_24h_mm": 12.0,
            "wind_speed_kmh": 14.0,
            "humidity_percent": 82,
            "frost_risk": "Low (Min 7.0°C)",
            "spray_window": "Sub-optimal (Rain expected within 12h)",
            "irrigation_recommendation": "Pause irrigation due to recent rainfall (12 mm)",
        }
    return {
        "location": location,
        "temp_current_c": 24.0,
        "temp_min_c": 12.0,
        "temp_max_c": 28.5,
        "rainfall_24h_mm": 0.0,
        "wind_speed_kmh": 8.5,
        "humidity_percent": 45,
        "frost_risk": "None",
        "spray_window": "Optimal (Low wind, no rain forecast)",
        "irrigation_recommendation": "Normal drip irrigation schedule: 3 L/m²",
    }


def lookup_plant_care_info(variety: str, category: Optional[str] = None) -> Dict[str, Any]:
    """Looks up agronomic care guidelines, pruning requirements, and disease prevention for a plant, fruit tree, or grape variety.

    Args:
        variety: Name of the variety (e.g., 'Cabernet Sauvignon', 'Gala Apple', 'Heirloom Tomato').
        category: Optional category ('Vineyard', 'Orchard', 'Garden').

    Returns:
        Dictionary with pruning, irrigation, fertilization, disease prevention, and visual diagram image_url.
    """
    var_lower = variety.lower()
    if "cabernet" in var_lower or "chardonnay" in var_lower or "grape" in var_lower or "vine" in var_lower:
        return {
            "variety": variety,
            "category": "Vineyard",
            "pruning_recommendation": "Double Guyot or Cordon de Royat pruning during winter dormancy (Jan-Feb). Maintain 6-8 buds per spur.",
            "irrigation_needs": "Regulated Deficit Irrigation (RDI) post-fruit set (2.0-3.5 L/m² per week depending on ET0).",
            "fertilization_guidance": "Foliar Nitrogen + Potassium application prior to veraison to support sugar accumulation.",
            "disease_prevention": "Monitor for Downy Mildew (Plasmopara viticola) and Powdery Mildew. Apply copper/sulfur sprays during optimal weather windows.",
            "diagram_image_url": f"{GCS_BASE_URL}/grape_pruning.png",
        }
    elif "apple" in var_lower or "cherry" in var_lower or "fruit" in var_lower or "tree" in var_lower:
        return {
            "variety": variety,
            "category": "Orchard",
            "pruning_recommendation": "Central Leader or Modified Spindle pruning in late winter. Thin central fruit clusters after June drop.",
            "irrigation_needs": "Deep watering at root zone (15-25 L per tree twice weekly during fruit enlargement).",
            "fertilization_guidance": "Balanced N-P-K (10-10-10) in early spring before bud break.",
            "disease_prevention": "Watch for Apple Scab and Codling Moth. Apply preventative organic Neem oil or targeted bio-fungicides.",
            "diagram_image_url": f"{GCS_BASE_URL}/orchard_layout.png",
        }
    else:
        return {
            "variety": variety,
            "category": "Garden",
            "pruning_recommendation": "Remove suckers/side shoots on indeterminate varieties. Pinch growing tips to promote fruit set.",
            "irrigation_needs": "Consistent drip irrigation (2.5-4.0 L/m² daily at soil level; avoid wetting foliage).",
            "fertilization_guidance": "High Phosphorus & Potassium liquid fertilizer every 2 weeks during flowering and fruiting.",
            "disease_prevention": "Mulch around base to prevent soil-borne Early Blight. Ensure 60cm spacing for airflow.",
            "diagram_image_url": f"{GCS_BASE_URL}/orchard_layout.png",
        }


def calculate_growing_degree_days(
    daily_highs_c: List[float], daily_lows_c: List[float], base_temp_c: float = 10.0
) -> Dict[str, Any]:
    """Calculates Growing Degree Days (GDD in °C) for wine grape or crop thermal accumulation.

    Args:
        daily_highs_c: List of daily maximum temperatures in °C.
        daily_lows_c: List of daily minimum temperatures in °C.
        base_temp_c: Base temperature threshold in °C (default 10.0°C for wine grapes).

    Returns:
        Dictionary with total GDD accumulated over the input period and daily details.
    """
    if len(daily_highs_c) != len(daily_lows_c):
        return {"error": "daily_highs_c and daily_lows_c lists must have the same length."}

    total_gdd = 0.0
    daily_gdd_list = []

    for high, low in zip(daily_highs_c, daily_lows_c):
        avg_temp = (high + low) / 2.0
        gdd = max(0.0, avg_temp - base_temp_c)
        total_gdd += gdd
        daily_gdd_list.append(round(gdd, 2))

    return {
        "base_temp_c": base_temp_c,
        "period_days": len(daily_highs_c),
        "total_gdd_c": round(total_gdd, 2),
        "daily_gdd": daily_gdd_list,
        "ripening_stage_indicator": "High heat accumulation - Monitor sugar/Brix" if total_gdd > 100 else "Standard growth accumulation",
    }


def calculate_irrigation_and_dosage(
    plot_area_m2: float, target_water_liters_per_m2: float, fertilizer_g_per_m2: Optional[float] = None
) -> Dict[str, Any]:
    """Calculates total water volume in liters and fertilizer requirements in kg for a garden plot, orchard, or vineyard row.

    Args:
        plot_area_m2: Area of the plot or row in square meters (m²).
        target_water_liters_per_m2: Desired watering rate in L/m².
        fertilizer_g_per_m2: Optional fertilizer application rate in grams per m².

    Returns:
        Dictionary containing total water requirement (liters and m³) and total fertilizer weight (kg).
    """
    total_water_liters = round(plot_area_m2 * target_water_liters_per_m2, 2)
    total_water_m3 = round(total_water_liters / 1000.0, 3)

    result = {
        "plot_area_m2": plot_area_m2,
        "watering_rate_l_per_m2": target_water_liters_per_m2,
        "total_water_liters": total_water_liters,
        "total_water_m3": total_water_m3,
    }

    if fertilizer_g_per_m2 is not None:
        total_fert_grams = plot_area_m2 * fertilizer_g_per_m2
        total_fert_kg = round(total_fert_grams / 1000.0, 2)
        result["fertilizer_rate_g_per_m2"] = fertilizer_g_per_m2
        result["total_fertilizer_kg"] = total_fert_kg

    return result
