import requests
from bs4 import BeautifulSoup

#returns deals, exits, and links, and date in a dictionary
def scrape_data(url):
    scraping_data = {'deals':[],'exits':[],'links':[],'date':""}

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    #print out the date at the top
    scraping_data['date'] += soup.find("time", class_="mt-1 sm:mt-0").text#["datetime"]
    data = soup.find("h2", string=lambda text: "Deals of the Week" in text)
    next_sibling = data.next_sibling
    other_fundings = False

    while next_sibling is not None:
        data = next_sibling

        #skips over any elements with id that is not p, h2, or h3
        if (data.name in ["p", "h2", "h3"]):
            #stop at exits and new funds for now
            if ("Exits" in data.text) or ("New Funds" in data.text): 
                break

            #print out each deal and its link
            if ("p" in data.name): 
                link = data.find("a")

                #only print out debt financing deals if it is before other fundings
                if ("debt" not in data.text) or (other_fundings == False):
                    if link is not None: scraping_data['links'].append(link["href"])
                    else: scraping_data['links'].append(None)
                    scraping_data['deals'].append(data.text)
            if ("Other Fundings" in data.text): other_fundings = True

        next_sibling = next_sibling.next_sibling

    #get exits
    data = soup.find("h3", string=lambda text: "Exits" in text)
    #check if there are exits
    if data is None: return scraping_data

    next_sibling = data.next_sibling
    new_fund_terms = ['launched','raised','held']
    new_fund = False


    while (next_sibling != None) and (next_sibling.name == "p"):
        data = next_sibling
        for term in new_fund_terms:
            if term in data.text:
                new_fund = True 
        if new_fund == True:
            break
        scraping_data['exits'].append(data.text)
        #add exit links to the same list as deals
        link = data.find("a")
        scraping_data['links'].append(link["href"]) if link is not None else scraping_data['links'].append(None)
        next_sibling = next_sibling.next_sibling
    
    return scraping_data