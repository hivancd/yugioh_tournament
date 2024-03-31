from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login as auth_login
from .models import Deck, Player , Tournament
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.template import loader
from django.http import Http404
from django.contrib import messages
from django.core.paginator import Paginator
from yugioh_tournament_app import models
from .forms import DeckForm, TournamentForm , DuelForm,PlayerProfileForm
from django.contrib import messages
from django.views.generic.edit import UpdateView
from django.contrib.auth import logout

def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            messages.info(request, "You need to be logged in to view this page.")
            return HttpResponseRedirect("/yugioh_tournament_app/login/")
            

    return wrapper


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "You need to be an admin to view this page.")
            return HttpResponseRedirect("/yugioh_tournament_app/tournaments/")

    return wrapper


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if "login" in request.POST:
            if len(username) < 4 or len(password) < 4:
                context = {
                    "error": "Username and password must be at least 4 characters long"
                }
                template = loader.get_template("yugioh_tournament_app/login.html")
                return HttpResponse(template.render(context, request))

            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return HttpResponseRedirect("/yugioh_tournament_app/main/")

            else:
                context = {"error": "Failed to authenticate. Please try again."}
                template = loader.get_template("yugioh_tournament_app/login.html")
                return HttpResponse(template.render(context, request))

        elif "register" in request.POST:
            return HttpResponseRedirect("/yugioh_tournament_app/register/")
        elif "change_password" in request.POST:
            return HttpResponseRedirect("/yugioh_tournament_app/change_password/")
    else:
        template = loader.get_template("yugioh_tournament_app/login.html")
        return HttpResponse(template.render(request=request))


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        second_last_name = request.POST.get("second_last_name")
        province = request.POST.get("province")
        municipality = request.POST.get("municipality")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        if "login" in request.POST:
            return HttpResponseRedirect("/yugioh_tournament_app/login/")
        elif (
            "register" in request.POST
            and username != ""
            and password != ""
        ):
            if len(username) < 4 or len(password) < 4:
                context = {
                    "error": "Username and password must be at least 4 characters long"
                }
                template = loader.get_template("yugioh_tournament_app/register.html")
                return HttpResponse(template.render(context, request))
            if password != confirm_password:
                context = {
                    "error": "passwords not matching "
                }
                template = loader.get_template("yugioh_tournament_app/register.html")
                return HttpResponse(template.render(context, request))
            elif User.objects.filter(username=username).exists():
                context = {"error": "Username already exists"}
                template = loader.get_template("yugioh_tournament_app/register.html")
                return HttpResponse(template.render(context, request))

            else:
                user = User.objects.create_user(
                    username=username, password=password
                )
                user.save()
                player = Player(
                    user=user,
                    second_last_name=request.POST.get("second_last_name"),
                    province=request.POST.get("province"),
                    municipality=request.POST.get("municipality"),
                    phone=request.POST.get("phone"),
                    address=request.POST.get("address"),
                )
                player.save()
                context = {"message": "Registered Successfully"}
                auth_login(request, user)
                return HttpResponseRedirect("/yugioh_tournament_app/main/")

        elif "register" in request.POST:
            context = {"error": "Invalid Username or Password"}
            template = loader.get_template("yugioh_tournament_app/register.html")
            return HttpResponse(template.render(context, request))

    else:
        template = loader.get_template("yugioh_tournament_app/register.html")
        return HttpResponse(template.render(request=request))


