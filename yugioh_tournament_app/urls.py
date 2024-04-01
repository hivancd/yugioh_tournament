from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login, name="login"),  # type: ignore
    path("logout/", views.logout_view, name="logout"),
    path("", views.main, name="main"),
    path("register/", views.register, name="register"),  # type: ignore
    path("change_password/", views.change_password, name="change_password"),  # type: ignore
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("tournaments/", views.tournaments, name="tournaments"),
    path("statistics/", views.statistics, name="statistics"),
    path("statistics/download/<int:stat_id>/", views.download_statistics, name="download_statistics"),
    path("deck_list/", views.deck_list, name="deck_list"),
    path("players/", views.players, name="players"),
    path("manual/", views.manual, name="manual"),
    path("deck_list/create_deck/", views.create_deck, name="create_deck"),
    path(
        "tournaments/create_tournament/",
        views.create_tournament,
        name="create_tournament",
    ),
    path(
        "deck_list/edit_deck/<int:deck_id>/",
        views.DeckUpdateView.as_view(),
        name="edit_deck",
    ),
    path("tournaments/<int:tournament_id>/add_duel/", views.add_duel, name="add_duel"),
    path("tournaments/tournament_details/<int:tournament_id>/", views.tournament_details, name="tournament_details"),
    path("confirm_participation", views.confirm_participation, name="confirm_participation"),
    path('tournaments/<int:tournament_id>/close/', views.close_tournament, name='close_tournament'),

    path("make_admin/<int:user_id>", views.make_admin, name="make_admin"),
    path("revoke_admin/<int:user_id>", views.revoke_admin, name="revoke_admin"),

    path("confirm_participation_action/<int:participant_id>", views.confirm_participation_action, name="confirm_participation_action"),
]
