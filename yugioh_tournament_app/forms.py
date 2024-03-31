from django import forms
from .models import Deck, Tournament, Player, Duel


class DeckForm(forms.ModelForm):
    ARCHETYPE_CHOICES = [
        ("agua", "Agua"),
        ("tierra", "Tierra"),
        ("fuego", "Fuego"),
        ("aire", "Aire"),
        ("luz", "Luz"),
        ("oscuridad", "Oscuridad"),
        ("mixto", "Mixto"),
    ]

    archtype = forms.ChoiceField(choices=ARCHETYPE_CHOICES)

    class Meta:
        model = Deck
        fields = [
            "deck_name",
            "main_deck",
            "side_deck",
            "extra_deck",
            "archtype",
        ]


class TournamentForm(forms.ModelForm):
    start_datetime = forms.DateTimeField(
        input_formats=["%d/%m/%Y %H:%M"],
        widget=forms.DateTimeInput(attrs={"placeholder": "dd/mm/yyyy hh:mm"}),
    )
    class Meta:
        model = Tournament
        fields = ["tournament_name", "start_datetime", "address"]


class DuelForm(forms.ModelForm):
    class Meta:
        model = Duel
        fields = [
            "player1",
            "player2",
            "date",
            "tournament_phase",
            "winner",
        ]


class PlayerProfileForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ["province", "municipality", "phone", "address"]
