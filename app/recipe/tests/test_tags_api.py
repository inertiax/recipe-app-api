from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicUserTagsApiTests(TestCase):
    """test the publicity available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """test that login is required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@amine.com',
            'test123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """test retrieving tags"""
        Tag.objects.create(user=self.user, name='vegan')
        Tag.objects.create(user=self.user, name='dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """test that tags returned are for the auth user"""
        user2 = get_user_model().objects.create_user(
            'other@amine.com',
            'tast321'
        )
        Tag.objects.create(user=user2, name='fruit')
        tag = Tag.objects.create(user=self.user, name='happy food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
