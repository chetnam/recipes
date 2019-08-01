**Intro**

Cooking is fun, and websites that share recipes are great. Detailed stories are fantastic, but maybe not when you're scrolling to get to the recipe.

Here's a list of recipe-sharing websites ranked by how many words are used _before_ you can get to the recipe: <https://api-get-recipes.azurewebsites.net/api/sources>.

Check out API Details below to see what other data this project has collected.
***
**Summary**

This project collects information about recipes from various recipe-sharing websites, stores this information, and provides access to this information through an API. There are two main components of this project, currently deployed through Microsoft Azure Functions:

- scrape-recipes: Scripts that collects information about recipes from sources via web-scraping and stores in a database; runs once a day; written in Python
- get-recipes: Provides endpoints to access different types of information from the data collected; written in NodeJS
***
**API Details**
From the API, you can 
* Determine the verbosity of a source before you get to the recipe: 

  https://api-get-recipes.azurewebsites.net/api/sources
* Get five recipes from a given source. Use the query paramter 'source' to specify your requested source. For example, if you wanted recipes from Delish: 

  https://api-get-recipes.azurewebsites.net/api/sources?source=Delish
* Get all recipes collected for a certain keyword/food. Use the query parameter 'topic' to specify your keyword or food of choice. For example, if you wanted all recipes related to tacos, try 

  https://api-get-recipes.azurewebsites.net/api/recipes?topic=taco
* Get a random list of five recipes. If you're feeling spontaneous or indecisive, try 

  https://api-get-recipes.azurewebsites.net/api/recipes/random
***
**Other Details**
* This project currently collects recipes from [AllRecipes](https://www.allrecipes.com/), [Delish](https://www.delish.com/), and [Love&OliveOil](https://www.loveandoliveoil.com/). It collects no more than 10 recipes a day from each of these sites.
* Both the scraping script and the API are hosted on Azure Functions. Python on the Consumption Plan is a preview offering in Azure, so it is quite possible that the scraper could be unavailable without warning. The API is in NodeJS on the Consumption Plan, and should be stable; however, it is currently hosted on a Windows machine and a serverless service, which means the cold start time can be non-trivial -- i.e. you might have to wait a couple seconds when you click on a link from the API Details section.
* More recipe-collection sources might be added in the future.
