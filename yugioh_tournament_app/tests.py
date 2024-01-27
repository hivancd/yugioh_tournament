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
            
class PlayerTests(TestCase):
    
    def __create_test_player():
        return Player(first_name='Carlos Mauricio',
            last_name='Reyes', second_last_name='Escudero',
            province='Sancti Spiritu', municipality='Majayigua',
            phone='+53 58607451', address='Sukasa')
    
    def test_phone_is_not_real(self):
        '''
        Checks the phone number is not something dumb like +53 12345678
        '''
        test_player=PlayerTests.__create_test_player()
        test_player.phone='+53 12345678'
        with self.assertRaises(exceptions.ValidationError):
            test_player.full_clean()
        
    def test_phone_is_not_giverish(self):
        '''
        Checks the phone number is made of digits
        '''
        test_player=PlayerTests.__create_test_player()
        test_player.phone='salchichas'
        with self.assertRaises(exceptions.ValidationError):
            test_player.full_clean()
            
    def test_phone_is_not_too_long(self):
        '''
        Checks the phonenumber is not too long for a phonenumber
        '''
        test_player=PlayerTests.__create_test_player()
        test_player.phone='+53413123424532645374374'
        with self.assertRaises(exceptions.ValidationError):
            test_player.full_clean()
            
    def test_phone_has_international_prefix(self):
        '''
        Checks phonenumber has the + prefix
        '''
        test_player=PlayerTests.__create_test_player()
        test_player.phone='5355641257'
        with self.assertRaises(exceptions.ValidationError):
            test_player.full_clean()
            
    def test_phone_is_optional(self):
        '''
        Checks the phone number can be empty
        '''
        test_player=PlayerTests.__create_test_player()
        test_player.phone=''
        test_player.full_clean()
        
    def test_fullname_works(self):
        '''
        Checks the returning of the players fullname is correct
        '''
        test_player=PlayerTests.__create_test_player()
        self.assertEqual(test_player.fullname(),'Carlos Mauricio Reyes Escudero')
        
    def test_fullname_has_no_whitespace(self):
        '''
        Checks the fullname does not return whitespace
        '''
        test_player=PlayerTests.__create_test_player()
        test_player.first_name='               Carlos        Mauricio   '
        self.assertEqual(test_player.fullname(),'Carlos Mauricio Reyes Escudero')    
        