import requests
from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from geopy import distance
from requests import exceptions


from foodcartapp.models import Order, Product, Restaurant
from places.models import Place
from django.conf import settings


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


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


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


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    order_items = Order.objects.add_total_price()\
        .exclude(order_status='Выполнен')\
        .prefetch_related('elements')\
        .prefetch_related('elements__product')\
        .order_by('-order_status', 'registered_at')\
        .add_available_restaurants()
    update_places(order_items, settings.YANDEX_API_KEY)
    restaurants = Restaurant.objects.all()
    update_places(restaurants, settings.YANDEX_API_KEY)

    for order in order_items:
        delivery_coordinates = get_coordinates(order.address, settings.YANDEX_API_KEY)
        if not delivery_coordinates:
            continue
        order.restaurants_with_distance = {}
        for restaurant in order.restaurants:
            restaurant_coordinates = get_coordinates(restaurant.address, settings.YANDEX_API_KEY)
            if not restaurant_coordinates:
                continue
            restaurant.distance = round(distance.distance(delivery_coordinates, restaurant_coordinates).km, 1)
            order.restaurants_with_distance[restaurant] = restaurant.distance
        order.restaurants_with_distance = sorted(order.restaurants_with_distance.items(), key=lambda item: item[1])
        order.restaurants_with_distance = {rest: dist for rest, dist in order.restaurants_with_distance}

    return render(request, template_name='order_items.html', context={
        'order_items': order_items
    })
