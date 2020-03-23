from googlemaps import Client as GoogleMaps



class Coordinates:
    lat = ""
    long = ""

def get_coodinates(country,city):
    gmaps = GoogleMaps('')
    try:
        geocode_result = gmaps.geocode(city +","+country)
        coordinates = Coordinates()
        coordinates.lat = geocode_result[0]['geometry']['location']['lat']
        coordinates.long = geocode_result[0]['geometry']['location']['lng']
        return coordinates
    except:
        return 0

