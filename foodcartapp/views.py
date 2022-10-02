from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Customer, Order, Product


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([{
        'title': 'Burger',
        'src': static('burger.jpg'),
        'text': 'Tasty Burger at your door step',
    }, {
        'title': 'Spices',
        'src': static('food.jpg'),
        'text': 'All Cuisines',
    }, {
        'title': 'New York',
        'src': static('tasty.jpg'),
        'text': 'Food is incomplete without a tasty dessert',
    }],
                        safe=False,
                        json_dumps_params={
                            'ensure_ascii': False,
                            'indent': 4,
                        })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products,
                        safe=False,
                        json_dumps_params={
                            'ensure_ascii': False,
                            'indent': 4,
                        })


@api_view(['POST'])
def register_order(request):
    raw_order = request.data
    try:
        if isinstance(raw_order['products'], str):
            content = {'products: Ожидался list со значениями, но был получен "str"'}
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
        if raw_order['products'] is None:
            content = {'products: Это поле не может быть пустым.'}
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
        if raw_order['products'] == []:
            content = {'products: Этот список не может быть пустым'}
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
    except KeyError:
        content = {'products: Обязательное поле.'}
        return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
    customer = Customer.objects.create(
        firstname=raw_order['firstname'],
        lastname=raw_order['lastname'],
        phone_number=raw_order['phonenumber'],
        address=raw_order['address'],
    )
    for product in raw_order['products']:
        order = Order(customer=customer,
                      product=Product.objects.get(id=product['product']),
                      quantity=product['quantity'])
        order.save()
    return Response(raw_order)
