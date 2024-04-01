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
from django.utils import timezone as tz
from django.db.models import Count
from django.db.models import F, Value as V
# import pytz
    
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
    
    @classmethod
    def insert(cls,username,password,first_name,last_name,second_last_name,province,municipality,phone,address,is_staff=False):
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
                try:
                    fake_user.__getattribute__(attributes[i])
                    val=values[i]
                    if(attributes[i]=='username'):
                        if val[0]=='@':
                            raise ValidationError('Username cant start with @')
                        val='@'+val
                    fake_user.__setattr__(attributes[i], val)
                except:
                    raise AttributeError('Tried to modify an Attribute in player model that is not existing.')
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
          
    @classmethod
    def is_valid_phonenumber(cls,phone):
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
        
    @classmethod
    def insert_deck(cls,deck_name,main_deck,side_deck,extra_deck,owner,archtype='Mixto'):
        d=Deck(deck_name=deck_name,main_deck=main_deck,side_deck=side_deck,extra_deck=extra_deck,player=owner,archtype=archtype)
        d.save()
        
    def __str__(self):
        return self.deck_name
            
class Tournament(models.Model):
    tournament_name=models.CharField(max_length=200)
    start_datetime=models.DateTimeField()
    address=models.CharField(max_length=200)
    champion=models.ForeignKey(Player,null=True,on_delete=models.RESTRICT)
    
    def __str__(self) -> str:
        return self.tournament_name
    
    @classmethod
    def insert_tournament(cls,name,start_datetime,address,champion=None):
        t=Tournament(tournament_name=name,start_datetime=start_datetime,address=address,champion=champion)
        t.save()
    
    def player_is_participant(self,champion:Player):
        participants= self.participants.all()
        for p in participants:
            if p.deck.player.id == champion.id:
                return True
        return False #'champion in participants'
        
    def set_champion(self, player:Player):
        if self.player_is_participant(player):
            self.champion=player
            return
        raise ValidationError(f'Tried to set {player.user.username} as a champion in {self.tournament_name} but he is not a participant.')
    
    def duel_validator(self,player1:Player,player2:Player,phase:str,winner1,winner2,datetime):
        condition1= (self.player_is_participant(player1) and self.player_is_participant(player2))
        condition3= datetime>=self.start_datetime
        def condition4():
            sum=(winner1 + winner2)
            if (sum <= 3):
                if sum==3 : return True
                else: return (winner1 - winner2 == 2) or (winner2 - winner1 == 2)
            return False
        return (condition1 and condition3 and condition4())
    
    def add_match(self,player1:Player,player2:Player,phase:str,winner1:int,winner2:int,datetime=tz.now()):
        is_valid=self.duel_validator(player1,player2,phase,winner1,winner2,datetime)
        if(not is_valid):
            raise ValidationError('Error inserting duel in Tournament.')
        d=Match(player1=player1,player2=player2,tournament=self,tournament_phase=phase,winner1=winner1,winner2=winner2,date=datetime)
        d.save()
    
