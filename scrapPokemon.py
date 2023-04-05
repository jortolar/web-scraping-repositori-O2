import requests
import re
from bs4 import BeautifulSoup

poke_domain = "https://www.pokemon.com"
url = "https://www.pokemon.com/es/pokedex/"
img_url = "https://assets.pokemon.com/assets/cms2/img/pokedex/full/{}.png"

# 1. Get the HTML Source File.

r = requests.get(url)
soup = BeautifulSoup(r.content, 'html.parser')

# 2. Extract the data and append it to a list.
pokedex = []

for sec in soup.find_all('li'):
    for link in sec.find_all('a'):
        if 'href' in link.attrs.keys():
            if re.search(r'/pokedex/(.+)', link['href']):
                pokemon = link.text
                pokemon = pokemon.split(' - ')
                pokemon = [x.strip() for x in pokemon]
                pokedex.append({
                    'number': pokemon[0],
                    'name': pokemon[1].lower(),
                    'ref': link['href']
                })


 # 3. Get the HTML file from each pokemon.
aug_pokedex = []
for row in pokedex:
    
    poke_url = poke_domain + row['ref']
    
    print("poke_url: ", poke_url)

    r = requests.get(poke_url)
    soup = BeautifulSoup(r.content, 'html.parser')


    for section in soup.find_all('div', class_="pokemon-stats-info active"):
        for attribute in section.find_all('li'):
            if (attribute["class"] == ['meter']):
                print(attribute['data-value'])
                print(attribute.text)  


    exit()

    # 2. Extract attributes.
    type_list = []
    weakness_list = []

    for section in soup.find_all('div', class_="pokedex-pokemon-attributes active"):
        for link in section.find_all('a'):
            if re.search(r'/pokedex/\?type=', link['href']):
                type_list.append(link.text)

            if re.search(r'/pokedex/\?weakness=', link['href']):
                weakness_list.append(link.text.strip())

    attr = ''
    val = ''
    for section in soup.find_all('div', class_="pokemon-ability-info color-bg color-lightblue match active"):
        for attribute in section.find_all('span'):
            
            if (attribute["class"] == ['attribute-title']):
                attr = attribute.text
            elif (attribute["class"] == ['attribute-value']):
                val = attribute.text

            if (attr != '' and val != ''):              
                match attr:
                    case "Categoría":
                        categoria = val
                    case "Altura":
                        altura = val
                    case "Peso":
                        peso = val
                    case "Habilidad":
                        habilidad = val        
                attr = ''
                val = ''

    old_img_name = "{0:0=3d}".format(int(row['number']))
    from_url = img_url.format(old_img_name)

    aug_pokedex.append({
        'name': row['name'],
        'number': row['number'],
        'ref': row['ref'],
        'type': type_list,
        'weakness': weakness_list,
        'categoria':categoria,
        'altura':altura,
        'peso':peso,
        'habilidad':habilidad,
        'image_url': from_url
       
    })

    print (list(aug_pokedex))



exit()
aug_pokedex = pd.DataFrame(aug_pokedex)




exit()

# 3. Generate a dataframe.
pokedex = pd.DataFrame(pokedex)[['number', 'name', 'ref']].copy()

# 4. Download the file as csv.
pokedex.to_csv(self.csv_file, index=False)

