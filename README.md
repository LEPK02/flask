# Installation for Local Development
## Server
### Virtual Environment
- Install [python](https://www.python.org/downloads/) and [pipenv](https://pipenv.pypa.io/en/latest/installation.html)
- Create `.env` files based on their respective `.example.env` files in directories `/server/db` and `/server`
- Navigate to `/server` folder
```
cd server
```
- Activate virtual environment
```
pipenv shell
```
- Starting the Flask server
```
pipenv run python app.py
```
# Deployment
- Deploy on [pythonanywhere](https://www.pythonanywhere.com/)

# TODO
- MongoDB sessions
- Flask rate limiting
- Admin accounts
- Flask HTML templates