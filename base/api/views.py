from django.contrib.auth.models import User, Group

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework import parsers, viewsets, status, filters

from base.api.serializers import CategorySerializer, ProductSerializer
from base.models import Category


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
        name = request.data.get('name')
        action = request.data.get('action')

        if user not in admins:
            return Response(self.messages[3], status=status.HTTP_403_FORBIDDEN)

        if action not in self.actions:
            return Response(self.messages[2], status=status.HTTP_400_BAD_REQUEST)

        category = None
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
        else:
            return Response(self.messages[1], status=status.HTTP_400_BAD_REQUEST)

        if action == self.actions[0]:
            category = self.qs.create(name=name)
            self.instance = category
        elif action == self.actions[1]:
            if name:
                category.name = name
                category.save()
                self.instance = category
            else:
                return Response(self.messages[4], status=status.HTTP_400_BAD_REQUEST)
        elif action == self.actions[2]:
            self.instance = category.delete()
        else:
            return Response(self.messages[4], status=status.HTTP_400_BAD_REQUEST)
        return Response(self.serializer_class(self.instance))