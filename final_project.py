from bs4 import BeautifulSoup  # for website parsing and scraping
import requests  # for http access
import json
from secrets import *
import sqlite3
import plotly.express as px #for boxplot graphing

CACHEFILE = "final_cache.json"

try:
    cache_file = open(CACHEFILE, 'r')
    cache_contents = cache_file.read()
    cache_diction = json.loads(cache_contents)
    cache_file.close()
except:
    cache_diction = {}


def get_unique_key(url):
    return url


def make_request_using_cache_html(url, header):
    unique_identifier = get_unique_key(url)

    if unique_identifier in cache_diction:
        print("Using Cache...")
        return cache_diction[unique_identifier]

    else:
        print("Fetching new data...")
        response = requests.get(url, headers=header) #unsure about this line
        cache_diction[unique_identifier] = response.text
        dumped_json_cache = json.dumps(cache_diction)
        write_file = open(CACHEFILE, "w")
        write_file.write(dumped_json_cache)
        write_file.close()
        return cache_diction[unique_identifier]

#create database
def init_db():
    connection = sqlite3.connect('final_proj.db')
    cur = connection.cursor()

    #drop tables
    statement = '''
        DROP TABLE IF EXISTS 'Directors';
    '''
    cur.execute(statement)
    statement = '''
        DROP TABLE IF EXISTS 'Movies';
    '''
    cur.execute(statement)

    connection.commit()

    #create tables
    statement = '''
        CREATE TABLE 'Directors' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Last' TEXT,
            'First' TEXT
        );
    '''
    cur.execute(statement)
    statement = '''
        CREATE TABLE 'Movies' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Title' TEXT,
            'DirectorId' INTEGER,
            'Rating' REAL,
            'Genre' TEXT,
            'Description' TEXT,
            FOREIGN KEY (DirectorId)
                REFERENCES Directors(Id)
        );
    '''

    cur.execute(statement)
    connection.commit()
    connection.close()

# init_db()

def insert_stuff_directors(movie_list):
    connection = sqlite3.connect('final_proj.db')
    cur = connection.cursor()

    for i in movie_list:
        first_name = i.director.split()[0]
        if len(i.director.split()) == 2: #and i.director != "No Director":
            last_name = i.director.split()[1]
        elif len(i.director.split()) == 3:
            last_name = i.director.split()[2]
        else:
            last_name = "NULL"

        cur.execute('SELECT First,Last FROM Directors WHERE First="' + str(first_name) + '" AND Last="' + str(last_name) + '"')
        check = cur.fetchone()
        if check == None:
            insertion = (None, last_name, first_name)
            statement = 'INSERT INTO "Directors" '
            statement += 'VALUES (?, ?, ?)'
            cur.execute(statement, insertion)
        else:
            pass
    connection.commit()
    connection.close()

def insert_stuff_movies(movie_list):
    connection = sqlite3.connect('final_proj.db')
    cur = connection.cursor()

    for i in movie_list:
        insertion = (None, i.title, i.director, i.rating, i.genre, i.description)
        statement = 'INSERT INTO "Movies" '
        statement += 'VALUES (?, ?, ?, ?, ?, ?)'
        cur.execute(statement, insertion)

        if len(i.director.split()) == 1:
            cur.execute('SELECT "Id" FROM Directors WHERE First="' + str(i.director.split()[0]) + '" AND Last="NULL"')
            director_id= cur.fetchone()[0]
            x = (str(director_id), str(i.director))
            statement = 'UPDATE Movies '
            statement += 'SET DirectorId=? '
            statement += 'WHERE DirectorId=?'
            cur.execute(statement, x)
        elif len(i.director.split()) == 2:
            cur.execute('SELECT "Id" FROM Directors WHERE First="' + str(i.director.split()[0]) + '" AND Last="' + str(i.director.split()[1]) + '"')
            director_id = cur.fetchone()[0]
            x = (str(director_id), str(i.director))
            statement = 'UPDATE Movies '
            statement += 'SET DirectorId=? '
            statement += 'WHERE DirectorId=?'
            cur.execute(statement, x)
        elif len(i.director.split()) == 3:
            cur.execute('SELECT "Id" FROM Directors WHERE First="' + str(i.director.split()[0]) + '" AND Last="' + str(i.director.split()[2]) + '"')
            director_id= cur.fetchone()[0]
            x = (str(director_id), str(i.director))
            statement = 'UPDATE Movies '
            statement += 'SET DirectorId=? '
            statement += 'WHERE DirectorId=?'
            cur.execute(statement, x)
    connection.commit()
    connection.close()



#functions to retrieve data
class Movie():
    def __init__(self, title, director, rating, desc, genre):
        self.title = title
        self.director = director
        self.rating = rating
        self.description = desc
        self.genre = genre

    def __str__(self):
        return "{} by {} ({})".format(self.title, self.director, self.rating)


