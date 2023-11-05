from bs4 import BeautifulSoup
import re

with open("data/volunteers.kml") as fp:
    kml_soup = BeautifulSoup(fp, "lxml-xml")

sites = kml_soup.find_all("Placemark")

volunteer_data = {
    "data": []
}

for site in sites:
    site = site.contents
    name = site[1].contents[0]
    volunteer_name, site_name = re.split(":\s{1}", name)
    for coord in site[5].contents[1].stripped_strings:
        lon, lat, _z = re.split(",", coord)

    volunteer_data["data"].append({
        "volunteer_name": volunteer_name,
        "site_name": site_name,
        "lat": lat,
        "lon": lon
    })

with open("data/volunteers.json", "w") as data_file:
    data_file.write(str(volunteer_data))
