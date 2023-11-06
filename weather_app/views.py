from django.shortcuts import render, redirect
from decouple import config
import requests
import datetime

def index(request):
    if request.method == 'POST':
        city1 = request.POST['city1']
        city2 = request.POST['city2']

        api_key = config("API_KEY")
        current_weather_url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}"
        forecast_url = "https://api.openweathermap.org/data/2.5/forecast?q={}&appid={}"

        weather_data1, daily_forecasts1 = None, None
        weather_data2, daily_forecasts2 = None, None

        if city1:
            weather_data1, daily_forecasts1 = fetch_weather_and_forecast(city1, api_key, current_weather_url, forecast_url)

        if city2:
            weather_data2, daily_forecasts2 = fetch_weather_and_forecast(city2, api_key, current_weather_url, forecast_url)

        context = {
            'weather_data1': weather_data1,
            'daily_forecasts1': daily_forecasts1,
            'weather_data2': weather_data2,
            'daily_forecasts2': daily_forecasts2,
        }

            # store the context in the session
        request.session['context'] = context

            # redirect to the same view using GET method
        return redirect('index')

        # get the context from the session
        context = request.session.get('context', {})

        # clear the session
        request.session.clear()

        return render(request, 'index.html', context)


    return render(request, 'index.html')

def fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_url):
    response = requests.get(current_weather_url.format(city, api_key)).json()

    if response.get('cod') == 200:
        forecast_response = requests.get(forecast_url.format(city, api_key)).json()

        weather_data = {
            'city': city,
            'temperature': round(response['main']['temp'] - 273.15),
            'description': response['weather'][0]['description'],
            'icon': response['weather'][0]['icon'],
        }

        daily_forecasts = []

        for daily_data in forecast_response.get('list', []):
            if 'dt_txt' in daily_data and daily_data['dt_txt'].endswith('12:00:00'):
                day = 'N/A'
                min_temp = 'N/A'
                max_temp = 'N/A'
                description = 'N/A'
                icon = 'N/A'

                try:
                    if 'dt' in daily_data:
                        day = datetime.datetime.fromtimestamp(daily_data['dt']).strftime('%A')
                    if 'main' in daily_data and 'temp_min' in daily_data['main']:
                        min_temp = round(daily_data['main']['temp_min'] - 273.15)
                    if 'main' in daily_data and 'temp_max' in daily_data['main']:
                        max_temp = round(daily_data['main']['temp_max'] - 273.15)
                    if 'weather' in daily_data and daily_data['weather']:
                        description = daily_data['weather'][0].get('description', 'N/A')
                        icon = daily_data['weather'][0].get('icon', 'N/A')
                        
                except Exception as e:
                    print(f"An error occurred: {str(e)}")

                daily_forecasts.append({
                    'day': day,
                    'min_temp': min_temp,
                    'max_temp': max_temp,
                    'description': description,
                    'icon': icon,
                })

        return weather_data, daily_forecasts

    return None, None