def get_movie_genre_most_popular(genre, plot=False):
    baseurl = 'https://www.imdb.com/'
    genre_url = 'https://www.imdb.com/search/title/?genres=' + str(genre.lower()) + '&explore=title_type,genres&pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=3396781f-d87f-4fac-8694-c56ce6f490fe&pf_rd_r=E52VWCW2VRPPGPAYEJ03&pf_rd_s=center-1&pf_rd_t=15051&pf_rd_i=genre&ref_=ft_gnr_pr1_i_1'
    header = {'User-Agent': 'Mozilla/5.0'}
    page_text = make_request_using_cache_html(genre_url, header)
    page_soup = BeautifulSoup(page_text, 'html.parser')
    content_div = page_soup.find_all(class_='lister-item mode-advanced')
    movies = []
    if plot == False:
        for i in content_div[:25]:
            details_url_abbr = i.find('a')['href']
            # print(details_url_abbr)
            details_url = baseurl + details_url_abbr
            # print(details_url)
            movie_page_text = make_request_using_cache_html(details_url, header = header)
            movie_page_soup = BeautifulSoup(movie_page_text, 'html.parser')
            try:
                movie_title_header = movie_page_soup.find(class_='title_wrapper')
                movie_title = movie_title_header.find('h1').contents[0].strip()
                # print(movie_title)
            except:
                movie_title = "No Title"
                # print(movie_title)
            try:
                movie_director_header = movie_page_soup.find(class_='credit_summary_item')
                if movie_director_header.find(class_='inline').contents[0] == "Director:" or "Creator:":
                    movie_director = movie_director_header.find('a').contents[0].strip()
                    # print(movie_director)
            except:
                movie_director = "No Director"
                # print(movie_director)
            try:
                movie_rating = movie_page_soup.find(itemprop="ratingValue").contents[0].strip()
                # print(movie_rating)
            except:
                movie_rating = 'No Rating Provided'
                # print(movie_rating)
            try:
                movie_desc_header = movie_page_soup.find('meta', property='og:description')
                movie_desc = movie_desc_header["content"].strip()
                # print(movie_desc)
            except:
                movie_desc = "No Description"
                # print(movie_desc)
            movie_instance = Movie(movie_title, movie_director, movie_rating, movie_desc, genre)
            movies.append(movie_instance)

    n = 0
    if plot == True:
        for i in content_div:
            if n < 15:
                n += 1
                details_url_abbr = i.find('a')['href']
                details_url = baseurl + details_url_abbr
                movie_page_text = make_request_using_cache_html(details_url, header=header)
                movie_page_soup = BeautifulSoup(movie_page_text, 'html.parser')
                try:
                    movie_title_header = movie_page_soup.find(class_='title_wrapper')
                    movie_title = movie_title_header.find('h1').contents[0].strip()
                    # print(movie_title)
                except:
                    movie_title = "No Title"
                    # print(movie_title)
                try:
                    movie_director_header = movie_page_soup.find(class_='credit_summary_item')
                    if movie_director_header.find(class_='inline').contents[0] == "Director:" or "Creator:":
                        movie_director = movie_director_header.find('a').contents[0].strip()
                        # print(movie_director)
                except:
                    movie_director = "No Director"
                    # print(movie_director)
                try:
                    movie_rating = movie_page_soup.find(itemprop="ratingValue").contents[0].strip()
                    # print(movie_rating)
                except:
                    movie_rating = 'No Rating Provided'
                    # print(movie_rating)
                try:
                    movie_desc_header = movie_page_soup.find('meta', property='og:description')
                    movie_desc = movie_desc_header["content"].strip()
                    # print(movie_desc)
                except:
                    movie_desc = "No Description"
                    # print(movie_desc)
                movie_instance = Movie(movie_title, movie_director, movie_rating, movie_desc, genre)
                movies.append(movie_instance)
        
    insert_stuff_directors(movies)
    insert_stuff_movies(movies)
    return movies

# get_movie_genre_most_popular('sci-fi')

#functions to create Boxplots
#boxplots to show distribution of ratings by genre
def boxplot(genre):
    popular = get_movie_genre_most_popular(genre)
    ratings = []
    name = []
    for i in popular:
        ratings.append(i.rating)
        name.append(genre)
    fig = px.box(ratings, x=name, y=ratings, title="Ratings for " + str(genre))
    fig.update_xaxes(title_text='Genre')
    fig.update_yaxes(title_text='Rating', type='linear')
    fig.write_html('plots_for_final_proj.html', auto_open=True)

# boxplot('sci-fi')

def multiple_boxplots(list_of_genres):
    ratings= []
    name = []
    for genre in list_of_genres:
        popular = get_movie_genre_most_popular(genre, plot = True)
        for i in popular:
            ratings.append(i.rating)
            name.append(genre)
    fig = px.box(ratings, x=name, y=ratings, title="Comparison of Genre Ratings")
    fig.update_xaxes(title_text='Genre')
    fig.update_yaxes(title_text='Rating', type='linear')
    fig.write_html('plots_for_final_proj.html', auto_open=True)

