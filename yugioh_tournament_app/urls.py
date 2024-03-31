from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login, name="login"),  # type: ignore
    path("logout/", views.logout_view, name="logout"),
    path("main/", views.main, name="main"),
    path("register/", views.register, name="register"),  # type: ignore
    path("change_password/", views.change_password, name="change_password"),  # type: ignore
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("tournaments/", views.tournaments, name="tournaments"),
    path("deck_list/", views.deck_list, name="deck_list"),
    path("statistics/", views.statistics, name="statistics"),
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
]
