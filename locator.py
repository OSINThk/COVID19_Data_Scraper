from googlemaps import Client as GoogleMaps



class Coordinates:
    lat = ""
    long = ""

def get_coodinates(country):
    gmaps = GoogleMaps('AIzaSyCyVhylbOfEtkqyA5GL3le-BOZ3H24rPUs')
    try:
        geocode_result = gmaps.geocode(country)
        coordinates = Coordinates()
        coordinates.lat = geocode_result[0]['geometry']['location']['lat']
        coordinates.long = geocode_result[0]['geometry']['location']['lng']
        return coordinates
    except:
        return 0

