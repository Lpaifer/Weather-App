from django.shortcuts import render
from django.core.cache import cache
import httpx

API_KEY = '54e719358f71910be672001072a0806b'

async def weather_view(request):
    city = request.GET.get("city", "Sorocaba")
    cache_key = f"weather_{city.lower()}"
    
    # Check if the data is already cached
    cached_data = cache.get(cache_key)
    if cached_data:
        return render(request, 'weather/index.html', {
            'weather_data': cached_data,
            'input': city
        })    

    # If not cached, fetch the data from the API
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=pt"

    # Initialize weather_data and error_message
    weather_data = {}
    error_message = None
    limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)

    try:
        async with httpx.AsyncClient(limits=limits) as client:
            response = await client.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                weather_data = {
                    'city': data['name'],
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed'],
                }

                # Cache the data for 10 minutes
                cache.set(cache_key, weather_data, timeout=600)

            else:
                error_message = f"Cidade '{city}' não encontrada."
    except Exception as e:
        error_message = str(e)

    return render(request, 'weather/index.html', {
        'weather_data': weather_data,
        'error_message': error_message,
        'input': city
    })


