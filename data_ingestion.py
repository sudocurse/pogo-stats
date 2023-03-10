import csv
import math
import sys
import urllib.request
from bs4 import BeautifulSoup
from collections import OrderedDict


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


def fetch_cp_table(data):
    """ Data is the html from the wiki page """
    # get h2#Levels h3.span.text=CP multiplier#<table>
    soup = BeautifulSoup(data, 'html.parser')
    # get class mw-parser-output
    body = soup.find('div', class_='mw-parser-output')
    # get h2#Levels
    levels_bro = None
    h2s = body.findAllNext('h2')
    for h in h2s:
        if h.find('span', id='Levels'):
            levels_bro = h
            
    if not levels_bro:
        raise Exception("Could not find h2#Levels")
        return

    # get table
    table = levels_bro.find_next_sibling('table')
    # skip first tr; columns are Levels, CP multiplier, Marginal stardust, marginal candy, Cumulative stardust,
    # cumulative candy
    rows = table.findAll('tr')[2:]
    cp_per_level = OrderedDict()
    # rows[n] is a tr containing td elements
    for row in rows:
        tds = row.findAll('td')
        # tds[0] is the level
        # tds[1] is the CP multiplier
        # tds[2] is the marginal stardust to next
        # tds[3] is the marginal candy
        # tds[4] is the cumulative stardust to next
        # tds[5] is the cumulative candy
        level = float(tds[0].text)
        if level == 50:
            cum_dust = 'n/a'
            cum_candy = 'n/a'
            marg_dust = 'n/a'
            marg_candy = 'n/a'
        elif level > 50:
            break
        else:
            cum_dust = int(tds[4].contents[1])
            marg_dust = int(tds[2].contents[1])
            marg_candy = int(tds[3].contents[1])
            cum_candy = int(tds[5].contents[1])
        cp_per_level[level] = {
            'cpm': float(tds[1].text),
            'marg_dust': marg_dust,
            'cum_dust': cum_dust,
            'marg_candy': marg_candy,
            'cum_candy': cum_candy
        }

    return cp_per_level


def prefetch_base_stats():
    # for Pokemon Go
    url = "https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_base_stats_(GO)"

