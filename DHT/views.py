import telepot
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from datetime import timedelta
import csv
from .models import Dht11

def home(request):
    return render(request, 'home.html')

@login_required
def table(request):
    data = Dht11.objects.all().order_by('-dt')
    return render(request, 'table.html', {'data': data})

@login_required
def download_csv(request):
    model_values = Dht11.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dht.csv"'
    writer = csv.writer(response)
    writer.writerow(['id', 'temp', 'hum', 'dt'])
    for row in model_values.values_list('id', 'temp', 'hum', 'dt'):
        writer.writerow(row)
    return response

@login_required
def value_view(request):
    derniere_ligne = Dht11.objects.last()
    if derniere_ligne:
        derniere_date = derniere_ligne.dt
        delta_temps = timezone.now() - derniere_date
        difference_minutes = delta_temps.total_seconds() // 60
        if difference_minutes < 60:
            temps_ecoule = f'il y a {int(difference_minutes)} min'
        else:
            heures = int(difference_minutes // 60)
            minutes = int(difference_minutes % 60)
            temps_ecoule = f'il y a {heures}h {minutes}min'
        valeurs = {
            'date': temps_ecoule,
            'id': derniere_ligne.id,
            'temp': derniere_ligne.temp,
            'hum': derniere_ligne.hum
        }
    else:
        valeurs = {
            'date': 'Aucune donnée disponible',
            'id': '-',
            'temp': '-',
            'hum': '-'
        }

    return render(request, 'value.html', {'valeurs': valeurs})

@login_required
def graphiqueTemp(request):
    return render(request, 'ChartTemp.html')

@login_required
def graphiqueHum(request):
    return render(request, 'ChartHum.html')

@login_required
def chart_data(request):
    dht = Dht11.objects.all().order_by('dt')
    data = {
        'temps': [record.dt for record in dht],
        'temperature': [record.temp for record in dht],
        'humidity': [record.hum for record in dht]
    }
    return JsonResponse(data)

@login_required
def chart_data_jour(request):
    now = timezone.now()
    last_24_hours = now - timedelta(hours=24)
    dht = Dht11.objects.filter(dt__range=(last_24_hours, now)).order_by('dt')
    data = {
        'temps': [record.dt for record in dht],
        'temperature': [record.temp for record in dht],
        'humidity': [record.hum for record in dht]
    }
    return JsonResponse(data)

@login_required
def chart_data_semaine(request):
    date_debut_semaine = timezone.now().date() - timedelta(days=7)
    dht = Dht11.objects.filter(dt__gte=date_debut_semaine).order_by('dt')
    data = {
        'temps': [record.dt for record in dht],
        'temperature': [record.temp for record in dht],
        'humidity': [record.hum for record in dht]
    }
    return JsonResponse(data)

@login_required
def chart_data_mois(request):
    date_debut_mois = timezone.now().date() - timedelta(days=30)
    dht = Dht11.objects.filter(dt__gte=date_debut_mois).order_by('dt')
    data = {
        'temps': [record.dt for record in dht],
        'temperature': [record.temp for record in dht],
        'humidity': [record.hum for record in dht]
    }
    return JsonResponse(data)

@login_required
def register_view(request):
    # Si besoin d'une page d'enregistrement, à adapter.
    if request.user.username not in ["admin", "admin2"]:
        return HttpResponseForbidden("Vous n'avez pas la permission d'accéder à cette page.")
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('register_view')
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            user.save()
            messages.success(request, "Utilisateur ajouté avec succès !")
            return redirect('/index')
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
            return redirect('register_view')

    return render(request, 'register.html')
@login_required
def sendtele():
    token = '6662023260:AAG4z48OO9gL8A6szdxg0SOma5hv9gIII1E'
    rece_id = 1242839034
    bot = telepot.Bot(token)
    bot.sendMessage(rece_id, 'La température dépasse la normale.')
    print('Notification envoyée.')

def custom_logout(request):
    logout(request)
    return redirect('/')


#####################################################
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import Dht11, Incident

@login_required
def incident(request):
    # On cherche s’il y a un incident en cours (end_dt is null)
    open_incident = Incident.objects.filter(end_dt__isnull=True).order_by('-start_dt').first()

    # Par défaut, on suppose pas d’incident
    flag_color = 'green'
    message = "Pas d'incidents."
    incident_in_progress = False

    if open_incident:
        flag_color = 'red'
        message = 'Attention, incident détecté.'
        incident_in_progress = True

    # Traitement du formulaire d’acquittement
    # => Seul sens si un incident est en cours
    if request.method == 'POST' and incident_in_progress:
        # Récupérer la remarque
        remarks = request.POST.get('remarks', '')

        # Marquer l’incident comme acquitté
        open_incident.ack = True
        open_incident.remarks = remarks
        open_incident.ack_user = request.user
        open_incident.save()
        messages.success(request, "Incident acquitté avec succès.")

        return redirect('incident')  # Rafraîchir la page ou rediriger ailleurs

    return render(request, 'incident.html', {
        'flag': flag_color,
        'message': message,
        'incident_in_progress': incident_in_progress
    })
####################3333333333333
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Incident

@login_required
def log_incident(request):
    # Récupérer le paramètre de filtrage
    time_filter = request.GET.get('filter', 'all')
    now = timezone.now()

    if time_filter == 'jour':
        start_date = now - timedelta(days=1)
    elif time_filter == 'semaine':
        start_date = now - timedelta(days=7)
    elif time_filter == 'mois':
        start_date = now - timedelta(days=30)
    elif time_filter == 'annee':
        start_date = now - timedelta(days=365)
    else:
        start_date = None

    if start_date:
        incidents = Incident.objects.filter(start_dt__gte=start_date).order_by('-start_dt')
    else:
        incidents = Incident.objects.all().order_by('-start_dt')

    # Déterminer si l'utilisateur peut voir la colonne "Acquittement"
    # On autorise par ex. le superuser ou les membres des groupes Admin / Admin1
    can_see_ack = (
        request.user.is_superuser or
        request.user.groups.filter(name__in=["Admin", "Admin1"]).exists()
    )

    # Déterminer si l'utilisateur peut voir les colonnes "Remarques" et "Utilisateur"
    # On autorise par ex. le superuser ou les membres des groupes Admin / Admin2
    can_see_remarks = (
        request.user.is_superuser or
        request.user.groups.filter(name__in=["Admin", "Admin2"]).exists()
    )

    return render(request, 'log_incident.html', {
        'incidents': incidents,
        'can_see_ack': can_see_ack,
        'can_see_remarks': can_see_remarks,
    })