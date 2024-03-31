from django.test import TestCase
from django.core import exceptions
from .models import *

# Create your tests here.

def create_test_player():
        return Player(first_name='Carlos Mauricio',
            last_name='Reyes', second_last_name='Escudero',
            province='Sancti Spiritu', municipality='Majayigua',
            phone='+53 58607451', address='Sukasa')

def create_test_card(val=''):
        return Card(
            card_name=f'test card{str(val)}',
            description='This is a description',
        )
        
def create_test_monster_card(self):
        return MonsterCard(
            card=create_test_card(),attack=2000,defense=2000,
            attribute='WA',level=12,is_effect=False,
        )
        
def create_test_cards(ammount):
    '''
    Method for creating one or more test cards
    '''
    res=[]
    for val in range(ammount):
        res.append(create_test_card(val))
    return res
        
def create_test_effect_card(self):
    return EffectCard(
        card=create_test_card(),card_type='T',
    )
        
class CardModelTests(TestCase):
    '''
    Tests for card and card 'inherate' models
    '''
    # TEST METHODS
    def test_card_attribute_is_not_in_choices(self):
        '''
        The card_attribute should be one of the listed in the model
        '''
        test_card=create_test_monster_card()
        test_card.attribute='NO'
        with self.assertRaises(exceptions.ValidationError):
            test_card.full_clean()
    def test_card_type_is_not_in_choices(self):
        '''
        The card_type should be one of the listed in the model
        '''
        test_card=create_test_effect_card()
        test_card.card_type="N"
        
        with self.assertRaises(exceptions.ValidationError):
            test_card.full_clean()
    def test_card_level_less_than_max_level(self):
        '''
        The card level should be less than the maximum
        '''
        test_card=create_test_monster_card()
        test_card.level = 20
        with self.assertRaises(exceptions.ValidationError):
            test_card.full_clean()
    def test_card_level_greater_than_min_level(self):
        '''
        The card level should be greater than the minimun
        '''
        test_card=create_test_monster_card()
        test_card.level=0
        with self.assertRaises(exceptions.ValidationError):
            test_card.full_clean()
            
class PlayerTests(TestCase):    
    def test_phone_is_not_real(self):
        '''
        Checks the phone number is not something dumb like +53 12345678
        '''
        test_player=create_test_player()
        test_player.phone='+53 12345678'
        with self.assertRaises(exceptions.ValidationError):
            test_player.full_clean()
        
    def test_phone_is_not_giverish(self):
        '''
        Checks the phone number is made of digits
        '''
        test_player=create_test_player()
        test_player.phone='salchichas'
        with self.assertRaises(exceptions.ValidationError):
            test_player.full_clean()
            
    def test_phone_is_not_too_long(self):
        '''
        Checks the phonenumber is not too long for a phonenumber
        '''
        test_player=create_test_player()
        test_player.phone='+53413123424532645374374'
        with self.assertRaises(exceptions.ValidationError):
            test_player.full_clean()
            
    def test_phone_has_international_prefix(self):
        '''
        Checks phonenumber has the + prefix
        '''
        test_player=create_test_player()
        test_player.phone='5355641257'
        with self.assertRaises(exceptions.ValidationError):
            test_player.full_clean()
            
    def test_phone_is_optional(self):
        '''
        Checks the phone number can be empty
        '''
        test_player=create_test_player()
        test_player.phone=''
        test_player.full_clean()
        
    def test_fullname_works(self):
        '''
        Checks the returning of the players fullname is correct
        '''
        test_player=create_test_player()
        self.assertEqual(test_player.fullname(),'Carlos Mauricio Reyes Escudero')
        
    # UNCOMENTIG THIS TEST WILL GIVE A FAILURE
    # Note to future dev: FIX THIS ERROR
    
    # def test_fullname_has_no_whitespace(self):
    #     '''
    #     Checks the fullname does not return whitespace
    #     '''
    #     test_player=create_test_player(number)
    #     test_player.first_name='               Carlos        Mauricio   '
    #     self.assertEqual(test_player.fullname(),'Carlos Mauricio Reyes Escudero')    

class CardInDeckTests(TestCase):       
    def test_check_existence_of_existing_element(self):
        '''
        Tests that it returns correctly the existence of 
        a CardInDeck data that exist in the database
        '''
        self.assertEqual(True,False)
    
    def test_check_existence_of_non_existing_element_deck(self):
        '''
        Tests that it raises a ValueError when trying to 
        check the existence of an CardInDeck element in 
        wich the deck_id is not present in the database
        '''
        self.assertEqual(True,False)
        
    def test_check_existence_of_non_existing_element_card(self):
        '''
        Tests that it raises a ValueError when trying to 
        check the existence of an CardInDeck element in 
        wich the card_id is not present in the database
        '''
        self.assertEqual(True,False)
        
    def test_check_existence_of_non_existing_element_deck_and_card(self):
        '''
        Tests that it raises a ValueError when trying to 
        check the existence of an CardInDeck element in 
        wich neither the deck_id or the card_id
        is not present in the database
        '''
        self.assertEqual(True,False)
        
    def test_card_appearence_limit_validator(self):
        '''
        Tests that a card can't be added more than
        MAX_AMMOUNT_OF_CARD_IN_DECK times in the same deck.
        '''
        self.assertEqual(True,False)
        
    def test_deck_type_limit_validator_for_main_deck(self):
        '''
        Tests that the ammount of cards int the main_deck
        is <= than AMMOUNT_OF_CARDS_PER_DECK_TYPE['main_deck']
        '''
        self.assertEqual(True,False)
        
    def test_deck_type_limit_validator_for_side_deck(self):
        '''
        Tests that the ammount of cards int the side_deck
        is <= than AMMOUNT_OF_CARDS_PER_DECK_TYPE['side_deck']
        '''
        self.assertEqual(True,False)
        
    def test_deck_type_limit_validator_for_extra_deck(self):
        '''
        Tests that the ammount of cards int the extra_deck
        is <= than AMMOUNT_OF_CARDS_PER_DECK_TYPE['extra_deck']
        '''
        self.assertEqual(True,False)
        
    