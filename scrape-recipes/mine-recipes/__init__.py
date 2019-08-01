import datetime
import logging
from bs4 import BeautifulSoup, NavigableString, Tag
import requests
import re
import pyodbc
import os
from .recipe import Recipe

import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    logging.info('Starting function to collect recipes')
    global crsr
    crsr = connectToDb()
    all_new_recipes = create_delish_recipes() + create_allrecipes_recipes() + create_laoo_recipes()
    all_new_recipes_tuples =  [recipe.returnTuple() for recipe in all_new_recipes]

    logging.info(f'Updating db with {len(all_new_recipes)} recipes')
    if len(all_new_recipes_tuples)>0:
        upload_recipes_details(all_new_recipes_tuples)


# Download web page and return contexts of body tag -- generic across all websites
def get_recipes_page_body(base_url):
    page = requests.get(base_url)
    if page.status_code != 200:
        raise Exception(f'Given ({base_url}) does not exist')
    return BeautifulSoup(page.content, 'html.parser').body

def connectToDb():
    server_name = 'experiments-svr' 
    server_address = f'tcp:{server_name}.database.windows.net'
    db_name = 'experiments-sql'
    uname = os.environ['db_user']
    pwd = os.environ['db_pwd']
    driver = '{ODBC Driver 17 for SQL Server}'
    connection_string = f'DRIVER={driver};SERVER={server_address},1433;DATABASE={db_name};UID={uname}@{server_name};PWD={pwd}'
    cnxn = pyodbc.connect(connection_string, autocommit=True)
    
    return cnxn.cursor()

# to enable skipping visiting pages of recipes that have already been collected
def filter_out_existing(items, source):
    items_tups = tuple(items)
    sql = f'SELECT UniquePath FROM recipes.recipes where UniquePath in {items_tups}'
    global crsr
    rows = [item[0] for item in crsr.execute(sql).fetchall()]
    items = [item for item in items if item not in rows]
    return items

def upload_recipes_details(recipes):    
    sql = f'INSERT INTO recipes.recipes (Source, UniquePath, Title, NumWordsBeforeRecipe, FullPath, EstimatedTime, Author) VALUES (?,?,?,?,?,?,?)'
    global crsr
    crsr.executemany(sql, recipes)


# TODO: refactor following three functions to improve modularity

def create_delish_recipes():
    
    delish_base_domain = "https://www.delish.com"
    delish_base_recipes = "https://www.delish.com/cooking/recipe-ideas/"
    delish_links_to_recipes = filter_out_existing(get_delish_items(delish_base_recipes), 'Delish')

    return [item for item in [extract_delish_recipe_info(recipe, delish_base_domain) for recipe in delish_links_to_recipes] if item is not None]

def create_allrecipes_recipes():
    allrecipes_base_domain = "https://www.allrecipes.com"
    allrecipes_base_recipes = "https://www.allrecipes.com/recipes"

    allrecipes_links_to_recipes = filter_out_existing(get_allrecipes_items(allrecipes_base_recipes), 'All Recipes')

    return [item for item in [extract_allrecipes_recipe_info(recipe, allrecipes_base_domain) for recipe in allrecipes_links_to_recipes] if item is not None]

def create_laoo_recipes():
    
    laoo_base_domain = "https://www.loveandoliveoil.com"
    laoo_base_recipes = "https://www.loveandoliveoil.com/category/recipes"
    
    laoo_links_to_recipes = filter_out_existing(get_laoo_items(laoo_base_recipes), 'Love and Olive Oil')

    return [item for item in [extract_laoo_recipe_info(recipe, laoo_base_domain) for recipe in laoo_links_to_recipes] if item is not None]



# all delish.com details
def get_delish_items(base_recipes_url):
    delish_body = get_recipes_page_body(base_recipes_url)

    list_of_items = delish_body.find_all('div', class_="full-item-content")
    if len(list_of_items) > 10:
        list_of_items = list_of_items[0:10]
        
    links_to_recipes = [item.select('a')[0]['href'] for item in list_of_items]
    
    return links_to_recipes

