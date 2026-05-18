from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.viewsets import GenericViewSet
from rest_framework import viewsets, status
from .models import Product, Review, Cart, CartItem, Order
from .serializers import ProductSerializer, ReviewSerializer, CartSerializer, CartItemSerializer, AddCartItemSerializer, \
    UpdateCartItemSerializer, OrderSerializer, CreateOrderSerializer
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin





class ProductViewSet(viewsets.ModelViewSet):
    # select_related avoids an extra query per product to fetch the collection
    queryset = Product.objects.select_related('collection').prefetch_related('images').all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer


    def get_queryset(self):
        return Review.objects.filter(product=self.kwargs['product_pk'])


    def get_serializer_context(self):
        return {"product_id": self.kwargs['product_pk']}



class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    # prefetch_related prevents N+1 queries when serializing cart items + their products
    queryset = Cart.objects.prefetch_related('items__product__images').all()
    serializer_class = CartSerializer



class CartItemViewSet(viewsets.ModelViewSet):

    http_method_names = ['get','post','patch','delete']


    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart=self.kwargs['cart_pk']).select_related('product').prefetch_related('product__images')


    def get_serializer_context(self):
        return {"cart_id": self.kwargs['cart_pk']}


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        # Each user only sees their own orders; admins see all
        if self.request.user.is_staff:
            return Order.objects.prefetch_related('items__product__images').all()
        return Order.objects.prefetch_related('items__product__images').filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}










