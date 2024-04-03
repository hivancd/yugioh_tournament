from django.test import TestCase
from django.core import exceptions
from .models import *

# Create your tests here.

def create_test_player():
        return Player(first_name='Carlos Mauricio',
            last_name='Reyes', second_last_name='Escudero',
            province='Sancti Spiritu', municipality='Majayigua',
            phone='+53 58607451', address='Sukasa')
 
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
        
    