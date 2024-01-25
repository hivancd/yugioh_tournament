from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
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
        