"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from asg.models import UserProfile, createUserProfile, User, GameExperiment, MaxHighScore
from django.core.urlresolvers import reverse


class ModelTest(TestCase):
    # test if the user proflie can be creation
    def test_userProfile_creation(self):
        user = User(username='_test', email='test@test.com')
        user.set_password('test')
        user.save()
        userProfile = UserProfile(user=user)
        userProfile.save()

        self.assertIsNotNone(self, userProfile)

    # test the default values of user profile
    def test_default_value_level(self):
        user = User(username='_test', email='test@test.com')
        user.set_password('test')
        user.save()
        userProfile = UserProfile(user=user)
        userProfile.save()

        self.assertEqual(userProfile.level == 0, True)

    def test_default_value_rating(self):
        user = User(username='_test', email='test@test.com')
        user.set_password('test')
        user.save()
        userProfile = UserProfile(user=user)
        userProfile.save()

        self.assertEqual(userProfile.rating == 0, True)

    def test_default_value_no_game_played(self):
        user = User(username='_test', email='test@test.com')
        user.set_password('test')
        user.save()
        userProfile = UserProfile(user=user)
        userProfile.save()

        self.assertEqual(userProfile.no_games_played == 0, True)

    def test_default_value_total_points(self):
        user = User(username='_test', email='test@test.com')
        user.set_password('test')
        user.save()
        userProfile = UserProfile(user=user)
        userProfile.save()

        self.assertEqual(userProfile.total_points == 0, True)

    def test_default_value_total_tokens(self):
        user = User(username='_test', email='test@test.com')
        user.set_password('test')
        user.save()
        userProfile = UserProfile(user=user)
        userProfile.save()

        self.assertEqual(userProfile.total_tokens == 0, True)

    def test_default_value_no_queries_issued(self):
        user = User(username='_test', email='test@test.com')
        user.set_password('test')
        user.save()
        userProfile = UserProfile(user=user)
        userProfile.save()

        self.assertEqual(userProfile.no_queries_issued == 0, True)

    def test_default_value_no_docs_assessed(self):
        user = User(username='_test', email='test@test.com')
        user.set_password('test')
        user.save()
        userProfile = UserProfile(user=user)
        userProfile.save()

        self.assertEqual(userProfile.no_docs_assessed == 0, True)

    # test the creation of gameExperiment
    def test_gameExperiment_creation(self):
        ge = GameExperiment()
        ge.save()
        self.assertIsNotNone(self, ge)

    # test the maxHighScore by the args of user and gameExperiment instances
    def test_maxHighScore(self):
        user = User(username='_test', email='test@test.com')
        user.set_password('test')
        user.save()
        userProfile = UserProfile(user=user)
        userProfile.save()
        ge = GameExperiment()
        ge.save()
        mhs = MaxHighScore(user=user, game_experiment=ge)
        self.assertIsNotNone(self, mhs)


class ViewTest(TestCase):
    # test if a new user can access to the pick view
    # Once the pick view accessed, the lock context will match with the list
    def test_pick_view_with_new_user(self):
        user = User(username='_test', email='test@test.com')
        user.set_password('test')
        user.save()
        userProfile = UserProfile(user=user)
        userProfile.save()

        response = self.client.get(reverse('pick', kwargs={'username': user}))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['lock'], ['0', '1', '1', '1', '1', '1'])

    # test if the right game can be started with the num given.
    def test_start_game_with_game_num(self):
        num = '5'
        response = self.client.get(reverse('startgame', kwargs={'num': num}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['gameId'], 5)