def extract_delish_recipe_info(uniquePath, base_url):
    url = f'{base_url}{uniquePath}'
    try:
        recipe_page_body = get_recipes_page_body(url)
        source = 'Delish'
        title = recipe_page_body.select('h1', class_="content-hed recipe-hed")[0].text
        author = recipe_page_body.find('span', {'class': 'byline-name'}).text

        totalTime = re.sub('\s+', ' ', recipe_page_body.find('span', {'class': 'total-time-amount'}).text).strip()
        estimatedTime = int(totalTime[0])*60 + int(totalTime.split()[2])

        numWordsBeforeRecipe = len(re.findall(r'\w+', (recipe_page_body.find('div', {'class': 'recipe-introduction'}).text)))

        recipe = Recipe(source, url, title, numWordsBeforeRecipe, author, estimatedTime, uniquePath)
        return recipe
    except Exception as e:
        logging.info(f'Error in extract_delish_recipe_info: {e}')
        return None


# all allrecipes.com details
def get_allrecipes_items(base_recipes_url):
    allrecipes_body = get_recipes_page_body(base_recipes_url)

    list_of_items = allrecipes_body.find_all('article', {'class': 'fixed-recipe-card'})
    if len(list_of_items) > 10:
        list_of_items = list_of_items[0:10]
        
    links_to_recipes = [item.find('a', {'class': 'fixed-recipe-card__title-link'})['href'][26:] for item in list_of_items]
    
    return links_to_recipes

def extract_allrecipes_recipe_info(uniquePath, base_url):
    url = f'{base_url}{uniquePath}'
    try:
        recipe_page_body = get_recipes_page_body(url)
        source = 'All Recipes'
        title = recipe_page_body.find('h1', id='recipe-main-content').text
        author = recipe_page_body.find('span', class_='submitter__name').text
        
        totalTime = recipe_page_body.find('span', class_='ready-in-time').text.strip()

        if len(totalTime) > 4: # means both h and m exist
            hourIndex = totalTime.find('h')
            estimatedTime = int(totalTime[0:hourIndex-1].strip())*60 + int(totalTime[hourIndex+1:-2].strip())
        else:
            estimatedTime = int(totalTime[0:-1].strip()) if totalTime[-1]=='m' else int(totalTime[0:-1].strip())*60
        
        numWordsBeforeRecipe = len(re.findall(r'\w+', recipe_page_body.find('div', class_='submitter__description').text))
        
        recipe = Recipe(source, url, title, numWordsBeforeRecipe, author, estimatedTime, uniquePath)
        
        return recipe
    except Exception as e:
        logging.info(f'Error in extract_allrecipes: {e}')
        return None

# all loveandoliveoil.com details

def get_laoo_items(base_recipes_url):
    laoo_body = get_recipes_page_body(base_recipes_url)

    list_of_items = laoo_body.find_all('div', {'class': 'archive-post'})
    if len(list_of_items) > 10:
        list_of_items = list_of_items[0:10]

    links_to_recipes = [item.find('a', {'rel':'bookmark'})['href'][31:-5] for item in list_of_items]
    
    return links_to_recipes

def extract_laoo_recipe_info(uniquePath, base_url):
    url = f'{base_url}{uniquePath}'
    try:
        recipe_page_body = get_recipes_page_body(url)
        source = 'Love and Olive Oil'
        
        title = recipe_page_body.find('h1', {'class': "post-title"}).text
        author = recipe_page_body.find_all('div', {'class': "post-meta"})[1].text.strip().split()[-1]
        
        totalTime = recipe_page_body.find('div', {'class': "time post-meta"}).select('p')[-1].text[12:].strip()

        hourIndex = totalTime.find('hour')
        if hourIndex==-1: # minutes only
            estimatedTime = int(totalTime.split()[0])
        else:
            estimatedTime = int(totalTime.split()[0])*60
        
        numWordsBeforeRecipe = 0

        for sib in recipe_page_body.find('div', id='recipe').previous_siblings:

            if isinstance(sib, NavigableString): # skip items that aren't tags and aren't text either
                continue
        
            numWordsBeforeRecipe += len(sib.text)
        
        recipe = Recipe(source, url, title, numWordsBeforeRecipe, author, estimatedTime, uniquePath)
        return recipe

    except Exception as e:
        logging.info(f'Error in extract_laoo_recipe_info: {e}')
        return None
