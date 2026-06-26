import re
import pandas as pd 
import requests
import folium

# TODO: MAP IMPROVEMENTS
# ✔️ Del taco locations should be labeled with tacos
# > Ability to toggle Del Taco locations off and on 
# > can filter out some del tacos? 
# ✔️ Label the national parks 
# > fix the color coding , and highlight the ones we've been to (and the del tacos!)
# > add national forests back in
# > only show actual national parks
# > change how many del tacos show based on zoom level
# > toggle for national forests 
# > something about distance between points
# > put this on github because it sparks joy

DEL_TACO = "https://locations.deltaco.com/us/"
DEL_TACO_LOGO = "img/deltaco.png"

custom_icon = folium.CustomIcon(
    DEL_TACO_LOGO,
    icon_size=(38, 38),      
    icon_anchor=(19, 19),    
    popup_anchor=(0, -10)    
)

# inspo https://observablehq.com/@erincaughey/national-parks-geojson
NATIONAL_PARKS_URL = "https://gist.githubusercontent.com/erincaughey/2f221501645757e28b715c4063e87595/raw/a90be1b434b1a8cdf71c2abc3373ca63987e2d23/nps-geo-boundary.json"
NATIONAL_FORESTS_URL = "https://gist.githubusercontent.com/erincaughey/2a7521ddd812b1aea2aa0a7e9975a124/raw/47ed240985b73633f7699d7f874d32a694029432/national-forests-geo.json"

VISITED = ['ACAD', 'HALE', 'HAVO', 'GRSM', 'JOTR']

