# SI 507 Final Project

By: Reilly Potter

## Project Instructions: 
My project allows the user to scrape the IMDb site to view the most popular movies in each genre, get information about the popular movies, create a boxplot of those popular movies' ratings,
compare several genres ratings using boxplots, etc.

- The user is able to select one of the genres (there are 23 genres) and see the distribution of ratings within that genre’s popular movies via boxplots.  
- In addition, they can also compare the ratings of multiple genres via boxplots. I will be using Plotly to create the boxplots, and command-line prompts to accept the users’ inputs.  
- The user is also able to list all genres using the ‘list’ command, and the program will list all of the genres along with a number.  
- The user can then see the top 25 most popular movies in any of those genres by either typing ‘popular <genre number from list>’ or ‘popular <genre>’ (ex: popular action).  
- The user can also get information about the movies on the popular list by using the 'info <movie number>' command. It will give them the title and description for that movie.  
- The user can enter ‘exit’ to exit the entire program and will see ‘Bye!’ appear in their terminal.  
- The user can use the command ‘help’ to see the command prompt instructions, and the instructions will automatically show up one time when they run the program.  

Python Packages Required:  
- BeautifulSoup
- Requests
- Json
- Sqlite3
- plotly.express

These are the instructions they will see:  

Possible commands:

    '''
    'list genres':  
        - Presents the list of available genres  
        - A valid genre is how it is presented in this list (all lowercase is fine)  
    'popular <genre number>/<genre name>':  
        - Presents the list of most popular movies in that genre  
        - Example calls: popular 3, popular action  
    'boxplot <genre number>/<genre name>':  
        - Takes only one genre at a time  
        - Presents a boxplot showing distribution of ratings in genre  
    'compare <list of genre numbers/names separated by comma>':  
        - Presents boxplots comparing the ratings of multiple desired genres  
        - Please don't put spaces in genre list  
        - Example calls: compare 4,6,8 or compare action,horror,sci-fi,romance  
    'exit':  
        - Exits the program  
    'help':  
        - Provides list of available commands (these instructions)  
        '''  
