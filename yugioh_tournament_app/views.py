from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login as auth_login
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.template import loader
from django.http import Http404, FileResponse
from django.contrib import messages
from django.core.paginator import Paginator
from yugioh_tournament_app import models
from .forms import DeckForm, TournamentForm , DuelForm, PlayerProfileForm, CloseTournamentForm
from django.contrib import messages
from django.views.generic.edit import UpdateView
from django.contrib.auth import logout

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

from io import BytesIO
import datetime

###
#   Decorators to mantain security of the site
###
def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            messages.info(request, "You need to be logged in to view this page.")
            return HttpResponseRedirect("/login/")
    
    return wrapper


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "You need to be an admin to view this page.")
            return HttpResponseRedirect("/tournaments/")

    return wrapper

###
#   Views
###
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if "login" in request.POST:
            if len(username) < 4 or len(password) < 4:
                context = {
                    "error": "Username and password must be at least 4 characters long"
                }
                template = loader.get_template("login.html")
                return HttpResponse(template.render(context, request))

            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return HttpResponseRedirect("/")

            else:
                context = {"error": "Failed to authenticate. Please try again."}
                template = loader.get_template("login.html")
                return HttpResponse(template.render(context, request))

        elif "register" in request.POST:
            return HttpResponseRedirect("/register/")
        elif "change_password" in request.POST:
            return HttpResponseRedirect("/change_password/")
    else:
        template = loader.get_template("login.html")
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
            return HttpResponseRedirect("/login/")
        elif (
            "register" in request.POST
            and username != ""
            and password != ""
        ):
            if len(username) < 4 or len(password) < 4:
                context = {
                    "error": "Username and password must be at least 4 characters long"
                }
                template = loader.get_template("register.html")
                return HttpResponse(template.render(context, request))
            if password != confirm_password:
                context = {
                    "error": "passwords not matching "
                }
                template = loader.get_template("register.html")
                return HttpResponse(template.render(context, request))
            elif User.objects.filter(username=username).exists():
                context = {"error": "Username already exists"}
                template = loader.get_template("register.html")
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
                return HttpResponseRedirect("/")

        elif "register" in request.POST:
            context = {"error": "Invalid Username or Password"}
            template = loader.get_template("register.html")
            return HttpResponse(template.render(context, request))

    else:
        template = loader.get_template("register.html")
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
                    "change_password.html"
                )
                return HttpResponse(template.render(context, request))

            user = authenticate(username=username, password=password)
            if user is None:
                context = {"error": "Invalid Username or Password"}
                template = loader.get_template(
                    "change_password.html"
                )
                return HttpResponse(template.render(context, request))

            user.password = make_password(new_password)
            user.save()
            context = {"message": "Password Changed Successfully"}
            template = loader.get_template("change_password.html")
            return HttpResponse(template.render(context, request))

        elif "login" in request.POST:
            return HttpResponseRedirect("/login/")

    else:
        template = loader.get_template("change_password.html")
        return HttpResponse(template.render(request=request))


@login_required
def main(request):
    template = loader.get_template("main.html")
    return HttpResponse(template.render(request=request))


@login_required
def tournaments(request):
    
    #Get the "search" form variables
    query = request.GET.get('q')
    dropdown_option = request.GET.get("dropdownName")

    #Filter for the wanted tournaments
    tournament_list = Tournament.objects.all()
    if dropdown_option == "name":
        tournament_list = Tournament.objects.filter(tournament_name__contains=query)
    elif dropdown_option == "address":
        tournament_list = Tournament.objects.filter(address__contains=query)
    
    #Limit the results
    paginator = Paginator(tournament_list, 10)  # Show 10 tournaments per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    #Render
    if query == None:
        query = ""

    return render(
        request, "tournaments.html", {"page_obj": page_obj, "query": query, "dropdown_option": dropdown_option}
    )

@login_required
def tournament_details(request, tournament_id):
    
    player_from_user = Player.objects.get(user=request.user)

    if request.method == "POST":
        tournament_info = Tournament.objects.get(id=tournament_id)
        deck_id = request.POST.get("dropdownName")
        deck_from_id = Deck.objects.get(id=deck_id)

        TournamentParticipant.add_participant(tournament_info, player_from_user, deck_from_id, datetime.datetime.now())
    
    decks = Deck.objects.filter(player=player_from_user)
    matches = Match.objects.filter(tournament__id=tournament_id)

    tournament_info = Tournament.objects.get(id=tournament_id)
    participants_total = TournamentParticipant.objects.filter(tournament__id=tournament_id)
    participants = TournamentParticipant.objects.filter(tournament__id=tournament_id, is_aproved=True)
    already_started = False #datetime.datetime.now() < tournament_info.start_datetime
    already_in_tournament = False
    for part in participants_total:
        if part.deck.player == player_from_user:
            already_in_tournament = True
            break

    template = loader.get_template('tournament_details.html')
    context = {
        'tournament_info': tournament_info,
        "participants": participants,
        "decks": decks,
        "user": request.user,
        "matches": matches,
        "already_started": already_started,
        "already_in_tournament": already_in_tournament
    }
    return HttpResponse(template.render(context, request))

@login_required
@admin_required
def confirm_participation(request):
    unconfirmed_participants = TournamentParticipant.objects.filter(is_aproved=False)
    context = {
        "user": request.user,
        "unconfirmed_participants": unconfirmed_participants
    }
    template = loader.get_template('confirm_participation.html')
    return HttpResponse(template.render(context, request))

