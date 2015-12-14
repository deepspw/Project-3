## Project 3 - Restaurant app

[@pgpnda](https://github.com/pgpnda/Project-3)'s Udacity Project 3

### Description

Project for udacity to create a web based 
flask application to be used with restaurant data.

### Requirements

    - Python 2.7
    - sqlite3
    - sqlalchemy
    - python-requests
    - Flask
    - google places api key
    - google oAuth client ID
 
### How to use

Enter your google places, and google oAuth client id into 
the gAPI.py file in the allocated slots. You will also need
to download your client ID json from the [google developers 
console](https://console.developers.google.com). Be sure
to authorise your domain or local host + authorised redirects.
Once downloaded place in the same folder as gAPI.py and name 
it client_secrets.json

After run setup.py
This will create your database and populate it with data from
the google places API. You can alter the parameters of data you
want from db/db_setup.py. Run app.py to run the app, with all luck
you can now navigate to your domain of choice and use the website
from your browser.

If unable to use your own api key there is a live demo at [tomball.me](www.tomball.me)
Although google oAuth does not work on this version and thus you wont
be able to edit items.
