import requests

url = 'https://maps.googleapis.com/maps/api/elevation/json?locations=39.7391536,-104.9847034&key=AIzaSyAIvugn_R6YSmaVt8zs1I_m38RIo66O4oM'

response = requests.get(url)