@login_required
@admin_required
def confirm_participation_action(request, participant_id):
    participant = TournamentParticipant.objects.get(id=participant_id)
    participant.is_aproved = True
    participant.save()
    return redirect("confirm_participation")

@login_required
def deck_list(request):
    
    #Get the "search" form variables
    query = request.GET.get('q')
    
    #Filter for the desired decks
    player_from_user = Player.objects.filter(user=request.user)[0]
    decks = Deck.objects.filter(player=player_from_user)
    if query != None:
        decks = Deck.objects.filter(deck_name__contains=query, player=player_from_user).values()
    
    #Limit the result count
    paginator = Paginator(decks, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    #Render
    if query == None:
        query = ""

    return render(
        request, "deck_list.html", {"page_obj": page_obj, "query": query}
    )

@login_required
@admin_required
def make_admin(request, user_id):
    user = User.objects.filter(id=user_id)[0]
    user.is_staff = True
    user.is_superuser = True
    user.save() 
    return redirect("players")

@login_required
@admin_required
def revoke_admin(request, user_id):
    user = User.objects.filter(id=user_id)[0]
    user.is_staff = False
    user.is_superuser = False
    user.save()
    return redirect("players")

@login_required
def players(request):
    
    #Get the "search" form variables
    query = request.GET.get('q')
    dropdown_option = request.GET.get("dropdownName")

    #Filter for the desired players
    players_data = Player.objects.all()
    if dropdown_option == "name":
        players_data = Player.objects.filter(user__username__contains=query)
    elif dropdown_option == "lastName":
        players_data = Player.objects.filter(second_last_name__contains=query)
    elif dropdown_option == "provincia":
        players_data = Player.objects.filter(province__contains=query)
    elif dropdown_option == "municipio":
        players_data = Player.objects.filter(municipality__contains=query)
    elif dropdown_option == "address":
        players_data = Player.objects.filter(address__contains=query)

    #Limit the result count
    paginator = Paginator(players_data, 10)  # Show 10 players per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    #Render
    if query == None:
        query = ""
    
    context = {
        "page_obj": page_obj,
        "user": request.user,
        "query": query,
        "dropdown_option": dropdown_option
    }

    template = loader.get_template("players.html")
    return HttpResponse(template.render(context, request))

@login_required
def statistics(request):
    template = loader.get_template("statistics.html")
    players_data = models.Player.objects.all()
    paginator = Paginator(players_data, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    most_decks = models.Consult.sort_by_num_decks()
    popular_arch = models.Consult.most_popular_archtypes()
    popular_arch = models.Consult.most_popular_archtypes()
    
    context = {
        "players": players_data,
        "page_obj": page_obj,
        "user": request.user,
        "most_decks": most_decks,
        "popular_arch": popular_arch
    }
    return HttpResponse(template.render(context, request))

@login_required
def download_statistics(request, stat_id):
    
    #Function to create statistics pdf, and return the contents of it
    def create_pdf_table(rows):
        buf = BytesIO()
        pdf = SimpleDocTemplate(buf, pagesize=letter)

        table_data = []
        for row in rows:
            table_data.append(row)
        table = Table(table_data)

        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
        ])

        table.setStyle(table_style)

        pdf_table = []
        pdf_table.append(table)
        pdf.build(pdf_table)
        return buf.getvalue()
    
    def data_to_filas(players_data):
        players_data_list = [entry for entry in players_data]
        filas = []
        filas.append(list(players_data_list[0].keys()))
        for player in players_data:
            filas.append(list(player.values()))
        return filas

    data = []
    if stat_id == 0:
        data_raw = models.Consult.sort_by_num_decks()
        for d in data_raw:
            data.append({'nombre':d.user.username, 'deck count':d.num_decks})
    elif stat_id == 1:
        data = models.Consult.most_popular_archtypes()
    filas = data_to_filas(data)
    content = create_pdf_table(filas)

    response = HttpResponse(content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="stats.pdf"'

    return response

@login_required
def manual(request):
    template = loader.get_template("manual.html")
    context = {
        "user": request.user
    }
    return HttpResponse(template.render(context, request))

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
    return render(request, "edit_profile.html", {"form": form})


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
            #messages.success(request, "Deck created successfully")
            return redirect(deck_list)
    else:
        form = DeckForm()
    return render(request, "create_deck.html", {"form": form})


class DeckUpdateView(UpdateView):
    model = Deck
    form_class = DeckForm
    template_name = "edit_deck.html"
    success_url = "/deck_list/"

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
                address=form.cleaned_data["address"]
            )
            return redirect(tournaments)
    else:
        form = TournamentForm()
    return render(
        request, "create_tournament.html", {"form": form}
    )

@login_required
@admin_required
def add_duel(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if request.method == "POST":
        form = DuelForm(request.POST)
        if form.is_valid():
            duel = form.save(commit=False)
            duel.tournament = tournament
            duel.save()
            #messages.success(request, "Match added successfully")
            return redirect("tournament_details", tournament_id=tournament_id)
        else:
            messages.error(request, "Error adding match")
    else:
        form = DuelForm()
    return render(request, "add_duel.html", {"form": form})

@login_required
@admin_required
def close_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if request.method == "POST":
        form = CloseTournamentForm(request.POST)
        if form.is_valid():
            current_champion = form.cleaned_data["champion"]
            tournament.champion = current_champion
            tournament.save()
            messages.success(request, "Champion selected successfully")
            return redirect('tournament_details', tournament_id=tournament.id)
        else:
            messages.error(request, "Error selecting Champion")
    else:
        form = CloseTournamentForm()
    return render(request, "close_tournament.html", {"form": form})
