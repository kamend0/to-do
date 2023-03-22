# Flask To-Do List

A straight-forward to-do list CRUD web app written in the Flask framework, using Jinja2 HTML templates as well as JavaScript for dynamic pages (e.g., replacing static text with submit form for editing tasks, and interacting with the Python backend). Features Google OAuth using the Flask-Dance library.

Database is a local SQLite3. Currently, no passwords are stored; the only way to use the app is via Google OAuth.


## Some leftover items

* **IN-PROGRESS** Continue to make prettier and more user-friendly with more CSS.
* Implement a simple email sign-up and login, exploring password encryption.
* Implement task groups, and display tasks in groups.
* Have an option for temporary users, where their tasks are only stored in perhaps the session, and are destroyed once they leave the page.


## Some thanks

ChatGPT helped me with a lot of this. I still had to correct it a lot, but I seriously don't think I would have finished this without its help. LLMs are nifty!

Huge thanks to user [Daenney](https://github.com/daenney) for his years-old response to a thread about Google OAuth token expiration [here](https://github.com/singingwolfboy/flask-dance/issues/143) which led me to using some code from [this archived Spotify repo](https://github.com/spotify/gimme/blob/master/gimme/views.py#L52-L94). This solved my issues with Google's OAuth process and I am very grateful, as this was something ChatGPT was not very helpful with. I even preserved the comments in my own code as they were so useful.