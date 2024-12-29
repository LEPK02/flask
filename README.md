<!-- START doctoc -->
<!-- END doctoc -->
# Task
The API backend will be used by a certain mental health institute for clinicians to manage therapy client cases within the institute. Assume that the frontend for the application has already been built.

1. The clinicians require a login system for the application. Implement the following:
  - POST /register: Register a user with username and password.
  - POST /login: Authenticate the user and return a success message.

2. In this institute, there are two roles for clinicians: "Senior" and "Junior". The success message for the /login method must reflect these roles.
  - Newly registered clinicians are automatically set as "Junior".
  - POST /promote: Promote a user from "Junior" to "Senior" with username and password. If the user is already "Senior", return a message accordingly.
  - POST /demote: Demote a user from "Senior" to "Junior" with username and password. If the user is already "Junior", return a message accordingly.

3. There are 3 clinicians who you must register with the back-end first:
  - Dr. Joel Tan. Username: joel87, Password: pwjoel87, Role: Senior
  - Dr. Huang Shimin. Username: shiminh, Password: pwshiminh , Role: Junior
  - Dr. Rishi Agarwal. Username: rishiaw, Password: pwrishiaw, Role: Junior

4. In this institute, there are several therapy cases. Implement the following:
  - GET /cases: Fetch the list of all cases.
  - POST /case: Add a case.
  - Each case must be a JSON object with the following fields: name, description
  - Fetching and adding a case does not depend on the role of the clinician.

5. There are 3 cases that you must register with the back-end first:
{ "name": "Jonathan Lim", "description": "A 28-year-old software engineer who is experiencing intense anxiety during team meetings and is struggling to speak up, fearing judgment from colleagues." }
{ "name": "Angela Paolo", "description": "A 42-year-old teacher who is coping with the recent loss of a parent and is finding it difficult to concentrate on work and daily responsibilities." }
{ "name": "Xu Yaoming", "description": "A 16-year-old high school student who is feeling overwhelmed by academic pressure and is struggling to balance schoolwork, extracurriculars, and personal time." }

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
# Usage
- Deployed at https://flask-x9e4.onrender.com
- View Swagger docs at https://flask-x9e4.onrender.com/apidocs/
# TODO
- MongoDB sessions
- Flask rate limiting
- Admin accounts
- Flask HTML templates
