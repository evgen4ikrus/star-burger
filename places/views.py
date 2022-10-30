import requests
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from requests import exceptions

from .models import Place


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None, None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def update_places(places, yandex_api_key):
    addresses = [place.address for place in Place.objects.all()]
    for item in places:
        if item.address not in addresses:
            try:
                latitude, longitude = fetch_coordinates(yandex_api_key, item.address)
            except exceptions.ConnectionError:
                return None
            if latitude and longitude:
                Place.objects.create(
                    address=item.address,
                    longitude=longitude,
                    latitude=latitude,
                    update_date=timezone.now()
                )


def get_coordinates(address, yandex_api_key):
    try:
        place = Place.objects.get(address=address)
    except ObjectDoesNotExist:
        return None, None
    return place.latitude, place.longitude