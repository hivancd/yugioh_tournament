from django.test import TestCase
from django.core import exceptions
from .models import *

# Create your tests here.

class CardModelTests(TestCase):
    '''
    Tests for card and card 'inherate' models
    '''
    
    # AUXILIAR METHODS
    def __create_test_card():
        return Card(
            card_name='test card',
            description='This is a description',
        )
    def __create_test_monster_card(self):
        return MonsterCard(
            card=CardModelTests.__create_test_card(),attack=2000,defense=2000,
            attribute='WA',level=12,is_effect=False,
        )
    def __create_test_effect_card(self):
        return EffectCard(
            card=CardModelTests.__create_test_card(),card_type='T',
        )
        
    # TEST METHODS
    def test_card_attribute_is_not_in_choices(self):
        '''
        The card_attribute should be one of the listed in the model
        '''
        test_card=self.__create_test_monster_card()
        test_card.attribute='NO'
        with self.assertRaises(exceptions.ValidationError):
            test_card.full_clean()
    def test_card_type_is_not_in_choices(self):
        '''
        The card_type should be one of the listed in the model
        '''
        test_card=self.__create_test_effect_card()
        test_card.card_type="N"
        
        with self.assertRaises(exceptions.ValidationError):
            test_card.full_clean()
    def test_card_level_less_than_max_level(self):
        '''
        The card level should be less than the maximum
        '''
        test_card=self.__create_test_monster_card()
        test_card.level = 20
        with self.assertRaises(exceptions.ValidationError):
            test_card.full_clean()
    def test_card_level_greater_than_min_level(self):
        '''
        The card level should be greater than the minimun
        '''
        test_card=self.__create_test_monster_card()
        test_card.level=0
        with self.assertRaises(exceptions.ValidationError):
            test_card.full_clean()