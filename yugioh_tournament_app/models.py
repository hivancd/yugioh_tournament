from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django import forms
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
# Create your models here.

class Card(models.Model):   
    card_name=models.CharField(max_length=200)
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
    
class Deck(models.Model): # CHECK AMMOUNT=RELATION DE CARTAS
    deck_name=models.CharField(max_length=200)
    main_deck_size=models.PositiveIntegerField(
        validators=[
            MinValueValidator(40),
            MaxValueValidator(60),
        ]
    )
    side_deck_size=models.PositiveIntegerField(
        validators=[
            MaxValueValidator(15),
        ]
    )
    extra_deck_size=models.PositiveIntegerField(
        validators=[
            MaxValueValidator(15),
        ]
    )
    
