from django.test import TestCase

class SmokeTest(TestCase):

    def test_good_maths(self):
        self.assertEqual(1 + 2, 3)

    def test_bad_maths(self):
        self.assertEqual(1 + 1, 3)