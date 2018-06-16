from django.contrib.auth.models import User, Group

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework import parsers, viewsets, status, filters

from base.api.serializers import CategorySerializer, ProductSerializer
from base.models import Category, Product

import dgis


class CategoryView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = CategorySerializer
    messages = {
        1: {'message': 'Category reference error', 'message_header': 'Error', 'error': True},
        2: {'message': 'Wrong action', 'message_header': 'Error', 'error': True},
        3: {'message': 'Only admins can edit categories', 'message_header': 'Error', 'error': True},
        4: {'message': 'Wrong input', 'message_header': 'Error', 'error': True},
    }
    actions = ['add', 'update', 'delete']
    qs = Category.objects
    instance = None

    def get(self, request, *args, **kwargs):
        reference = request.GET.get('reference')
        if reference:
            try:
                try:
                    reference = int(reference)
                except ValueError, e:
                    category = self.qs.filter(name=reference).last()
                else:
                    category = self.qs.get(id=reference)
            except (Category.DoesNotExist, TypeError):
                return Response(self.messages[1], status=status.HTTP_400_BAD_REQUEST)
            serializer = self.serializer_class(category)
        else:
            serializer = self.serializer_class(self.qs.all(), many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        user = request.user
        admins = User.objects.filter(groups__name='admin')
        reference = request.data.get('reference')
        action = request.data.get('action')

        name = request.data.get('name')

        category = None

        if user not in admins:
            return Response(self.messages[3], status=status.HTTP_403_FORBIDDEN)

        if action not in self.actions:
            return Response(self.messages[2], status=status.HTTP_400_BAD_REQUEST)

        if reference:
            try:
                try:
                    reference = int(reference)
                except ValueError, e:
                    category = self.qs.filter(name=reference).last()
                else:
                    category = self.qs.get(id=reference)
            except (Category.DoesNotExist, TypeError):
                return Response(self.messages[1], status=status.HTTP_400_BAD_REQUEST)


        if action == self.actions[0]:
            category = self.qs.create(name=name)
            self.instance = category
        elif action == self.actions[1]:
            if category:
                if name:
                    category.name = name
                category.save()
                self.instance = category
            else:
                return Response(self.messages[4], status=status.HTTP_400_BAD_REQUEST)
        elif action == self.actions[2]:
            if category:
                self.instance = category
                category.delete()
            else:
                return Response(self.messages[1], status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(self.messages[4], status=status.HTTP_400_BAD_REQUEST)
        data = self.serializer_class(self.instance).data
        return Response(data)


class ProductView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ProductSerializer
    messages = {
        1: {'message': 'Product reference error', 'message_header': 'Error', 'error': True},
        2: {'message': 'Wrong action', 'message_header': 'Error', 'error': True},
        3: {'message': 'Only admins can edit products', 'message_header': 'Error', 'error': True},
        4: {'message': 'Wrong input', 'message_header': 'Error', 'error': True},
        5: {'message': 'Category does not exist', 'message_header': 'Error', 'error': True},
    }
    actions = ['add', 'update', 'delete', 'delete_all']
    qs = Product.objects
    instance = None

    def get(self, request, *args, **kwargs):
        reference = request.GET.get('reference')
        if reference:
            try:
                try:
                    reference = int(reference)
                except ValueError, e:
                    category = self.qs.filter(name=reference).last()
                else:
                    category = self.qs.get(id=reference)
            except (Category.DoesNotExist, TypeError):
                return Response(self.messages[1], status=status.HTTP_400_BAD_REQUEST)
            serializer = self.serializer_class(category)
        else:
            serializer = self.serializer_class(self.qs.all(), many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        user = request.user
        admins = User.objects.filter(groups__name='admin')
        reference = request.data.get('reference')
        action = request.data.get('action')

        name = request.data.get('name')
        category_id = request.data.get('category')
        description = request.data.get('description', '')
        base_fare = request.data.get('base_fare', 0)
        margin = request.data.get('margin', 0)

        category = None
        product = None

        if user not in admins:
            return Response(self.messages[3], status=status.HTTP_403_FORBIDDEN)

        if action not in self.actions:
            return Response(self.messages[2], status=status.HTTP_400_BAD_REQUEST)

        if category_id:
            category = Category.objects.filter(id=category_id)
            if category.exists():
                category = category[0]
            else:
                return Response(self.messages[5], status=status.HTTP_400_BAD_REQUEST)


        if reference:
            try:
                try:
                    reference = int(reference)
                except ValueError, e:
                    product = self.qs.filter(name=reference).last()
                else:
                    product = self.qs.get(id=reference)
            except (Product.DoesNotExist, TypeError):
                return Response(self.messages[1], status=status.HTTP_400_BAD_REQUEST)


        if action == self.actions[0]:
            product = self.qs.create(name=name, category=category,
                                      creator=user, description=description,
                                      base_fare=int(base_fare), margin=int(margin), total_fare=int(base_fare)+int(margin))
            self.instance = product
        elif action == self.actions[1]:
            if product:
                if name:
                    product.name = name
                if description:
                    product.description = description
                if base_fare:
                    product.base_fare = base_fare
                if margin:
                    product.margin = margin
                if category:
                    product.category = category
                product.creator = user
                product.total_fare = int(base_fare) + int(margin)
                product.save()
                self.instance = product
            else:
                return Response(self.messages[4], status=status.HTTP_400_BAD_REQUEST)
        elif action == self.actions[2]:
            if product:
                self.instance = product
                product.delete()
            else:
                return Response(self.messages[1], status=status.HTTP_400_BAD_REQUEST)
        elif action == self.actions[3]:
            if category:
                qs = self.qs.filter(category=category)
                self.instance = qs.first()
            else:
                qs = self.qs.all()
                self.instance = self.qs.last
            qs.delete()
        else:
            return Response(self.messages[4], status=status.HTTP_400_BAD_REQUEST)
        return Response(self.serializer_class(self.instance).data)


class Dgis(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        api = dgis.API('rutnpt3272')
        magnums = api.search(what='Magnum', where=u'Алматы')
        return magnums