class TournamentParticipant(models.Model): # TEST PENDING
    tournament=models.ForeignKey(Tournament,on_delete=models.CASCADE, related_name='participants')
    deck=models.ForeignKey(Deck,on_delete=models.RESTRICT, related_name='tournaments')
    inscription_date=models.DateTimeField(default=tz.now)
    is_aproved=models.BooleanField(default=False)
    
    @classmethod
    def check_existence(cls,player_id,deck_id,tournament_id): # TEST PENDING
        '''
        Given the ids raises an error if they dont exist in their respective tables.
        '''
        if not Deck.objects.filter(pk=deck_id).exists():
            raise ValueError(f'There is no element with id=={deck_id} in the table Deck.')
        if not Player.objects.filter(pk=player_id).exists():
            raise ValueError(f'There is no element with id=={player_id} in the table Player.')
        if not Tournament.objects.filter(pk=tournament_id).exists():
            raise ValueError(f'There is no element with id=={tournament_id} in the table Tournament.')
    
    @classmethod
    def deck_is_from_participant_validator(cls,player,deck):
        if not (deck.player.id == player.id):
            raise ValueError(f'The deck is not property of the given player')
        
    @classmethod
    def player_is_already_in_tournament_validator(cls,tournament,player):
        for part in TournamentParticipant.objects.filter(tournament=tournament):
            if(part.deck.player.id==player.id):
                raise ValidationError('The player is already participating in this tournament.')
    
    @classmethod
    def inscription_in_time_validator(cls,tournament:Tournament,inscription_date:dt.datetime):
        if (inscription_date)> (tournament.start_datetime):
            raise ValidationError(f'This tournament already started, no new participant can be added')
        
    @classmethod
    def check_validations(cls,tournament,player,deck,inscription_date):
        TournamentParticipant.player_is_already_in_tournament_validator(tournament=tournament,player=player)
        TournamentParticipant.check_existence(tournament_id=tournament.id,player_id=player.id,deck_id=deck.id)
        TournamentParticipant.deck_is_from_participant_validator(player=player,deck=deck)
        #TournamentParticipant.inscription_in_time_validator(tournament=tournament, inscription_date=inscription_date)
        
    @classmethod
    def add_participant(cls,tournament,player,deck,inscription_date):
        TournamentParticipant.check_validations(tournament,player,deck,inscription_date)
        element = TournamentParticipant(tournament=tournament,deck=deck,inscription_date=inscription_date)
        element.save()
        
    def __str__(self):
        return f'player: {self.deck.player.__str__()} tournament: "{self.tournament.__str__()}" deck: "{self.deck.__str__()}".'
        
class Match(models.Model):
    player1=models.ForeignKey(Player, on_delete=models.RESTRICT, related_name='was_player1')
    player2=models.ForeignKey(Player, on_delete=models.RESTRICT, related_name='was_player2')
    winner1=models.PositiveSmallIntegerField(validators=[MaxValueValidator(3)])
    winner2=models.PositiveSmallIntegerField(validators=[MaxValueValidator(3)])
    tournament=models.ForeignKey(Tournament, on_delete=models.RESTRICT, related_name='duels')
    date=models.DateTimeField()
    tournament_phase=models.CharField(max_length=200)
    
    def get_winner(self):
        if self.winner1>self.winner2:
            return self.player1
        return self.player2
        
    def get_loser(self):
        if self.winner1>self.winner2:
            return self.player2
        return self.player1
        
    def __str__(self):
        return f'The player {self.player1} faced {self.player2} in the tournament: "{self.tournament}" in the {self.tournament_phase} phase.'

