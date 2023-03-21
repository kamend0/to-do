# Flask To-Do List

A straight-forward web to-do list written in the Flask framework with Google OAuth; some supporting Jinja2 HTML templates as well as JavaScript for dynamic pages: mainly replacing the static text with forms when editing tasks, and interacting with the Python backend.

Database is just local SQLite3.


## Some leftover items

* Obviously, make prettier with a lot more CSS and HTML work. It's a bit ugly right now.
* Implement task groups.


## Some thanks

ChatGPT helped me with a lot of this. I still had to correct it a lot, but I seriously don't think I would have finished this without its help. LLMs are nifty!

Huge thanks to user [Daenney](https://github.com/daenney) for his years-old response to a thread about Google OAuth token expiration [here](https://github.com/singingwolfboy/flask-dance/issues/143) which led me to using some code from [this archived Spotify repo](https://github.com/spotify/gimme/blob/master/gimme/views.py#L52-L94). This solved my issues with Google's OAuth process and I am forever grateful. I even preserved the comments as they were so useful.