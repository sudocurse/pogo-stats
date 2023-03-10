import csv
import sys
import urllib.request
from bs4 import BeautifulSoup

def print_info(row):

    # use format widths to line things up
    info_string = f"Name: {row['Name']:>20} "
    # attack = 

    print(info_string)

def get_wiki_page(url):
    # user agent
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = response.read().decode('utf-8')
        return data


def prefetch_cp_table():
    url = "https://bulbapedia.bulbagarden.net/wiki/Power_Up#CP_multiplier"
    data = get_wiki_page(url)
    # get h2#Levels h3.span.text=CP multiplier#<table>
    soup = BeautifulSoup(data, 'html.parser')
    # mw-body
    body = soup.find('div', id='mw-parser-output')
    table = None
    print(body.contents)
    for child in body.descendants:
        print(child.name, child.contents)
        if child.name == 'h2':
            print(child.contents)
            # if child.text == 'Levels':
            #     table = child.find_next_sibling('table')
            #     break


def prefetch_base_stats():
    # for Pokemon Go
    url = "https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_base_stats_(GO)"

def main():
    file = sys.argv[1]
    with open(file, 'r') as f:
        r = csv.DictReader(f)
        print("# info piece")
        print_info(next(r))
        print_info(next(r))
        print_info(next(r))

        print("# wiki debugging")
        prefetch_base_stats()


""" PokeGenie current export columns
'Index,Name,Form,Pokemon Number,Gender,CP,HP,Atk IV,Def IV,Sta IV,IV Avg,Level Min,Level Max,Quick Move,Charge Move,Charge Move 2,Scan Date,Original Scan Date,Catch Date,Weight,Height,Lucky,Shadow/Purified,Favorite,Dust,Rank % (G),Rank # (G),Stat Prod (G),Dust Cost (G),Candy Cost (G),Name (G),Form (G),Sha/Pur (G),Rank % (U),Rank # (U),Stat Prod (U),Dust Cost (U),Candy Cost (U),Name (U),Form (U),Sha/Pur (U),Rank % (L),Rank # (L),Stat Prod (L),Dust Cost (L),Candy Cost (L),Name (L),Form (L),Sha/Pur (L),Marked for PvP use\n'
"""


if __name__ == '__main__':
    main()

