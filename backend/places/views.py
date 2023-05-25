import requests
from django.conf import settings
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


def get_addresses_coordinates(addresses):
    places = Place.objects.filter(address__in=addresses)
    places_addresses = [place.address for place in places]
    addresses_coordinates = {}
    for address in addresses:
        if address in places_addresses:
            continue
        try:
            latitude, longitude = fetch_coordinates(settings.YANDEX_API_KEY, address)
        except exceptions.ConnectionError:
            continue
        if latitude and longitude:
            Place.objects.create(
                address=address,
                longitude=longitude,
                latitude=latitude,
                update_at=timezone.now()
            )
    for place in places:
        if place.address in addresses_coordinates:
            continue
        addresses_coordinates[place.address] = (place.latitude, place.longitude)
    return addresses_coordinates
