from src.precise_value import Precise_value
import unittest

class test__init__(unittest.TestCase):
    def setup(self):
        

    def test__init__(self):
        value_1 = Precise_value('no_rounding', '3')
        value_2 = Precise_value('no_rounding', '3')
