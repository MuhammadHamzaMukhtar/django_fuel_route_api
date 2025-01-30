import requests
import pandas as pd
from django.http import JsonResponse
from rest_framework.decorators import api_view

ORS_API_KEY = "5b3ce3597851110001cf62489180e88ae4f14c55b98532cf75e8e06f"
ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"
GEOCODE_URL = "https://api.openrouteservice.org/geocode/search"
CAR_AVERAGE = 10
AVERAGE_COST = 3.0

def get_coordinates(location):
    response = requests.get(GEOCODE_URL, params={
        "api_key": ORS_API_KEY,
        "text": location
    })
    
    if response.status_code == 200:
        data = response.json()
        if data["features"]:
            return data["features"][0]["geometry"]["coordinates"]  
    return None

@api_view(['GET'])
def get_route(request):
    start = request.GET.get("start")  
    finish = request.GET.get("finish") 

    if not start or not finish:
        return JsonResponse({"error": "Start and Finish locations are required"}, status=400)
    
    start_coords = get_coordinates(start)
    finish_coords = get_coordinates(finish)
    
    if not start_coords or not finish_coords:
        return JsonResponse({"error": "Invalid start or finish location"}, status=400)

    response = requests.get(ORS_URL, params={
        "api_key": ORS_API_KEY,
        "start": f"{start_coords[0]},{start_coords[1]}",
        "end": f"{finish_coords[0]},{finish_coords[1]}"
    })

    if response.status_code != 200:
        return JsonResponse({"error": "Failed to fetch route"}, status=500)

    route_data = response.json()
    distance = route_data['features'][0]['properties']['summary']['distance'] / 1609  
    fuel_needed = distance / CAR_AVERAGE  
    total_cost = fuel_needed * AVERAGE_COST  

    return JsonResponse({
        "map": route_data['features'][0]['geometry'], 
        "total_distance": f"{round(distance, 2)} miles",
        "fuel_needed": f"{round(fuel_needed, 2)} gallons",
        "total_fuel_cost": f"{round(total_cost, 2)} USD",
    })