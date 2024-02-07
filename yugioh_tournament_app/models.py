from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django import forms
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from django import forms
import datetime as dt
# Create your models here.

class Player(models.Model):
            
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200)
    second_last_name=models.CharField(max_length=200)
    province=models.CharField(max_length=200)
    municipality=models.CharField(max_length=200)
    phone=models.CharField(max_length=15,blank=True)
    address=models.CharField(max_length=200)
    
    def insert_new_player(first_name,last_name,second_last_name,province,municipality,phone,address):
        Player.is_valid_phonenumber(phone)
        p = Player(first_name=first_name,last_name=last_name,second_last_name=second_last_name,province=province,municipality=municipality,phone=phone,address=address)
        p.save()
    
    def add_deck(self,deck_name,main_deck,side_deck,extra_deck,archtype='Mixto'):
        Deck.insert_deck(deck_name,main_deck,side_deck,extra_deck,self,archtype)
        
    def is_valid_phonenumber(phone):
        if phone:
            try:
                if not PhoneNumber.from_string(phone).is_valid():
                    raise ValidationError('The phone number field is not correct.')
            except:
                raise ValidationError('The phone number field is not correct.')
    
    def fullname(self):
        return ' '.join([self.first_name,self.last_name,self.second_last_name.strip()])
    
    def __str__(self):
        return self.fullname()    
    
class Deck(models.Model): 
    MIN_MAIN_DECK_SIZE=40
    AMMOUNT_OF_CARDS_PER_DECK_TYPE={
        'main_deck':60,
        'side_deck':15,
        'extra_deck':15,
    }
    
    deck_name=models.CharField(max_length=200)
    main_deck=models.PositiveIntegerField(validators=[MinValueValidator(MIN_MAIN_DECK_SIZE),MaxValueValidator(AMMOUNT_OF_CARDS_PER_DECK_TYPE['main_deck'])])
    side_deck=models.PositiveIntegerField(validators=[MaxValueValidator(AMMOUNT_OF_CARDS_PER_DECK_TYPE['side_deck'])])
    extra_deck=models.PositiveIntegerField(validators=[MaxValueValidator(AMMOUNT_OF_CARDS_PER_DECK_TYPE['extra_deck'])])
    archtype=models.CharField(max_length=200,default='Mixto')
    player=models.ForeignKey(Player,on_delete=models.CASCADE, related_name='decks')
        
    def insert_deck(deck_name,main_deck,side_deck,extra_deck,owner,archtype='Mixto'):
        d=Deck(deck_name=deck_name,main_deck=main_deck,side_deck=side_deck,extra_deck=extra_deck,player=owner,archtype=archtype)
        d.save()
        
    def __str__(self):
        return self.deck_name
            
class Tournament(models.Model):
    tournament_name=models.CharField(max_length=200)
    start_datetime=models.DateTimeField()
    address=models.CharField(max_length=200)
    
    def __str__(self) -> str:
        return self.tournament_name
    
    def insert_tournament(name,start_datetime,address):
        t=Tournament(tournament_name=name,start_datetime=start_datetime,address=address)
        t.save()
    
class TournamentParticipant(models.Model): # TEST PENDING
    tournament=models.ManyToManyField(Tournament, related_name='participants')
    deck=models.ManyToManyField(Deck)
    inscription_date=models.DateTimeField(default=dt.datetime.now())
    
    def check_existence(player_id,deck_id,tournament_id): # TEST PENDING
        '''
        Given the ids raises an error if they dont exist in their respective tables.
        '''
        if not Deck.objects.filter(pk=deck_id).exists():
            raise ValueError(f'There is no element with id=={deck_id} in the table Deck.')
        if not Player.objects.filter(pk=player_id).exists():
            raise ValueError(f'There is no element with id=={player_id} in the table Player.')
        if not Tournament.objects.filter(pk=tournament_id).exists():
            raise ValueError(f'There is no element with id=={tournament_id} in the table Tournament.')
        
    def deck_is_from_participant_validator(player,deck):
        if not (deck.owner.id == player.id):
            raise ValueError(f'The deck does is not property of the given player')
        if TournamentParticipant.objects.filter(player=player.id).exists():
            raise ValueError(f'This player is already participating in this tournament')
        
    def inscription_in_time_validator(tournament,inscription_date):
        if inscription_date > tournament.start_datetime:
            raise ValidationError(f'This tournament already started, no new participant can be added')
        
    def check_validations(tournament,player,deck,inscription_date):
        TournamentParticipant.check_existence(tournament_id=tournament.id,player_id=player.id,deck_id=deck.id)
        TournamentParticipant.deck_is_from_participant_validator(player=player,deck=deck)
        TournamentParticipant.inscription_in_time_validator(tournament=tournament, inscription_date=inscription_date)
        
    def add_participant(tournament,player,deck,inscription_date):
        TournamentParticipant.check_validations(tournament,player,deck,inscription_date)
        element = TournamentParticipant(tournament=tournament,player=player,deck=deck,inscription_date=inscription_date)
        element.save()
        
    def __str__(self):
        return f'The player {self.player.__str__()} participates in the tournament "{self.tournament.__str__()}" using the deck "{self.deck.__str__()}".'
        
class Duel(models.Model):
    RESULTS={
        'player1':'player1',
        'player2':'player2',
        'tie':'tie',
    }
    player1=models.ManyToManyField(Player, related_name='was_player1')
    player2=models.ManyToManyField(Player, related_name='was_player2')
    tournament=models.ManyToManyField(Tournament,related_name='duels')
    date=models.DateTimeField()
    tournament_phase=models.CharField(max_length=200)
    winner=models.CharField(max_length=7,choices=RESULTS)
    
    def get_winner(self):
        if self.winner == 'player1':
            return self.player1
        if self.winner == 'player2':
            return self.player2
        else:
            return 'It was a tie'
        
    def get_loser(self):
        if self.winner == 'player1':
            return self.player2
        if self.winner == 'player2':
            return self.player1
        else:
            return 'It was a tie'
        
    def __str__(self):
        return f'The player {self.player1} faced {self.player2} in the tournament: "{self.tournament}" in the {self.tournament_phase}.'