# Coordinates dataset for National Park Visitor Centers
NATIONAL_PARK_VISITOR_CENTERS = {
    "National Park": [
        "Acadia National Park", "Arches National Park", "Badlands National Park", "Big Bend National Park", 
        "Biscayne National Park", "Black Canyon of the Gunnison National Park", "Bryce Canyon National Park", 
        "Canyonlands National Park", "Capitol Reef National Park", "Carlsbad Caverns National Park", 
        "Channel Islands National Park", "Congaree National Park", "Crater Lake National Park", 
        "Cuyahoga Valley National Park", "Death Valley National Park", "Denali National Park", 
        "Dry Tortugas National Park", "Everglades National Park", "Gates of the Arctic National Park", 
        "Gateway Arch National Park", "Glacier National Park", "Glacier Bay National Park", 
        "Grand Canyon National Park", "Grand Teton National Park", "Great Basin National Park", 
        "Great Sand Dunes National Park", "Great Smoky Mountains National Park", "Guadalupe Mountains National Park", 
        "Haleakalā National Park", "Hawaiʻi Volcanoes National Park", "Hot Springs National Park", 
        "Indiana Dunes National Park", "Isle Royale National Park", "Joshua Tree National Park", 
        "Katmai National Park", "Kenai Fjords National Park", "Kings Canyon National Park", 
        "Kobuk Valley National Park", "Lake Clark National Park", "Lassen Volcanic National Park", 
        "Mammoth Cave National Park", "Mesa Verde National Park", "Mount Rainier National Park", 
        "New River Gorge National Park", "North Cascades National Park", "Olympic National Park", 
        "Petrified Forest National Park", "Pinnacles National Park", "Redwood National Park", 
        "Rocky Mountain National Park", "Saguaro National Park", "Sequoia National Park", 
        "Shenandoah National Park", "Theodore Roosevelt National Park", "Virgin Islands National Park", 
        "Voyageurs National Park", "White Sands National Park", "Wind Cave National Park", 
        "Wrangell-St. Elias National Park", "Yellowstone National Park", "Yosemite National Park", 
        "Zion National Park", "American Samoa National Park"
    ],
    "Code": [
        "ACAD", "ARCH", "BADL", "BIBE", "BISC", "BLCA", "BRCA", "CANY", "CARE", "CAVE", 
        "CHIS", "CONG", "CRLA", "CUVA", "DEVA", "DENA", "DRTO", "EVER", "GAAR", "JEVA", 
        "GLAC", "GLBA", "GRCA", "GRTE", "GRBA", "GRSA", "GRSM", "GUMO", "HALE", "HAVO", 
        "HOSP", "INDU", "ISRO", "JOTR", "KATM", "KEFJ", "SEKI", "KOVA", "LACL", "LAVO", 
        "MACA", "MEVE", "MORA", "NERI", "NOCA", "OLYM", "PEFO", "PINN", "REDW", "ROMO", 
        "SAGU", "SEKI", "SHEN", "THRO", "VIIS", "VOYA", "WHSA", "WICA", "WRST", "YELL", 
        "YOSE", "ZION", "NPSA"
    ],
    "Visitor Center": [
        "Hulls Cove Visitor Center", "Arches Visitor Center", "Ben Reifel Visitor Center", "Panther Junction Visitor Center",
        "Dante Fascell Visitor Center", "South Rim Visitor Center", "Bryce Canyon Visitor Center", "Island in the Sky Visitor Center",
        "Capitol Reef Visitor Center", "Carlsbad Caverns Visitor Center", "Robert J. Lagomarsino Visitor Center", "Harry Hampton Visitor Center",
        "Steel Visitor Center", "Boston Mill Visitor Center", "Furnace Creek Visitor Center", "Denali Visitor Center",
        "Garden Key Visitor Center", "Ernest F. Coe Visitor Center", "Bettles Ranger Station", "Gateway Arch Visitor Center",
        "Apgar Visitor Center", "Glacier Bay Visitor Center", "Grand Canyon Visitor Center (South Rim)", "Craig Thomas Discovery and Visitor Center",
        "Lehman Caves Visitor Center", "Great Sand Dunes Visitor Center", "Sugarlands Visitor Center", "Pine Springs Visitor Center",
        "Haleakalā Visitor Center", "Kīlauea Visitor Center", "Fordyce Bathhouse Visitor Center", "Indiana Dunes Visitor Center",
        "Houghton Visitor Center", "Joshua Tree Visitor Center", "King Salmon Visitor Center", "Kenai Fjords National Park Visitor Center",
        "Kings Canyon Visitor Center", "Northwest Arctic Heritage Center", "Lake Clark Visitor Center", "Kohm Yah-mah-nee Visitor Center",
        "Mammoth Cave Visitor Center", "Mesa Verde Visitor Center", "Henry M. Jackson Memorial Visitor Center", "Canyon Rim Visitor Center",
        "North Cascades Visitor Center", "Olympic National Park Visitor Center", "Painted Desert Visitor Center", "Pinnacles Visitor Center (East Side)",
        "Hiouchi Visitor Center", "Beaver Meadows Visitor Center", "Red Hills Visitor Center (West District)", "Foothills Visitor Center",
        "Dickey Ridge Visitor Center", "South Unit Visitor Center", "Cruz Bay Visitor Center", "Rainy Lake Visitor Center",
        "White Sands Visitor Center", "Wind Cave Visitor Center", "Wrangell-St. Elias Visitor Center", "Old Faithful Visitor Education Center",
        "Yosemite Valley Visitor Center", "Zion Canyon Visitor Center", "National Park of American Samoa National Park"
    ],
    "Latitude": [
        44.4093, 38.6164, 43.7495, 29.3275, 25.4651, 38.5562, 37.6403, 38.4735, 38.2891, 32.1753,
        34.2638, 33.8294, 42.8988, 41.2625, 36.4616, 63.7284, 24.6285, 25.3929, 66.9171, 38.6247,
        48.5292, 58.4114, 36.0589, 43.6543, 39.0052, 37.7329, 35.6852, 31.8966, 20.7145, 19.4294,
        34.5134, 41.6333, 47.1239, 34.1339, 58.6888, 60.1171, 36.7397, 66.8978, 60.4853, 40.4325,
        37.1843, 37.3353, 46.7861, 38.0701, 48.6703, 48.0997, 35.0654, 36.4939, 41.7944, 40.3661,
        32.2503, 36.4853, 38.8522, 46.9653, 18.3314, 48.6111, 32.7794, 43.5567, 62.0164, 44.4604,
        37.7487, 37.2003, -14.2583
    ],
    "Longitude": [
        -68.2475, -109.6199, -101.9405, -103.2031, -80.3344, -107.6869, -112.1694, -109.8214, -111.2618, -104.4439,
        -119.2661, -80.8239, -122.1331, -81.5619, -116.8665, -148.8866, -82.8732, -80.5843, -151.5153, -90.1848,
        -113.9822, -135.8856, -112.1092, -110.7183, -114.2245, -105.5122, -83.5361, -104.8282, -156.2514, -155.2571,
        -93.0536, -87.0538, -88.5631, -116.3156, -156.6575, -149.4419, -118.9634, -162.5961, -151.0742, -121.5358,
        -86.1008, -108.4042, -121.7344, -81.0758, -121.2672, -123.4244, -109.7816, -121.1467, -124.0847, -105.5583,
        -111.1664, -118.8358, -78.1911, -103.5272, -64.7936, -93.3444, -106.1719, -103.4781, -145.2736, -110.5873,
        -119.5872, -112.9869, -170.6833
    ]
}


