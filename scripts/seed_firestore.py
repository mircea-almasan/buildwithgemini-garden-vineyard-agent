import sys
from google.cloud import firestore

# CRITICAL: Hardcoded project ID string literal
# Do NOT read from GOOGLE_CLOUD_PROJECT or google.auth.default() (returns project number on Agent Platform)
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-01-b2884ff80cc8"

def seed_database():
    print(f"Connecting to Firestore with project ID: {FIRESTORE_PROJECT_ID}")
    db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    collection_ref = db.collection("property_inventory")

    seeded_items = [
        {
            "id": "vine-cab-01",
            "category": "Vineyard",
            "name": "Cabernet Sauvignon Block A",
            "variety": "Cabernet Sauvignon",
            "location": "South Slope Row 1-5",
            "planting_date": "2021-04-15",
            "soil_notes": "Clay loam over limestone, pH 6.5",
            "status": "Ripening - Pre-Harvest",
            "notes": "Trellis: Guyot Double. Good canopy health.",
            "last_action": {"action": "Canopy Trimming", "date": "2026-08-20"}
        },
        {
            "id": "vine-chardo-02",
            "category": "Vineyard",
            "name": "Chardonnay Block B",
            "variety": "Chardonnay",
            "location": "East Terrace Row 1-4",
            "planting_date": "2022-03-20",
            "soil_notes": "Silty clay loam, pH 6.6",
            "status": "Veraison Complete",
            "notes": "Trellis: Cordon Spur. High Brix monitoring active.",
            "last_action": {"action": "Cluster Thinning", "date": "2026-08-10"}
        },
        {
            "id": "orchard-gala-01",
            "category": "Orchard",
            "name": "Gala Apple Trees",
            "variety": "Royal Gala Apple",
            "location": "North Orchard Row 2",
            "planting_date": "2019-11-05",
            "soil_notes": "Well-drained sandy loam, pH 6.8",
            "status": "Fruit Maturation",
            "notes": "M.9 Rootstock. Drip irrigation system attached.",
            "last_action": {"action": "Organic Pest Spray (Neem)", "date": "2026-07-25"}
        },
        {
            "id": "orchard-cherry-02",
            "category": "Orchard",
            "name": "Bing Cherry Orchard",
            "variety": "Bing Cherry",
            "location": "West Orchard Row 1",
            "planting_date": "2020-02-18",
            "soil_notes": "Deep alluvial silt, pH 6.7",
            "status": "Post-Harvest Rest",
            "notes": "Netting applied during fruiting. Pruning scheduled for winter.",
            "last_action": {"action": "Harvesting", "date": "2026-06-30"}
        },
        {
            "id": "garden-tomato-01",
            "category": "Garden",
            "name": "Heirloom Tomato Bed",
            "variety": "Brandywine & San Marzano",
            "location": "Kitchen Garden Raised Bed 1",
            "planting_date": "2026-05-10",
            "soil_notes": "Organic compost & biochar mix, pH 6.2",
            "status": "Active Harvesting",
            "notes": "Drip tape watering 2L/m² daily. Staked with cages.",
            "last_action": {"action": "Fertilizing (Fish Emulsion)", "date": "2026-09-01"}
        },
        {
            "id": "garden-herbs-02",
            "category": "Garden",
            "name": "Mediterranean Herb Plot",
            "variety": "Rosemary, Thyme, Sage",
            "location": "South Garden Border",
            "planting_date": "2025-04-01",
            "soil_notes": "Gravelly well-draining soil, pH 7.1",
            "status": "Perennial Growth",
            "notes": "Low water requirement. Mulched with gravel.",
            "last_action": {"action": "Pruning & Drying", "date": "2026-08-15"}
        }
    ]

    for item in seeded_items:
        doc_ref = collection_ref.document(item["id"])
        doc_ref.set(item)
        print(f"Seeded document: {item['id']} ({item['name']} - {item['category']})")

    print("\nDatabase seeding completed successfully.")

if __name__ == "__main__":
    seed_database()