# multiple_boxplots(['sci-fi', 'romance', 'crime'])

#interactive program for users to select and compare genres
genre_choices_dict = {'Action': 'action', 'Adventure': 'adventure', 'Animation': 'animation', 'Biography': 'biography', 'Comedy': 'comedy', 'Crime': 'crime', 'Documentary': 'documentary',
'Drama': 'drama', 'Family': 'family', 'Fantasy': 'fantasy', 'Film-Noir': 'film-noir', 'History': 'history', 'Horror': 'horror', 'Music': 'music', 'Musical': 'musical', 'Mystery': 'mystery',
'Romance': 'romance', 'Sci-Fi': 'sci-fi', 'Short': 'short', 'Sport': 'sport', 'Thriller': 'thriller', 'War': 'war', 'Western': 'western'}

lowercase_genre_choices = []
for i in genre_choices_dict:
    lowercase_genre_choices.append(i.lower())

def print_genre_choices():
    pretty_listing = []
    for i in genre_choices_dict:
        pretty_listing.append(i)
    enumerated_pretty_listing = list(enumerate(pretty_listing, 1))
    for i in enumerated_pretty_listing:
        print(i[0], i[1])

def get_enumerated_genre_choices():
    pretty_listing = []
    for i in genre_choices_dict:
        pretty_listing.append(i)
    enumerated_pretty_listing = list(enumerate(pretty_listing, 1))
    return enumerated_pretty_listing

def print_instructions():
    instructions = '''
    Possible commands:
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
    print(instructions)

def user_interactive_program():
    accepted_first = ['popular','compare','help','exit','list','info', 'boxplot']
    response = ''
    enumerated_genres = get_enumerated_genre_choices()
    init_db()
    print_instructions()
    while response != 'exit':
        print(' ')
        response = input('Enter a command: ').lower()
        split = response.split()
        if split[0] not in accepted_first:
            print("Invalid command. Please try again. Enter 'help' for list of possible commands")
        if split[0] == "list":
            print_genre_choices()
        elif split[0] == "help":
            print_instructions()
        elif split[0] == "boxplot":
            genre_comparing = split[1].split(',')
            if split[1] not in lowercase_genre_choices and str.isnumeric(split[1]) != True:
                print("Please enter a valid genre")
                continue
            elif str.isnumeric(genre_comparing[0]) == True:
                for genre_num in genre_comparing:
                    for x in enumerated_genres:
                        if x[0] == int(genre_num):
                            boxplot(x[1])
            elif str.isnumeric(genre_comparing[0]) != True:
                boxplot(split[1])
        elif split[0] == "compare":
            genre_comparing = split[1].split(',')
            if str.isnumeric(genre_comparing[0]) == True:
                updated_list = []
                for genre_num in genre_comparing:
                    for x in enumerated_genres:
                        if x[0] == int(genre_num):
                            updated_list.append([x[1]])
                real_list = []
                for i in updated_list:
                    real_list.append(i[0])
                multiple_boxplots(real_list)
            else:
                for g in genre_comparing:
                    if g not in lowercase_genre_choices:
                        print("Only valid genres will be graphed")
                        continue
                updated_list = []
                for genre in genre_comparing:
                    for k in genre_choices_dict:
                        if k.lower() == genre:
                            updated_list.append(genre_choices_dict[k])
                multiple_boxplots(updated_list)
        elif split[0] == "popular":
            if str.isnumeric(split[1]) == True:
                for x in enumerated_genres:
                    if int(split[1]) == x[0]:
                        movie_list = get_movie_genre_most_popular(genre_choices_dict[x[1]])
            elif split[1] not in lowercase_genre_choices:
                print("Please enter a valid genre")
                continue
            else:
                for k in genre_choices_dict:
                    if k.lower() == split[1]:
                        movie_list = get_movie_genre_most_popular(genre_choices_dict[k])
            active_enumerated_movie_list = list(enumerate(movie_list, start = 1))
            for b in active_enumerated_movie_list:
                print(b[0], b[1])
            print("type 'info <movie number>' to get the movie's description")
            print(" ")
        elif split[0] == "info":
            try:
                for m in active_enumerated_movie_list:
                    if int(split[1]) == m[0]:
                        title_for_description = m[1].title
                        print(title_for_description)
                        connection = sqlite3.connect('final_proj.db')
                        cur = connection.cursor()
                        cur.execute('SELECT Description FROM Movies WHERE Title="' + str(title_for_description) +'"')
                        info = cur.fetchone()[0]
                        print(info)
                        connection.commit()
                        connection.close()
            except:
                print("No active movie list. Get one by typing 'popular <genre>'")
                print(" ")
    print("Bye!")
            

if __name__ == "__main__":
    user_interactive_program()
    pass