def main():
    # file = sys.argv[1]
    # with open(file, 'r') as f:
        # r = csv.DictReader(f)
        # print("# info piece")
        # print_info(next(r))
        # print_info(next(r))
        # print_info(next(r))
    # url = "https://bulbapedia.bulbagarden.net/wiki/Power_Up#CP_multiplier"
    # data = get_wiki_page(url)

    with open('Power Up - Bulbapedia, the community-driven Pokémon encyclopedia.html') as f:
        data = f.read()
        # load CPMs
        cp_table = fetch_cp_table(data)
        
    # assume we got base stats
    # get pokemon and IVs
    # pkmn = get_capture(d) for d in data
    # stats = get_base_stats(pkmn.name)
    
    mons = []
    base_stats = {}
    with open('pkmn.txt') as f:
        for line in f:
            # looking for ^Aron.*, ^Lairon.*, ^Aggron.*
            if line.startswith('Aron') or line.startswith('Lairon') or line.startswith('Aggron'):
                # headers for lines in question are
                # Pokemon, Best Atk IV, Best Def IV, Best Sta IV, Base Atk, Base Def, Base HP, Level, CP multiplier for
                # level, CPM, cp
                d = [x.strip() for x in line.split(',')]
                try:
                    mon, iv_atk, iv_def, iv_sta, base_atk, base_def, base_hp, _, _, scanned_cp = d
                except ValueError:
                    mon, iv_atk, iv_def, iv_sta, base_atk, base_def, base_hp, _, _ = d
                    scanned_cp = False
                if mon not in base_stats:
                    base_stats[mon] = {
                        'atk': int(base_atk),
                        'def': int(base_def),
                        'hp': int(base_hp)
                    }
                    print(f"🧑‍🏫 {mon} base stat lookup: {base_atk}/{base_def}/{base_hp}")

    combos = {}
    for mon in base_stats:
        combos[mon] = {}
        print(f"{mon}: {base_stats[mon]}")
        for a in range(0, 16):
            for d in range(0, 16):
                for s in range(0, 16):
                    for level in cp_table:
                        cpm = cp_table[level]['cpm']
                        computed_atk = (base_stats[mon]['atk'] + a) * cpm
                        computed_def = (base_stats[mon]['def'] + d) * cpm
                        computed_sta = (base_stats[mon]['hp'] + s) * cpm
                        computed_atk, computed_def, computed_sta = math.floor(computed_atk), math.floor(computed_def), math.floor(computed_sta)
                        cp = math.floor(computed_atk * math.sqrt(computed_def) * math.sqrt(computed_sta) / 10)
                        combos[mon][f'{a}/{d}/{s}'] = {
                            'computed_atk': computed_atk,
                            'computed_def': computed_def,
                            'computed_hp': computed_sta,
                            'cp': cp
                        }

    for mon in combos:
        aaa = "none < 1500 for {}".format(mon)
        for ivs in combos[mon]:
            if combos[mon][ivs]['cp'] <= 1500:
                aaa = f"{mon} {ivs} {combos[mon][ivs]}"
        print(aaa)

    def computed_values(mon, lookup):
        d = combos[mon]
        return "{}/{}/{} CP:{}".format(d[lookup]['computed_atk'], d[lookup]['computed_def'], d[lookup]['computed_hp'], d[lookup]['cp'])
    for mon in combos:
        # find combos[mon][n] with the highest computed_atk
        top_atk = max(combos[mon], key=lambda x: combos[mon][x]['computed_atk'])
        top_def = max(combos[mon], key=lambda x: combos[mon][x]['computed_def'])
        top_sta = max(combos[mon], key=lambda x: combos[mon][x]['computed_hp'])
        top_cp = max(combos[mon], key=lambda x: combos[mon][x]['cp'])
        print(f"{mon}:")
        batk = computed_values(mon, top_atk)
        print(f"  Best Atk: {batk} ({top_atk})")
        bdef = computed_values(mon, top_def)
        print(f"  Best Def: {bdef} ({top_def})")
        bsta = computed_values(mon, top_sta)
        print(f"  Best Sta: {bsta} ({top_sta})")
        bcp = computed_values(mon, top_cp)
        print(f"  Best CP: {bcp} ({top_cp})")
        lows = '0/0/0'
        print(f"  All 0s: {computed_values(mon, lows)} ({lows})")
        mid_atk_only = '8/0/0'
        print(f"  Mid Atk: {computed_values(mon, mid_atk_only)} ({mid_atk_only})")
        high_atk_only = '15/0/0'
        print(f"  High Atk: {computed_values(mon, high_atk_only)} ({high_atk_only})")
        mid_def_only = '0/8/0'
        print(f"  Mid Def: {computed_values(mon, mid_def_only)} ({mid_def_only})")
        high_def_only = '0/15/0'
        print(f"  High Def: {computed_values(mon, high_def_only)} ({high_def_only})")
        mid_sta_only = '0/0/8'
        print(f"  Mid Sta: {computed_values(mon, mid_sta_only)} ({mid_sta_only})")
        high_sta_only = '0/0/15'
        print(f"  High Sta: {computed_values(mon, high_sta_only)} ({high_sta_only})")
        low_atk_highs = '0/15/15'
        print(f"  Low Atk Highs: {computed_values(mon, low_atk_highs)} ({low_atk_highs})")
        mid_atk_highs = '8/15/15'
        print(f"  Mid Atk Highs: {computed_values(mon, mid_atk_highs)} ({mid_atk_highs})")
        all_highs = '15/15/15'
        print(f"  All Highs: {computed_values(mon, all_highs)} ({all_highs})")
        print()



if __name__ == '__main__':
    main()

