from apis import spotify
from apis import send_grid
import random
from datetime import datetime

def print_menu():
    print('''
---------------------------------------------------------------------
Spotify Genius
---------------------------------------------------------------------
1 - Select your favorite genres  
2 - Select your favorite artists 
3 - Discover new music
4 - Quit
---------------------------------------------------------------------
    ''')

########################################################################################################################

# Initializing genre list and user preferences

available_genres = spotify.get_genres_abridged()

genres = []
for genre in available_genres:
    genres.append({'name': genre, 'selected': False})

artists = []

########################################################################################################################

# Functions used in the main menu functions

def print_genre_list():
    genre_template = '{num}. [{selected}] {genre}'
    list_num = 1
    for genre in genres:
        if genre['selected'] == True:
            selected = 'X'
        else:
            selected = ' '
        print(genre_template.format(num=list_num, selected=selected, genre=genre['name']))
        list_num += 1


def search_and_add_artists():

    while True:
        search_term = input('\nSearch for an artist: ')
        artist_results = spotify.get_artists(search_term)
        if len(artist_results) > 10:
            artist_results = artist_results[:10]
        selection_status = {}

        artist_template = '{num}. {artist_name}'

        list_num = 1
        print('\nHere are some artist results for "' + search_term + '":\n')
        for artist in artist_results:
            print(artist_template.format(num=list_num, artist_name=artist.get('name')))
            list_num += 1

        artists_to_add = input('\nTo add one or more artists to your recommendations, type the numbers by their names separated by commas and without spaces: ')
        artists_to_add = artists_to_add.split(',')
        if artists_to_add == ['']:
            print('\nNo artists have been added.')
        else:
            for artist in artists_to_add:
                if artist_results[int(artist) - 1] not in artists:
                    artists.append(artist_results[int(artist) - 1])
                    selection_status[artist_results[int(artist) - 1]['name']] = 'added'
                else:
                    selection_status[artist_results[int(artist) - 1]['name']] = 'already_added'
            # this could be done much better as a separate function, but oh well
            print('\nYou have:')
            for change in selection_status:
                if selection_status[change] == 'added':
                    print('Added', change, 'to your artists list.')
                if selection_status[change] == 'already_added':
                    print('Tried to add', change + ', who was already in your artists list.')
        
        if artists != []:
            print('\nYour selected artists are now:')
            for artist in artists:
                print(artist['name'])

        search_again = input('\nWould you like to search artists again? (y/n) ')
        if search_again.lower() == 'y':
            continue
        else:
            break


def remove_artists():
    artist_template = '{num}. {artist_name}'
    list_num = 1
    if artists == []:
        print('\nYour artists list is currently empty. Try adding some using the search and add feature.')
    else:
        print('\nYou currently have', len(artists), 'artists in your artists list:')
        for artist in artists:
            print(artist_template.format(num=list_num, artist_name=artist.get('name')))
            list_num += 1

        artist_to_remove = input('\nType the number of the artist you want to remove from your list: ')
        if artist_to_remove == '':
            print('\nNo artists were removed from your list.')
        else:
            removed_artist = artists.pop(int(artist_to_remove) - 1)
            print('\nThe artist', removed_artist.get('name'), 'was removed from your list.')

            if artists != []:
                print('\nYour selected artists are now:')
                for artist in artists:
                    print(artist['name'])
            else:
                print('\nYour artists list is now empty.')
            

def clear_artist_list():
    global artists
    if artists == []:
        print('\nYour artists list is currently empty. Try adding some using the search and add feature.')
    else:
        choice = input('\nAre you sure that you want to completely clear your selected artists list? (y/n) ')
        if choice.lower() == 'y':
            artists = []
            print('\nYour artists list has been cleared.')
        elif choice.lower() == 'n':
            print('\nYour artists list has not been cleared.')


def clear_genre_list():
    
    global genres
    genres = []
    for genre in available_genres:
        genres.append({'name': genre, 'selected': False})

    print('\nYour selected genres have been cleared.')


def print_tracklist_table(tracklist:list):
    width = 152
    template = '{0:<3}| {1:>47.47} | {2:>47.47} | {3:>47.47}'
    print('-' * width)
    print(template.format('#', 'Title', 'Artist', 'Album'))
    print('-' * width)
    track_num = 1
    for track in tracklist:
        track_name = track.get('name')
        artist_name = track.get('artist').get('name')
        album_name = track.get('album').get('name')
        print(template.format(track_num, track_name, artist_name, album_name))
        track_num += 1
    print('-' * width)


def create_html_tracklist(tracklist:list):
    track_players = []
    for track in tracklist:
        track_id = track.get('id')
        track['track_player'] = 'track_player'

        track_player_html = spotify.get_track_player_html(track_id)
        track_players.append(track_player_html)

    html_tracklist = spotify.get_formatted_tracklist_table_html(tracklist)
    html_tracklist = html_tracklist.replace('<th>name</th>', '<th>Title</th>')
    html_tracklist = html_tracklist.replace('<th>album_image_url_small</th>', '<th>Album Art</th>')
    html_tracklist = html_tracklist.replace('<th>artist_name</th>', '<th>Artist</th>')
    html_tracklist = html_tracklist.replace('<th>album_name</th>', '<th>Album</th>')
    html_tracklist = html_tracklist.replace('<th>track_player</th>', '<th>Preview Song</th>')

    player_template = '<td>{0}</td>'
    
    for iframe in track_players:
        html_tracklist = html_tracklist.replace('<td>track_player</td>', player_template.format(iframe), 1)
    
    return html_tracklist