def change_password(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        if "change" in request.POST:
            if len(username) < 4 or len(password) < 4:
                context = {
                    "error": "Username and password must be at least 4 characters long"
                }
                template = loader.get_template(
                    "yugioh_tournament_app/change_password.html"
                )
                return HttpResponse(template.render(context, request))

            user = authenticate(username=username, password=password)
            if user is None:
                context = {"error": "Invalid Username or Password"}
                template = loader.get_template(
                    "yugioh_tournament_app/change_password.html"
                )
                return HttpResponse(template.render(context, request))

            user.password = make_password(new_password)
            user.save()
            context = {"message": "Password Changed Successfully"}
            template = loader.get_template("yugioh_tournament_app/change_password.html")
            return HttpResponse(template.render(context, request))

        elif "login" in request.POST:
            return HttpResponseRedirect("/yugioh_tournament_app/login/")

    else:
        template = loader.get_template("yugioh_tournament_app/change_password.html")
        return HttpResponse(template.render(request=request))


@login_required
def main(request):
    template = loader.get_template("yugioh_tournament_app/main.html")
    return HttpResponse(template.render(request=request))


@login_required
def tournaments(request):
    tournament_list = Tournament.objects.all()
    paginator = Paginator(tournament_list, 10)  # Show 10 tournaments per page

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request, "yugioh_tournament_app/tournaments.html", {"page_obj": page_obj}
    )


# def deck_list(request):
#     template = loader.get_template("yugioh_tournament_app/deck_list.html")
#     decks_data = models.Deck.objects.all()
#     context = {
#         "decks": decks_data,
#     }
#     return HttpResponse(template.render(context, request))
@login_required
def deck_list(request):
    decks = Deck.objects.all()
    paginator = Paginator(decks, 10)  # Show 10 decks per page

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request, "yugioh_tournament_app/deck_list.html", {"page_obj": page_obj}
    )


@login_required
def statistics(request):
    template = loader.get_template("yugioh_tournament_app/statistics.html")
    players_data = models.Player.objects.all()
    paginator = Paginator(players_data, 10)  # Show 10 players per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "players": players_data,
        "page_obj": page_obj,  # Add this line
    }
    return HttpResponse(template.render(context, request))


@login_required
def manual(request):
    template = loader.get_template("yugioh_tournament_app/manual.html")
    return HttpResponse(template.render())


@login_required
def edit_profile(request):
    player = Player.objects.get(user=request.user)
    if request.method == "POST":
        form = PlayerProfileForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect("main")
    else:
        form = PlayerProfileForm(instance=player)
    return render(request, "yugioh_tournament_app/edit_profile.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def create_deck(request):
    if request.method == "POST":
        form = DeckForm(request.POST)
        if form.is_valid():
            deck = form.save(
                commit=False
            )  # commint false es para que no guarde en la base de datos todavia
            deck.player = Player.objects.get(user=request.user)
            deck.save()
            messages.success(request, "Deck created successfully")
            return redirect(deck_list)
    else:
        form = DeckForm()
    return render(request, "yugioh_tournament_app/create_deck.html", {"form": form})


class DeckUpdateView(UpdateView):
    model = Deck
    form_class = DeckForm
    template_name = "yugioh_tournament_app/edit_deck.html"
    success_url = "/yugioh_tournament_app/deck_list/"

    def get_object(self):
        deck_id = self.kwargs.get("deck_id")
        return get_object_or_404(Deck, id=deck_id)


@login_required
@admin_required
def create_tournament(request):
    if request.method == "POST":
        form = TournamentForm(request.POST)
        if form.is_valid():
            Tournament.insert_tournament(
                name=form.cleaned_data["tournament_name"],
                start_datetime=form.cleaned_data["start_datetime"],
                address=form.cleaned_data["address"],
                # champion=form.cleaned_data['champion'],  # Uncomment this line if your form includes a 'champion' field
            )
            messages.success(request, "Tournament created successfully")
            redirect(tournaments)
    else:
        form = TournamentForm()
    return render(
        request, "yugioh_tournament_app/create_tournament.html", {"form": form}
    )


@admin_required
def add_duel(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if request.method == "POST":
        form = DuelForm(request.POST)
        if form.is_valid():
            duel = form.save(commit=False)
            duel.tournament = tournament
            duel.save()
            messages.success(request, "Match added successfully")
            redirect(tournaments)
    else:
        form = DuelForm()
    return render(request, "yugioh_tournament_app/add_duel.html", {"form": form})
