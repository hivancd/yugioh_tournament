from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django import forms
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from django import forms
# Create your models here.

class Card(models.Model):   
    card_name=models.CharField(max_length=200,unique=True)
    description=models.CharField(max_length=200)

    def __str__(self):
        return self.card_name
        
class EffectCard(models.Model):
    CARD_TYPES={
        'S':'Spell',
        'T':'Trap',
    }
    card=models.OneToOneField(
        Card,
        on_delete = models.CASCADE,
        primary_key=True,
    )
    card_type=models.CharField(
        max_length=2,
        choices=CARD_TYPES,
    )
    
        
class MonsterCard(models.Model):
    CARD_ATTRIBUTES={
        'DA':'Dark',
        'DI':'Divine',
        'E':'Earth',
        'F':'Fire',
        'L':'Light',
        'WA':'Water',
        'WI':'Wind',
    }    
    MAX_LEVEL=13
    card = models.OneToOneField(
        Card,
        on_delete = models.CASCADE,
        primary_key=True,
    )
    attack=models.PositiveIntegerField()
    defense=models.PositiveIntegerField()
    attribute=models.CharField(
        max_length=2,
        choices=CARD_ATTRIBUTES,
    )
    level=models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(MAX_LEVEL),
        ],
        null=True,
    )
    is_effect=models.BooleanField()    
    
    def __str__(self):
        return self.card.card_name
        
    class Meta:
        constraints=[
            models.CheckConstraint( 
                name="%(app_label)s_%(class)s_attribute_valid",
                check=models.Q(attribute__in=['DA','DI','E','F','L','WA','WI',])
            ),
        ]

class Player(models.Model):
    #De los jugadores se quiere guardar el nombre completo, municipio, provincia, teléfono (opcional) y la dirección
    
    def is_valid_phonenumber(phone):
        if phone:
            try:
                if not PhoneNumber.from_string(phone).is_valid():
                    raise ValidationError('The phone number field is not correct.')
            except:
                raise ValidationError('The phone number field is not correct.')
            
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200)
    second_last_name=models.CharField(max_length=200)
    province=models.CharField(max_length=200)
    municipality=models.CharField(max_length=200)
    phone=models.CharField(max_length=15,blank=True,validators=[is_valid_phonenumber])
    address=models.CharField(max_length=200)
    
    def fullname(self):
        return ' '.join([self.first_name,self.last_name,self.second_last_name.strip()])
    def __str__(self):
        return self.fullname()    
    
class Deck(models.Model): 
    deck_name=models.CharField(max_length=200)
    cards_in_deck=models.ManyToManyField(Card,through='CardInDeck',blank=True)
    # main_deck_size=models.PositiveIntegerField(
    #     validators=[
    #         MaxValueValidator(60),
    #     ]
    # )
    # side_deck_size=models.PositiveIntegerField(
    #     validators=[
    #         MaxValueValidator(15),
    #     ]
    # )
    # extra_deck_size=models.PositiveIntegerField(
    #     validators=[
    #         MaxValueValidator(15),
    #     ]
    # )
    
    # def get_card_ammount(self,deck_type=''):
    #     '''
    #     This function returns the ammount of cards in a deck.
    #     The parameter deck_type can be passed to get the ammount of cards 
    #     of an specific deck type (Ex: main_deck)
    #     '''
    #     # print(f'in get_card_ammount deck_type=={deck_type}')
    #     print(self.cards_in_deck.filter(deck_type=deck_type))
    #     if deck_type=='':
    #         print('first if')
    #         return len(self.cards_in_deck.all())
    #     else:
    #         try:
    #             return len(self.cards_in_deck.filter(deck_type=deck_type))
    #         except:
    #             raise ValueError('Received an unexisting deck type')
            
    def is_valid_to_play(self):
        return CardInDeck.objects.filter(deck=self,deck_type='main_deck').count()>=CardInDeck.MIN_MAIN_DECK_SIZE
    
    def __str__(self):
        return self.deck_name
            

class CardInDeck(models.Model): # TEST PENDING
    MIN_MAIN_DECK_SIZE=40
    DECK_TYPES={
        'main_deck':'main_deck',
        'side_deck':'side_deck',
        'extra_deck':'extra_deck',
    }
    AMMOUNT_OF_CARDS_PER_DECK_TYPE={
        'main_deck':60,
        'side_deck':15,
        'extra_deck':15,
    }
    MAX_AMMOUNT_OF_CARD_IN_DECK=3
    deck_type=models.CharField(max_length=10,choices=DECK_TYPES)
    card=models.ForeignKey(Card,on_delete=models.CASCADE)
    deck=models.ForeignKey(Deck,on_delete=models.CASCADE)
    
    def card_in_deck_validator(self): # TEST PENDING
        '''
        Checks if the given card has reached the limit on the deck.
        '''
        card_ammount=len(CardInDeck.objects.filter(card=self.card,deck=self.deck))
        if card_ammount==CardInDeck.MAX_AMMOUNT_OF_CARD_IN_DECK:
            raise(ValidationError('The card '+self.card+' already was added '+ CardInDeck.MAX_AMMOUNT_OF_CARD_IN_DECK + ' times in this deck'))
    
    def deck_type_limit_validator(self): # TEST PENDING
        '''
        Checks if the deck has reached the card limit of that type
        '''
        if self.deck.cards_in_deck.filter(card=self.card).count() >= CardInDeck.MAX_AMMOUNT_OF_CARD_IN_DECK:
            raise ValidationError(f"Cannot add more than {CardInDeck.MAX_AMMOUNT_OF_CARD_IN_DECK} cards of the same type to the deck.")
        
    def check_existence(card_id,deck_id): # TEST PENDING
        '''
        Given the ids raises an error if they dont exist in their respective tables.
        '''
        if not Deck.objects.filter(pk=deck_id).exists():
            raise ValueError(f'There is no element with id=={deck_id} in the table Deck.')
        if not Card.objects.filter(pk=card_id).exists():
            raise ValueError(f'There is no element with id=={card_id} in the table Card.')
        
    def check_validations(card_id,deck_id,deck_type):# TEST PENDING
        CardInDeck.check_existence(card_id,deck_id)
        queryset = CardInDeck.objects.filter(card=card_id,deck=deck_id)
        if queryset.exists():
            queryset[0].card_in_deck_validator()
            deck_type_queryset=queryset.filter(deck_type=deck_type)
            if deck_type_queryset.exists():
                deck_type_queryset[0].deck_type_limit_validator()
                
    def add_element(card,deck,deck_type): # TEST PENDING
        CardInDeck.check_validations(card.id,deck.id,deck_type)
        element = CardInDeck(card=card,deck=deck,deck_type=deck_type)
        element.save()
              
    def __str__(self):
        return self.card.__str__() + ' is in the ' + self.deck_type +' of the deck: ' + self.deck.__str__()
