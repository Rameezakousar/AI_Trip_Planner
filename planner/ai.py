import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_trip(destination, start_date, end_date, budget, travelers, hotel, transport):

    prompt = f"""
You are an expert travel planner.

Create a professional travel itinerary.

Destination: {destination}
Start Date: {start_date}
End Date: {end_date}
Budget: ₹{budget}
Travelers: {travelers}
Hotel: {hotel}
Transport: {transport}

Rules:
- No introduction.
- No paragraphs.
- Use headings.
- Use bullet points.
- Create day-wise itinerary.
- Mention food.
- Mention attractions.
- Mention travel tips.
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text

    except Exception:

        return f"""
🌍 TRIP SUMMARY

Destination : {destination}

Dates : {start_date} to {end_date}

Travelers : {travelers}

Budget : ₹{budget}

Hotel : {hotel}

Transport : {transport}

---------------------------------------

DAY 1

🌅 Morning
• Check into hotel
• Visit famous attractions

🍽 Afternoon
• Enjoy local lunch

🌇 Evening
• Shopping
• Sunset point

---------------------------------------

DAY 2

🌅 Morning
• Visit museums

🍽 Afternoon
• Local sightseeing

🌇 Evening
• Street food

---------------------------------------

🍴 Must Try Foods

• Local Special Dish
• Famous Dessert
• Fresh Juice

---------------------------------------

⭐ Top Attractions

• Attraction 1
• Attraction 2
• Attraction 3

---------------------------------------

🎒 Travel Tips

✔ Carry water
✔ Start early
✔ Keep cash

---------------------------------------

💰 Estimated Budget

Hotel : ₹10000
Food : ₹5000
Transport : ₹4000
Activities : ₹3000

🎉 Have a wonderful trip!
"""