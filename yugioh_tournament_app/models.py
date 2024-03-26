from typing import Any
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django import forms
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from django import forms
import datetime as dt
from django.contrib.auth.models import User

    
def copy_fields(original,copy):
    keys = list(original.__dict__.keys())[2:]
    for k in keys:
        copy.__setattr__(k,original.__dict__[k])

class Player(models.Model):
            
    # EN EL MODELO USER VIENEN PROPS DE USERNAME, FIRST_NAME, LAST_NAME, IS_STAFF, PASSWORD, ETC
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    second_last_name=models.CharField(max_length=200)
    province=models.CharField(max_length=200)
    municipality=models.CharField(max_length=200)
    phone=models.CharField(max_length=15,blank=True)
    address=models.CharField(max_length=200)
    
    def del_player(self):
        return self.user.delete()
    
    def insert(username,password,first_name,last_name,second_last_name,province,municipality,phone,address,is_staff=False):
        if(username[0]=='@'):
            raise ValidationError('Username cant start with the character @')
        Player.is_valid_phonenumber(phone)
        u=User(username=username,password=password,first_name=first_name,last_name=last_name,is_staff=is_staff)
        p = Player(user=u,second_last_name=second_last_name,province=province,municipality=municipality,phone=phone,address=address)
        u.save()
        p.save()
        return p
        
    def get_fake_user(self):
        fake_user=User()
        user_keys=list(self.user.__dict__.keys())[2:]
        for uk in user_keys:
            fake_user.__setattr__(uk,self.user.__dict__[uk])
        fake_user.username = '@' + fake_user.username
        return fake_user
        
    def get_copy(self):
        copy = Player() 
        keys = list(self.__dict__.keys())[2:]
        for k in keys:
            copy.__setattr__(k,self.__dict__[k])
        return copy

        
    def modify(self, attributes:list, values:list):
        prev:Player = self.get_copy()
        fake_user:User = self.get_fake_user()
        for i in range(len(attributes)):
            try:
                prev.__getattribute__(attributes[i])
                prev.__setattr__(attributes[i], values[i])
            except:
                # print('not player props')
                try:
                    fake_user.__getattribute__(attributes[i])
                    val=values[i]
                    if(attributes[i]=='username'):
                        if val[0]=='@':
                            raise ValidationError('Username cant start with @')
                        val='@'+val
                    fake_user.__setattr__(attributes[i], val)
                except:
                    print('property not found.')
                    pass    
        try:
            Player.is_valid_phonenumber(prev.phone)
            prev.clean_fields(exclude= ['user'])
            fake_user.full_clean()
            copy_fields(prev,self)
            fake_user.username = fake_user.username[1:]
            copy_fields(fake_user,self.user)
        except:
            print('validation error')
        return
          
    def is_valid_phonenumber(phone):
        if phone:
            try:
                if not PhoneNumber.from_string(phone).is_valid():
                    raise ValueError('The phone number field is not correct.')
            except:
                raise ValueError('The phone number field is not correct.')
    
    def add_deck(self,deck_name,main_deck,side_deck,extra_deck,archtype='Mixto'):
        Deck.insert_deck(deck_name,main_deck,side_deck,extra_deck,self,archtype)
        
    def fullname(self):
        return self.user.username
    
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
    champion=models.OneToOneField(Player,on_delete=models.RESTRICT,blank=True,default=None)
    
    def __str__(self) -> str:
        return self.tournament_name
    
    def insert_tournament(name,start_datetime,address,champion=None):
        t=Tournament(tournament_name=name,start_datetime=start_datetime,address=address,champion=champion)
        t.save()
    
    def check_champion_is_participant(self,champion) -> bool:
        participants= self.participants.all()
        return champion in participants
        
    def set_champion(self, player:Player):
        if self.check_champion_is_participant(player):
            self.champion=player
            return
        raise ValidationError(f'Tried to set {player.user.username} as a champion in {self.tournament_name} but he is not a participant.')
        
    
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
    
# from yugioh_tournament_app.models import *
# Player.insert_new_player('ale','jan','dro','Matanzas','Varadero','','otracasa')
# Player.insert_new_player('mau','ri','cio','sancti spiritu','majayigua','','sucasa')
# p1=Player.objects.get(pk=1)
# p2=Player.objects.get(pk=2)
# p1.add_deck('deck de alejandro',40,10,10)
# p2.add_deck('deck de mauricio',45,13,2)
# d1=Deck.objects.get(pk=1)
# from datetime import datetime as dt
# from datetime import timedelta as delta
# Tournament.insert_tournament('torneo de alejandro y mauricio',dt.now(),'el rinconcito del amor')