class Consult():
    
    @classmethod
    def sort_by_num_decks(cls):
        '''
        Returns the more used decks ordered.
        '''
        ans = Player.objects.annotate(num_decks=Count('decks')).order_by('-num_decks')
        return ans
    
    @classmethod
    def most_popular_archtypes(cls):
        '''
        Returns most popular archtypes.
        '''
        ans = Deck.objects.values('archtype').annotate(count=Count('archtype')).order_by('count').reverse()
        return ans
    
    @classmethod
    def most_popular_region_for_archtype(cls,archtype):
        ans= Deck.objects.filter(archtype=archtype).values('player__province', 'player__municipality').annotate(num_decks=Count('id')).order_by('-num_decks').first()
        return ans
    
    @classmethod
    def champions_for_municipality(cls,start_date,end_date=tz.now().date()):
        # ans= Deck.objects.filter(archtype=archtype).values('player__province', 'player__municipality').annotate(num_decks=Count('id')).order_by('-num_decks').first()
        # return ans
        midnight_time= dt.time(0,0,0,0)
        if(start_date==end_date):
            end_date+=dt.timedelta(days=1)
        start_date= dt.datetime.combine(start_date,midnight_time)
        end_date= dt.datetime.combine(end_date,midnight_time)        
        start_date=tz.make_aware(start_date)
        end_date=tz.make_aware(end_date)
        
        ans = {}
        for t in Tournament.objects.all():
            if t.champion and t.start_datetime >= start_date and t.start_datetime <=end_date:
                champ = t.champion
                decks = TournamentParticipant.objects.filter(tournament=t).values('deck').all()
                for d in decks:
                    deck=Deck.objects.get(pk=d['deck'])
                    if deck.player ==champ:
                        if champ.municipality in ans.keys():
                            ans[champ.municipality]+=1
                        else: 
                            ans[champ.municipality]=1
        return ans
    
    @classmethod
    def most_used_archtypes(cls):
        ans = {}
        for tp in TournamentParticipant.objects.all():
            if tp.deck.archtype in ans.keys():
                ans[tp.deck.archtype]+=1
            else: 
                ans[tp.deck.archtype]=1
        return ans
        
    @classmethod
    def champions_for_province(cls,start_date,end_date=tz.now().date()):
        # ans= Deck.objects.filter(archtype=archtype).values('player__province', 'player__municipality').annotate(num_decks=Count('id')).order_by('-num_decks').first()
        # return ans
        midnight_time= dt.time(0,0,0,0)
        if(start_date==end_date):
            end_date+=dt.timedelta(days=1)
        start_date= dt.datetime.combine(start_date,midnight_time)
        end_date= dt.datetime.combine(end_date,midnight_time)        
        start_date=tz.make_aware(start_date)
        end_date=tz.make_aware(end_date)
        
        ans = {}
        for t in Tournament.objects.all():
            if t.champion and t.start_datetime >= start_date and t.start_datetime <=end_date:
                champ = t.champion
                decks = TournamentParticipant.objects.filter(tournament=t).values('deck').all()
                for d in decks:
                    deck=Deck.objects.get(pk=d['deck'])
                    if deck.player ==champ:
                        if champ.province in ans.keys():
                            ans[champ.province]+=1
                        else: 
                            ans[champ.province]=1
        return ans
        
    @classmethod 
    def most_victories_in_time_period(cls,start_date,end_date=tz.now().date()):
        midnight_time= dt.time(0,0,0,0)
        if(start_date==end_date):
            end_date+=dt.timedelta(days=1)
        start_date= dt.datetime.combine(start_date,midnight_time)
        end_date= dt.datetime.combine(end_date,midnight_time)        
        start_date=tz.make_aware(start_date)
        end_date=tz.make_aware(end_date)
        
        player_vict= {}
        for d in Match.objects.all():
            if d.date >= start_date and d.date <=end_date:
                p=d.get_winner()
                if p.pk in player_vict.keys():
                    player_vict[p.pk] += 1
                else: 
                    player_vict[p.pk] = 1
        return player_vict
    
    @classmethod
    def most_used_archtype_in_tournament(cls,tournament:Tournament):
        ans=tournament.participants.values('deck__archtype').annotate(count=Count('id')).order_by('count')
        return ans
    
    @classmethod
    def most_used_archtype_in_tournament_round(cls,tournament:Tournament,round:str):
        duels=Match.objects.filter(tournament=tournament, tournament_phase=round)
        decks = TournamentParticipant.objects.filter(tournament=tournament).values('deck').all()
        ans={}
        for m in duels:
                p1 = m.player1
                p2 = m.player2
                for d in decks:
                    deck=Deck.objects.get(pk=d['deck'])
                    if deck.player == p1 or deck.player == p2:
                        if deck.archtype in ans.keys():
                            ans[deck.archtype]+=1
                        else: 
                            ans[deck.archtype]=1
        return ans
    
    @classmethod
    def winned_tournaments_for_archtype(cls,start_date,end_date=tz.now().date()):
        midnight_time= dt.time(0,0,0,0)
        if(start_date==end_date):
            end_date+=dt.timedelta(days=1)
        start_date= dt.datetime.combine(start_date,midnight_time)
        end_date= dt.datetime.combine(end_date,midnight_time)
        start_date=tz.make_aware(start_date)
        end_date=tz.make_aware(end_date)
        
        ans = {}
        for t in Tournament.objects.all():
            if t.champion and t.start_datetime >= start_date and t.start_datetime <=end_date:
                champ = t.champion
                decks = TournamentParticipant.objects.filter(tournament=t).values('deck').all()
                for d in decks:
                    deck=Deck.objects.get(pk=d['deck'])
                    if deck.player ==champ:
                        if deck.archtype in ans.keys():
                            ans[deck.archtype]+=1
                        else: 
                            ans[deck.archtype]=1
        return ans
    
                