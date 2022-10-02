from django.core.exceptions import ObjectDoesNotExist, ValidationError
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
    for fild in ['firstname', 'lastname', 'phonenumber', 'address', 'products']:
        if fild not in raw_order.keys():
            content = f'{fild}: Обязательное поле.'
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
        elif not raw_order[fild]:
            content = f'{fild}: Поле не может быть пустым.'
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
    if not isinstance(raw_order['products'], list):
        content = {'products: Ожидался list со значениями, но был получен другой тип'}
        return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
    if not isinstance(raw_order['firstname'], str):
        content = {'firstname: Ожидалася тип string, но был ролучен другой тип.'}
        return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
    for product in raw_order['products']:
        try:
            Product.objects.get(id=product['product'])
        except ObjectDoesNotExist:
            content = {'products: Недопустимый первичный ключ.'}
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)

    try:
        customer = Customer(
            firstname=raw_order['firstname'],
            lastname=raw_order['lastname'],
            phonenumber=raw_order['phonenumber'],
            address=raw_order['address'],
        )
        customer.full_clean()
    except ValidationError:
        content = {'phonenumber: Введен некорректный номер телефона.'}
        return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
    customer.save()

    for product in raw_order['products']:
        order = Order(customer=customer,
                      product=Product.objects.get(id=product['product']),
                      quantity=product['quantity'])
        order.save()
    return Response(raw_order)
