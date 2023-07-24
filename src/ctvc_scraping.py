import re
import requests
from bs4 import BeautifulSoup

#returns deals, exits, and links, and date in a dictionary
def scrape_data(url):
    scraping_data = {'deals':[],'exits':[],'links':[],'date':""}
    try:
        page = requests.get(url)
    except:
        return None
    soup = BeautifulSoup(page.content, 'html.parser')

    #print out the date at the top
    try:
        date = soup.find("time", class_="mt-1 sm:mt-0").text
    except:
        date = 'no date found'
    scraping_data['date'] += date
    #data = soup.find("h2", string=re.compile("deals of the week",re.IGNORECASE)) #soup.find("h2", string=lambda text: "Deals of the Week" in text)
    h2_tags = soup.find_all('h2')
    for tag in h2_tags:
        if re.search("deals of the week", tag.text, re.IGNORECASE):
            data = tag
            break

    h2_tags = soup.find_all('h2')
    for tag in h2_tags:
        if re.search("deals of the week", tag.text, re.IGNORECASE):
            data = tag
            break
    #check if data is an assigned variable 
    if 'data' not in locals():
        return None
    next_sibling = data.next_sibling
    other_fundings = False


    def add_links(block):
        #number of distinct paragraphs in the block
        num_paragraphs = int(len(block.find_all('br')) / 2 + 1)
        urls = block.find_all('a')

        if num_paragraphs == 1:
            if len(urls) != 0:
                scraping_data['links'].append(urls[0].get('href'))
            else:
                scraping_data['links'].append(None)
            return

        #avoid unequal number of links and paragraphs
        if len(urls) != num_paragraphs:
            print()
            print(f"NUM PARAGRAPHS: {num_paragraphs}")
            print()
            for i in range(num_paragraphs):
                scraping_data['links'].append(None)
        
        for url in urls:
            scraping_data['links'].append(url.get('href'))

    while next_sibling is not None:
        data = next_sibling

        #stop at dividor
        if (data.name == "hr"):
            break
        
        if ("Exits" in data.text) or ("New Funds" in data.text): 
            break

        #print out each deal and its link
        if ("p" in data.name): 

            #only print out debt financing deals if it is before other fundings
            if ("debt" not in data.text) or (other_fundings == False):
                # link = data.find("a")
                # if link is not None: scraping_data['links'].append(link.get('href'))
                # else: scraping_data['links'].append(None)
                add_links(data)
                scraping_data['deals'].append(data.text)
        if ("Other Fundings" in data.text): other_fundings = True

        next_sibling = next_sibling.next_sibling

    #get exits
    #data = soup.find("h3", string=lambda text: "Exits" in text)
    h3_tags = soup.find_all('h3')
    for tag in h2_tags:
        if re.search("exits", tag.text, re.IGNORECASE):
            data = tag
            break

    #check if there are exits
    if data == None: 
        return scraping_data

    next_sibling = data.next_sibling
    new_fund_terms = ['launched','raised','held']
    new_fund = False


    while (next_sibling != None) and (next_sibling.name == "p"):
        data = next_sibling

        #stop at dividor
        if (data.name == "hr"):
            break

        for term in new_fund_terms:
            if term in data.text:
                new_fund = True 
        if new_fund == True:
            break
        scraping_data['exits'].append(data.text)
        #add exit links to the same list as deals
        # link = data.find("a")
        # scraping_data['links'].append(link.get('href')) if link is not None else scraping_data['links'].append(None)
        add_links(data)
        next_sibling = next_sibling.next_sibling
    
    return scraping_data