def get_file_path(file_name):
    import os
    import sys
    dir_path = os.path.dirname(sys.argv[0])
    return os.path.join(dir_path, file_name)


def save_tracklist_as_file(tracklist:list):
    html_string = create_html_tracklist(tracklist)

    now = datetime.now()
    filename = now.strftime('Spotify Genius %m-%d-%Y %H-%M.html')

    f = open(get_file_path(filename), 'w', encoding='utf8')
    f.write(html_string)
    f.close()

    print('\nYour playlist has been saved to "' + get_file_path(filename) + '".')


def save_tracklist_as_temp_file(tracklist:list):
    html_string = create_html_tracklist(tracklist)

    filename = 'sg_temp.html'
    temp_path = get_file_path(filename)

    f = open(temp_path, 'w', encoding='utf8')
    f.write(html_string)
    f.close()

    return temp_path


def delete_temp_file(temp_path):
    import os
    os.remove(temp_path)


def email_with_html_attachment(from_email:str, to_email:str, subject:str, body:str, filename:str, file_path:str):
    import base64
    from apis import authentication
    from sendgrid.helpers.mail import (
        Mail, Attachment, FileContent, FileName,
        FileType, Disposition)
    from sendgrid import SendGridAPIClient

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=body)
    with open(file_path, 'rb') as f:
        data = f.read()
        f.close()
    encoded = base64.b64encode(data).decode()
    attachment = Attachment()
    attachment.file_content = FileContent(encoded)
    attachment.file_type = FileType('text/html')
    attachment.file_name = FileName(filename)
    attachment.disposition = Disposition('attachment')
    message.attachment = attachment
    try:
        sendgrid_client = SendGridAPIClient(authentication.get_token('https://www.apitutor.org/sendgrid/key'))
        sendgrid_client.send(message)
        return True
    except:
        return False


def email_to_self(tracklist:list):
    temp_path = save_tracklist_as_temp_file(tracklist)
    
    email = input('\nPlease type your email address: ')
    now = datetime.now()
    subject = now.strftime('Your Recommendations from Spotify Genius on %m/%d/%Y')
    filename = now.strftime('Spotify Genius %m-%d-%Y %H-%M.html')
    body = 'Here is your Spotify Genius playlist!\nIn order to view this file, download it to your computer first (or drag it to your desktop), then double click.'
    success = email_with_html_attachment(email, email, subject, body, filename, temp_path)

    if success:
        print('\nYour playlist has been successfully sent.')
    else:
        print('\nThere was an issue sending your playlist. Please try again.')

    delete_temp_file(temp_path)


def email_to_others(tracklist:list):
    temp_path = save_tracklist_as_temp_file(tracklist)
    
    now = datetime.now()
    email = input('\nPlease type your email address: ')
    sender_name = input('\nAlso, please enter your name so your recipient knows who you are!: ')
    recipient = input('\nFinally, please enter your recipient\'s email address: ')
    subject_template = '{sender} sent you a playlist they think you\'d like!'
    filename_template = now.strftime('{sender}\'s Spotify Genius %m-%d-%Y %H-%M.html')
    body_template = 'Here is a specially-made Spotify Genius playlist that your friend {sender} sent you!\nIn order to view this file, download it to your computer first (or drag it to your desktop), then double click.'
    success = email_with_html_attachment(email, recipient, subject_template.format(sender=sender_name), body_template.format(sender=sender_name), filename_template.format(sender=sender_name), temp_path)

    if success:
        print('\nYour playlist has been successfully sent.')
    else:
        print('\nThere was an issue sending your playlist. Please try again.')

    delete_temp_file(temp_path)


def fetch_and_handle_recommendation_data(artist_input, genre_input):
    print('\nNow creating a brand new playlist of recommendations, just for you...')
    recommendations = spotify.get_similar_tracks(artist_ids=artist_input, genres=genre_input)

    print('\nHere it is! Take a look:')
    print_tracklist_table(recommendations)

    print('\nYou can now either:')
    print('1. Download this playlist as an HTML file to your computer')
    print('2. Email this playlist to yourself (with the file attached)')
    print('3. Email this playlist to a friend')
    print('4. Do nothing and return to the main menu')

    while True:
        tracklist_choice = input('\nWhat would you like to do? ')
        if tracklist_choice == '1':
            save_tracklist_as_file(recommendations)
            break
        elif tracklist_choice == '2':
            email_to_self(recommendations)
            break
        elif tracklist_choice == '3':
            email_to_others(recommendations)
            break
        elif tracklist_choice == '4':
            break
        else:
            print('\nThat\'s not a valid option. Please try again.')


########################################################################################################################

