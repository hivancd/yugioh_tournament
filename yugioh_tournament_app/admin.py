from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Player)
admin.site.register(Deck)
admin.site.register(TournamentParticipant)
admin.site.register(Match)
admin.site.register(Tournament)
