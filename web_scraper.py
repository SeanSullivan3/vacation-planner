import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass

baseurl = 'https://travel.usnews.com'
header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}


def get_city_url(chosen_city) -> str:
    destinations_page = requests.get(baseurl + '/destinations/', headers=header)
    soup = BeautifulSoup(destinations_page.text, "html.parser")
    try:
        city_href = soup.find("a", string=chosen_city).get("href")
        return baseurl + city_href
    except AttributeError:
        return "not a listed city"


def get_list_of_cities() -> [str]:
    destinations_page = requests.get(baseurl + '/destinations/', headers=header)
    soup = BeautifulSoup(destinations_page.text, "html.parser")
    cities = []
    for city in soup.find_all("li", class_="List__ListItem-rhf5no-1 jYdEtR"):
        cities.append(str(city.string))
    return cities


@dataclass
class ThingToDo:
    name: str
    address: str
    type: [str]
    time_to_spend: str
    image: str
    description: str

    def print(self):
        print(self.name)
        print(self.address)
        print(self.type)
        print(self.time_to_spend)
        print(self.image)
        print(self.description)


def find_things_to_do(city) -> [ThingToDo]:
    city_url = get_city_url(city)
    if city_url == "not a listed city":
        return [ThingToDo("not a listed city", "", [], "", "", "")]
    city_thing_to_do_page = requests.get(city_url + 'Things_To_Do/', headers=header)
    soup = BeautifulSoup(city_thing_to_do_page.text, "html.parser")
    things_to_do = []
    for thing in soup.find_all("li", class_="GenericList__ListItemContainer-tjuxmv-1 exYsXw"):
        name = thing.find("div", class_="Raw-slyvem-0 cUEqig").string
        try:
            address = thing.find("span",
                                 class_="Span-sc-19wk4id-0 DetailCardTour__StyledAddress-sc-1f2q998-9 lCyXL lgJjwM").string
        except AttributeError:
            address = "Not listed"
        try:
            type = (thing.find("div",
                               class_="DetailCardTour__TourAttributes-sc-1f2q998-18 PiElq md-mb3 lg-mb3 Hide-kg09cx-0 hWOBmI")
                    .find("div", class_="DetailCardTour__AttributeText-sc-1f2q998-19 dvRdkw t-font-fam mr3").string)
            types = type.split(", ")
        except AttributeError:
            types = []
        try:
            time_to_spend = (thing.find("div", class_="DetailCardTour__TourAttributes-sc-1f2q998-18 PiElq")
                             .find("div",
                                   class_="DetailCardTour__AttributeText-sc-1f2q998-19 dvRdkw t-font-fam mr3").string)
        except AttributeError:
            time_to_spend = ""
        try:
            image = str(thing.find("img").get("src"))
            image = image[image.find("url=") + len("url="):len(image)].replace("%2F", "/").replace("%3A", ":")
        except AttributeError:
            image = ""
        try:
            description = ""
            for desc in thing.find("div", class_="Raw-slyvem-0 iccyqK").find_all("p"):
                for string in desc.strings:
                    if str(string).find("Tip:") != -1:
                        break
                    if str(string)[len(string) - 1] == ".":
                        string += " "
                    description += string
        except AttributeError:
            description = ""
        things_to_do.append(ThingToDo(name, address, types, time_to_spend, image, description))
    return things_to_do
