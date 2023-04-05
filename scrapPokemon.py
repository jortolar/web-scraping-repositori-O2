import requests
import re
from bs4 import BeautifulSoup

poke_domain = "https://www.pokemon.com"
url = "https://www.pokemon.com/es/pokedex/"
img_url = "https://assets.pokemon.com/assets/cms2/img/pokedex/full/{}.png"

# 1. Obtener el fichero HTML de la Pokédex

r = requests.get(url)
soup = BeautifulSoup(r.content, 'html.parser')


pokedex = []

# 2. Obtener todos los pokemons con su id, su nombre y la URL de sus características 
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



aug_pokedex = []

# 3. obtener el fichero HTML de cada pokemon y extraer las características de cada uno
for row in pokedex:
    
    poke_url = poke_domain + row['ref']
    
    print("poke_url: ", poke_url)

    r = requests.get(poke_url)
    soup = BeautifulSoup(r.content, 'html.parser')

    type_list = []
    weakness_list = []

    # tipo y debilidad
    for section in soup.find_all('div', class_="pokedex-pokemon-attributes active"):
        for link in section.find_all('a'):
            if re.search(r'/pokedex/\?type=', link['href']):
                type_list.append(link.text)

            if re.search(r'/pokedex/\?weakness=', link['href']):
                weakness_list.append(link.text.strip())

    attr = ''
    val = ''

    # Atributos - Altura, peso, categoría, 
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

    #Puntos de Base
    for section in soup.find_all('div', class_="pokemon-stats-info active"):
        for lista in section.find_all('li'):

            aux = lista.text.strip()
            if (aux != ''):   
                txt = aux

            if ('data-value' in lista.attrs):
                val = lista['data-value']
            
            if (txt != '' and val != ''):              
                match txt:
                    case "PS":
                        ps = val
                    case "Ataque":
                        ataque = val
                    case "Defensa":
                        defensa = val
                    case "Ataque Especial":
                        ataque_esp = val    
                    case "Defensa Especial":
                        defensa_esp = val  
                    case "Velocidad":
                        velocidad = val
                      
                txt = ''
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
        'ps': ps,
        'ataque': ataque,
        'defensa': defensa,
        'ataque_esp': ataque_esp,
        'defensa_esp': defensa_esp,
        'velocidad': velocidad,
        'image_url': from_url
       
    })

    print (list(aug_pokedex))

    exit()


# 4. Crear un fichero csa con el dataset.


