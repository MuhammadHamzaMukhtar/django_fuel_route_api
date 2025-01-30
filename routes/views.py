import requests
import pandas as pd
from django.http import JsonResponse
from rest_framework.decorators import api_view

# Constants
ORS_API_KEY = "5b3ce3597851110001cf62489180e88ae4f14c55b98532cf75e8e06f"
ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"
GEOCODE_URL = "https://api.openrouteservice.org/geocode/search"
AVERAGE = 10  # Average MPG for a vehicle
AVERAGE_COST = 3.0  # Average fuel price per gallon

# Load fuel prices
def load_fuel_data():
    file_path = "fuel_prices.csv"  # Ensure this file exists in your project
    return pd.read_csv(file_path)

fuel_data = load_fuel_data()

def get_coordinates(location):
    response = requests.get(GEOCODE_URL, params={
        "api_key": ORS_API_KEY,
        "text": location
    })
    
    if response.status_code == 200:
        data = response.json()
        if data["features"]:
            return data["features"][0]["geometry"]["coordinates"]  # [longitude, latitude]
    return None

@api_view(['GET'])
def get_route(request):
    start = request.GET.get("start")  # Example: "New York, NY"
    finish = request.GET.get("finish")  # Example: "Los Angeles, CA"

    if not start or not finish:
        return JsonResponse({"error": "Start and Finish locations are required"}, status=400)
    
    start_coords = get_coordinates(start)
    finish_coords = get_coordinates(finish)
    
    # Log start and finish coordinates
    print(f"Start coordinates: {start_coords}")
    print(f"Finish coordinates: {finish_coords}")
    
    if not start_coords or not finish_coords:
        return JsonResponse({"error": "Invalid start or finish location"}, status=400)

    # Get route from OpenRouteService
    response = requests.get(ORS_URL, params={
        "api_key": ORS_API_KEY,
        "start": f"{start_coords[0]},{start_coords[1]}",
        "end": f"{finish_coords[0]},{finish_coords[1]}"
    })

    if response.status_code != 200:
        return JsonResponse({"error": "Failed to fetch route"}, status=500)

    route_data = response.json()
    distance = route_data['features'][0]['properties']['summary']['distance'] / 1609  # Convert meters to miles
    print(distance)
    fuel_needed = distance / AVERAGE  # 10 MPG vehicle
    # total_cost, fuel_stops = calculate_fuel_stops(route_data, fuel_needed)
    total_cost = fuel_needed * AVERAGE_COST  # Average fuel price

    return JsonResponse({
        "map": route_data['features'][0]['geometry'],  # GeoJSON for frontend
        "total_distance": f"{round(distance, 2)} miles",
        "fuel_needed": f"{round(fuel_needed, 2)} gallons",
        "total_fuel_cost": f"{round(total_cost, 2)} USD",
    })

# def calculate_fuel_stops(route_data, fuel_needed):
#     total_cost = 0
#     fuel_stops = []
#     current_range = 500  # Maximum range in miles
#     remaining_fuel = 50  # 50 gallons max

#     for i, point in enumerate(route_data['features'][0]['geometry']['coordinates']):
#         lat, lon = point[1], point[0]

#         # Find nearest fuel station
#         nearby_stations = fuel_data.nsmallest(5, "Retail Price")  # Get top 5 cheapest stations
#         cheapest_station = nearby_stations.iloc[0]
#         station_cost = cheapest_station["Retail Price"]

#         # Refill if needed
#         if current_range < 100 and fuel_needed > 0:
#             gallons_needed = min(50 - remaining_fuel, fuel_needed)
#             cost = gallons_needed * station_cost
#             total_cost += cost
#             remaining_fuel += gallons_needed
#             fuel_needed -= gallons_needed
#             current_range = 500  # Reset range

#             fuel_stops.append({
#                 "name": cheapest_station["Truckstop Name"],
#                 "address": cheapest_station["Address"],
#                 "city": cheapest_station["City"],
#                 "state": cheapest_station["State"],
#                 "price_per_gallon": station_cost,
#                 "gallons_filled": gallons_needed,
#                 "cost": cost
#             })

#         current_range -= 10  # Reduce by 10 miles per iteration

#     return total_cost, fuel_stops
