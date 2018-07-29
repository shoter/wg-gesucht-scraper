import urllib.request
from bs4 import BeautifulSoup as soup
import re
import collections

class Empty(object):
    pass

def __namedtuple_with_defaults__(typename, field_names, default_values=()):
    T = collections.namedtuple(typename, field_names)
    T.__new__.__defaults__ = (None,) * len(T._fields)
    if isinstance(default_values, collections.Mapping):
        prototype = T(**default_values)
    else:
        prototype = T(*default_values)
    T.__new__.__defaults__ = tuple(prototype)
    return T

Settings = __namedtuple_with_defaults__("Settings", 
"minArea maxPrice cityId categoryId rentId",
[0, 99999, 8, 1, 2])

def __normalizeText__(text):
    text = text.strip()
    text = re.sub(" +", " ", text)
    text = re.sub("\n", "", text)
    return text

def getLinks(pageNumber, settings):
    opener = urllib.request.FancyURLopener({})
    url = ("https://www.wg-gesucht.de/en/1-zimmer-wohnungen-in-Berlin.8.1.1." + str(pageNumber)
    + ".html?offer_filter=1&noDeact=1&" 
    + "city_id=" + str(settings.cityId) 
    + "&category=" + str(settings.categoryId)
    + "&rent_type=" + str(settings.rentId) 
    + "&sMin=" + str(settings.minArea) 
    + "&rMax" + str(settings.maxPrice))

    f = opener.open(url)
    content = f.read()

    ss = soup(content, 'html.parser')

    links = ss.find_all("a", "detailansicht")
    base = "https://www.wg-gesucht.de/en/"
    result = []
    for link in links:
        href = link["href"]
        fullUrl = base + href
        if fullUrl not in result and not href.startswith("//airbnb") and not href.startswith("http"):
            result.append(fullUrl)

    return result

# Return properties:
# title : string
# price : int
# area : int
# availability : string
# details : string[]
def getOfferInformation(url): 
    global ss
    opener = urllib.request.FancyURLopener({})
    f = opener.open(url)
    content = f.read()

    ss = soup(content, 'html.parser')

    divs = ss.find_all("div", "col-xs-6 col-sm-4 text-center print_text_left")
    result = Empty()
    result.details = []
    for div in divs:
        
        result.details.append(__normalizeText__(div.get_text()))

    headlines = ss.find_all("h2", "headline-key-facts")

    first = True
    for headline in headlines:
        num = int(re.findall(r'\d+', headline.get_text().strip())[0])
        if first:
            first = False
            result.area = num
        else:
            result.price = num
    
    links = ss.find_all("a")
    for link in links:
        if link.has_attr("onclick") and link["onclick"].find("map_tab") != -1:
            result.location = __normalizeText__(link.get_text())

    divs = ss.find_all("div", "col-sm-3")
    for div in divs:
        if div.get_text().find("Availability") != -1:
            bs = div.find("p").find_all("b")
            result.availability = __normalizeText__(bs[0].get_text())


    result.title = __normalizeText__(
        ss.find_all("h1")[0].get_text()
    )

    return result

def getOfferInformationsFromPage(pageNumber=0, settings=Settings()):
    result = []
    links = getLinks(pageNumber, settings)

    for link in links:
        result.append(getOfferInformation(link))
    return result


def printInfo(result):
    print(result.title)
    print("Price: " + str(result.price) + " Euro")
    print("Area: " + str(result.area) + " sqm")
    print("Availability: " + result.availability)
    print("Details: ")
    for detail in result.details:
        print(detail)

results = getOfferInformationsFromPage(0, 
Settings(40, 600))

for result in results:
    printInfo(result)


#test = getOfferInformation("https://www.wg-gesucht.de/en/1-zimmer-wohnungen-in-Berlin-Moabit.6379439.html")