# https://open-meteo.com/en/docs/geocoding-api?name=&countryCode=US&count=20
def get_coordinates(city, state):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=20&countryCode=US&language=en&format=json"

    try:
        response = requests.get(url).json()

        if "results" in response:
            for result in response["results"]:
                # Use .get() to prevent a KeyError if 'admin1' is missing from the JSON
                if result.get('admin1') == state:
                    return [result['latitude'], result['longitude']] 
            
            # Fallback: if exact state isn't matched but results exist, return the first one
            return [response["results"][0]['latitude'], response["results"][0]['longitude']]

    except Exception as e:
        print(f"Error fetching API for {city}, {state}: {e}")

    print(f"wamp wamp: {city}, {state}")
    return [0, 0]


# find all the states with a del taco
def states_del_taco():
    states = []
    
    response = requests.get(DEL_TACO)

    html = response.text

    states = re.findall(fr"us\/(\w\w)\">(\w+(?: \w+)*)", html)

    return(states)

# find all the cities with a del taco
def cities_del_taco():
    states = states_del_taco()

    city_states_del_taco = []

    for abbr, state in states:

        # gets the page with each state's location cities
        # print (f"#####{state} ({abbr})#####")
        # print(DEL_TACO+abbr)
        response = requests.get(DEL_TACO+abbr)
        # print(response.status_code)


        body = response.text

        # parse out city names 
        city_names = re.findall(fr"us\/{abbr}\/\w+(?:-\w+)*'>(\w+(?:\s\w+)*)<", body)

        city_detail = []
        for city in city_names:
            coords = get_coordinates(city, state)
            city_detail.append([city, state, coords[0], coords[1]])

        city_states_del_taco.extend(city_detail)
    
    return(city_states_del_taco)


def forest_styling(feature):
    return {
        'fillColor': 'green',
        'color': 'green',
        'weight': 1,
        'fillOpacity': 0.3
    }
def parks_styling(feature):
    if feature['properties']['UNIT_TYPE'] == "National Park":
        if feature['properties']['UNIT_CODE'] in VISITED:
            return {
            'fillColor': 'purple',
            'color': 'purple',
            'weight': 1,
            'fillOpacity': 0.6
            }
        else: 
            return {
                'fillColor': 'green',
                'color': 'green',
                'weight': 1,
                'fillOpacity': 0.6
                }
    else:
        return {
            'fillColor': 'transparent',
            'color': 'transparent',
            'weight': 0,
            'fillOpacity': 0
        }

if __name__ == "__main__":
    df = pd.DataFrame()
    try:
        df = pd.read_csv("data/cities_del_taco.csv")
    except:
        print("need to fetch del tacos...")
        df = pd.DataFrame(cities_del_taco(), columns=["city", "state", "lat", "long"])
        df.to_csv("cities_del_taco.csv", index=False)
        
    # make the map 
    taco_map = folium.Map(location=[37.0902, -95.7129], zoom_start=4, tiles="cartodb positron")

    # Add Del Tacos 
    for _, row in df.iterrows():
        folium.Marker(
            location=[row['lat'], row['long']],
            popup=f"<b>{row['city']}</b><br>{row['state']}",
            tooltip=row['city'],
            # icon=folium.Icon(color='blue', icon='info-sign')
            icon=custom_icon
        ).add_to(taco_map)



    nps = folium.GeoJson(
        NATIONAL_PARKS_URL, 
        name='Parks',
        style_function=parks_styling
    ).add_to(taco_map)

    # nps = folium.Choropleth(
    #     geo_data=NATIONAL_PARKS,
    #     fill_opacity=.4,
    #     # line_weight=1,
    # ).add_to(taco_map)

    # National Park tooltips
    nps_tooltip = folium.GeoJsonTooltip(
        fields=['UNIT_NAME', 'UNIT_TYPE'],      # Properties to extract from your GeoJSON
        aliases=['', ''],       # Custom display names
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
    ).add_to(nps)   

    # National Forests tooltips
    forest_tooltip = folium.GeoJsonTooltip(
        fields=['FORESTNAME'],      # Properties to extract from your GeoJSON
        aliases=[''],       # Custom display names
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
    )
    folium.GeoJson(
        NATIONAL_FORESTS_URL,
        name='Forests',
        tooltip=forest_tooltip,
        style_function=forest_styling
    ).add_to(taco_map)

    # Add Visitor Centers
    visitor_centers = pd.DataFrame(NATIONAL_PARK_VISITOR_CENTERS)
    for _, row in visitor_centers.iterrows():
        if row['Code'] in VISITED:
            color = 'purple'
        else:
            color = 'green'

        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            tooltip=row['National Park'],
            icon=folium.Icon(color=color, icon_color='white', icon='tree', prefix='fa')
        ).add_to(taco_map)

    taco_map.save("../taco_map.html")