# Functions to handle main menu options

def handle_genre_selection():
    # 1. Allow user to select one or more genres using the 
    #    spotify.get_genres_abridged() function
    # 2. Allow user to store / modify / retrieve genres
    #    in order to get song recommendations 

    print('\nAvailable genres:\n')
    print_genre_list()
    print()

    genre_status = {}
    genres_to_select = input('Type the numbers of the genres you want to select (or deselect), separated by commas and without spaces (or type "c" to clear all): ')
    genres_to_select = genres_to_select.split(',')
    if genres_to_select == ['']:
        print('\nNo changes have been made to your selected genres.')
    elif genres_to_select == ['c']:
        clear_genre_list()
    else:
        for genre in genres_to_select:
            if genres[int(genre) - 1]['selected'] != True:
                genres[int(genre) - 1]['selected'] = True
                genre_status[genres[int(genre) - 1]['name']] = 'checked'
            elif genres[int(genre) - 1]['selected'] == True:
                genres[int(genre) - 1]['selected'] = False
                genre_status[genres[int(genre) - 1]['name']] = 'unchecked'
        
        print('\nYou have:')
        for change in genre_status:
            if genre_status[change] == 'checked':
                print('Selected', change + '.')
            if genre_status[change] == 'unchecked':
                print('Deselected', change + '.')
    

def handle_artist_selection():
    # 1. Allow user to search for an artist using 
    #    spotify.get_artists() function
    # 2. Allow user to store / modify / retrieve artists
    #    in order to get song recommendations

    print('''
---------------------------------------------------------------------
Artist Selection Options
---------------------------------------------------------------------
1 - Search for and add artists to your recommendation list  
2 - Remove a specific artist from your list
3 - Clear your artists list completely
---------------------------------------------------------------------
    ''')

    while True:
        menu_choice = input('What would you like to do? ')
        if menu_choice == '1':
            search_and_add_artists()
            break
        elif menu_choice == '2':
            remove_artists()
            break
        elif menu_choice == '3':
            clear_artist_list()
            break
        else:
            print(menu_choice, 'is an invalid choice. Please try again.')
        print()
    

def get_recommendations():
    # 1. Allow user to retrieve song recommendations using the
    #    spotify.get_similar_tracks() function
    # 2. List them below
    
    selected_genres = []
    for genre in genres:
        if genre.get('selected'):
            selected_genres.append(genre.get('name'))
    
    ids_of_selected_artists = []
    for artist in artists:
        ids_of_selected_artists.append(artist.get('id'))
    
    if len(selected_genres) + len(ids_of_selected_artists) == 0:
        print('\nYou must choose at least one genre or artist in order to get recommendations.')
    elif len(selected_genres) + len(ids_of_selected_artists) <= 5:
        artist_input = ids_of_selected_artists
        genre_input = selected_genres

        fetch_and_handle_recommendation_data(artist_input, genre_input)
    elif len(selected_genres) + len(ids_of_selected_artists) > 5:
        if len(selected_genres) <= 2:
            slots_left = 5
            genre_input = selected_genres
            slots_left -= len(genre_input)

            artist_input = []
            for i in range(slots_left):
                dummy_var = i
                random_artist = random.choice(ids_of_selected_artists)
                artist_input.append(random_artist)
                ids_of_selected_artists.remove(random_artist)
            
            fetch_and_handle_recommendation_data(artist_input, genre_input)
        elif len(ids_of_selected_artists) <= 3:
            slots_left = 5
            artist_input = ids_of_selected_artists
            slots_left -= len(artist_input)

            genre_input = []
            for i in range(slots_left):
                random_genre = random.choice(selected_genres)
                genre_input.append(random_genre)
                selected_genres.remove(random_genre)
            
            fetch_and_handle_recommendation_data(artist_input, genre_input)
        else:
            artist_input = []
            for i in range(3):
                random_artist = random.choice(ids_of_selected_artists)
                artist_input.append(random_artist)
                ids_of_selected_artists.remove(random_artist)

            genre_input = []
            for i in range(2):
                random_genre = random.choice(selected_genres)
                genre_input.append(random_genre)
                selected_genres.remove(random_genre)
            
            fetch_and_handle_recommendation_data(artist_input, genre_input)
        

########################################################################################################################

# Begin Main Program Loop:
print()
print('=' * 120)
print('\nWelcome to Spotify Genius!\n\nThis app uses your favorite music genres and artists to give you Spotify song recommendations.\nThen, you can either save the playlist to your computer or email it to yourself or a friend!\n\nLet\'s get started!')
while True:
    print_menu()
    choice = input('What would you like to do? ')
    if choice == '1':
        handle_genre_selection()
    elif choice == '2':
        handle_artist_selection()
    elif choice == '3':
        get_recommendations()
        # In addition to showing the user recommendations, allow them
        # to email recommendations to one or more of their friends using
        # the sendgrid.send_mail() function.
    elif choice == '4':
        print('\nThanks for using Spotify Genius! Quitting now...')
        break
    else:
        print(choice, 'is an invalid choice. Please try again.')
    print()
    input('Press enter to continue...')
