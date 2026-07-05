from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.db.models import Sum, Count
from .ai import generate_trip
from .models import Trip
import requests
WEATHER_API_KEY = "e3e847953fa43f409ca0cc2643f8a94c"
def home(request):
    return render(request, "planner/home.html")


def login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            auth_login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "planner/login.html")


def register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register")

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")

    return render(request, "planner/register.html")
@login_required
def dashboard(request):

    search = request.GET.get("search")

    trips = Trip.objects.filter(user=request.user)

    if search:
        trips = trips.filter(destination__icontains=search)

    trips = trips.order_by("-created_at")

    trip_count = trips.count()

    total_budget = (
        trips.aggregate(total=Sum("budget"))["total"] or 0
    )

    favorite = (
        Trip.objects.filter(user=request.user)
        .values("destination")
        .annotate(total=Count("destination"))
        .order_by("-total")
        .first()
    )

    favorite_destination = (
        favorite["destination"] if favorite else "No Trips"
    )

    return render(
        request,
        "planner/dashboard.html",
        {
            "trips": trips,
            "search": search,
            "trip_count": trip_count,
            "total_budget": total_budget,
            "favorite_destination": favorite_destination,
        }
    )
@login_required
def plan_trip(request):

    if request.method == "POST":

        destination = request.POST.get("destination")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        budget = request.POST.get("budget")
        travelers = request.POST.get("travelers")
        hotel = request.POST.get("hotel")
        transport = request.POST.get("transport")

        try:

            trip = generate_trip(
                destination,
                start_date,
                end_date,
                budget,
                travelers,
                hotel,
                transport
            )

            image = f"https://picsum.photos/800/400?random={destination.lower()}"

            Trip.objects.create(
                user=request.user,
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                budget=budget,
                travelers=travelers,
                hotel=hotel,
                transport=transport,
                itinerary=trip,
                image_url=image
            )

            return render(
                request,
                "planner/result.html",
                {
                    "trip": trip
                }
            )

        except Exception as e:

            print("Gemini Error:", e)

            messages.error(
                request,
                "Gemini AI is temporarily unavailable or your API quota has been exceeded. Please try again later."
            )

            return redirect("plan_trip")

    return render(request, "planner/plan_trip.html")
@login_required
def trip_detail(request, trip_id):

    trip = get_object_or_404(
        Trip,
        id=trip_id,
        user=request.user
    )

    weather = {}

    try:

        url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"q={trip.destination}"
            f"&appid={WEATHER_API_KEY}"
            f"&units=metric"
        )

        response = requests.get(url)

        data = response.json()
        print("URL:", url)
        print("Weather Response:", data)

        if response.status_code == 200:

            weather = {
                "temp": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"].title(),
                "city": data["name"],
            }

    except Exception as e:

        print("Weather Error:", e)
    packing_list = [
    "Clothes",
    "Mobile Charger",
    "Power Bank",
    "Water Bottle",
    "Medicines",
    "ID Proof",
    
]


    return render(
        request,
        "planner/trip_detail.html",
        {
            "trip": trip,
            "weather": weather,
            "packing_list": packing_list,
        }
    )            
        


@login_required
def delete_trip(request, trip_id):

    trip = get_object_or_404(
        Trip,
        id=trip_id,
        user=request.user
    )

    trip.delete()

    messages.success(request, "Trip deleted successfully!")

    return redirect("dashboard")
@login_required
def toggle_favorite(request, trip_id):

    trip = get_object_or_404(
        Trip,
        id=trip_id,
        user=request.user
    )

    trip.favorite = not trip.favorite
    trip.save()

    return redirect("dashboard")

@login_required
def download_pdf(request, trip_id):

    trip = get_object_or_404(
        Trip,
        id=trip_id,
        user=request.user
    )

    response = HttpResponse(content_type='application/pdf')
    response["Content-Disposition"] = (
        f'attachment; filename="{trip.destination}_itinerary.pdf"'
    )

    pdf = canvas.Canvas(response)

    y = 800

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "AI Trip Planner")
    y -= 40

    pdf.setFont("Helvetica", 12)

    pdf.drawString(50, y, f"Destination: {trip.destination}")
    y -= 20

    pdf.drawString(50, y, f"Start Date: {trip.start_date}")
    y -= 20

    pdf.drawString(50, y, f"End Date: {trip.end_date}")
    y -= 20

    pdf.drawString(50, y, f"Budget: ₹{trip.budget}")
    y -= 20

    pdf.drawString(50, y, f"Travelers: {trip.travelers}")
    y -= 20

    pdf.drawString(50, y, f"Hotel: {trip.hotel}")
    y -= 20

    pdf.drawString(50, y, f"Transport: {trip.transport}")
    y -= 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "AI Itinerary")
    y -= 25

    pdf.setFont("Helvetica", 10)

    for line in trip.itinerary.split("\n"):

        pdf.drawString(50, y, line[:100])
        y -= 15

        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y = 800

    pdf.save()

    return response


def logout_view(request):

    logout(request)

    return redirect("home")

@login_required
def edit_trip(request, trip_id):

    trip = get_object_or_404(
        Trip,
        id=trip_id,
        user=request.user
    )

    if request.method == "POST":
        trip.budget = request.POST.get("budget")
        trip.hotel = request.POST.get("hotel")
        trip.transport = request.POST.get("transport")
        trip.travelers = request.POST.get("travelers")
        trip.save()

        messages.success(request, "Trip updated successfully!")
        return redirect("dashboard")

    return render(
        request,
        "planner/edit_trip.html",
        {
            "trip": trip
        }
    )
@login_required
def profile(request):

    trip_count = Trip.objects.filter(user=request.user).count()

    total_budget = sum(
        Trip.objects.filter(user=request.user)
        .values_list("budget", flat=True)
    )

    return render(
        request,
        "planner/profile.html",
        {
            "trip_count": trip_count,
            "total_budget": total_budget,
        }
    )

