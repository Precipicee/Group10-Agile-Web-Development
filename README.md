# Group10-Agile-Web-Development
Group 10's Agile Web Development Project: FitTrack

FitTrack is a simple, user-friendly fitness tracker web application developed for the Agile Web Development unit. The app allows users to track their daily weight and exercise habits and visualize their progress over time.

---

## Group Members

| UWA ID       | Name             | GitHub Username   |
|--------------|------------------|-------------------|
| 24386354     | Mika Li          | MMs-gitH          |
| 23813728     | Dante McGee      | Precipicee        |
| 22487434     | Bianca Sumich    | biancasumich      |
| 24648002     | Zachary Wang     | ZacAster          |

---

## How to run the Application
1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Create a `.env` file in the root directory:
   ```bash
   nano .env
   ```

   Add the following lines:
   ```env
   SECRET_KEY=
   WTF_CSRF_SECRET_KEY=
   OPENAI_API_KEY=
   ```

3. Make the run script executable and start the app:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
Note: Please register your own API key via the OpenAI platform.
---

## Running the Unit and System Tests

To run all tests:

1. Ensure Google Chrome and ChromeDriver (v124+) are installed.
2. Activate the virtual environment:

```bash
source venv/bin/activate

3. Run all tests:

```bash
python -m unittest discover -s test -p "*test.py" -v
```

**Note:** Ensure it is run in the base directory so it can find the directory `./test` (it is a relative path, not absolute).

## Tutorial of the Website

After getting the server to run and reaching the homepage on `http://127.0.0.1:5000`, you will be greeted with the `Home` page.

[image of homepage here]

On this homepage, you can ___.

In the navigation bar at the top of the screen, there initially appears three tabs: `Home`, `About` and `Sign In`.

> Home is the page we are currently on.

> About includes a brief introduction to our website.

> Sign In takes you to the sign-in page, where you can either sign-in or choose to sign-up.

Once creating an account using the `Sign Up` page, you must fill in some preliminary information.

[images of sign-up and preliminary info here]

Once this information is filled out, you will be taken to the `Data Page`, which allows you to choose if you want to add data (the `Upload Data` portion of the project), or view reports (the `Visualise Data` section). New tabs in the navigation bar will now be included: `Entry` and `Reports`.

[image of navbar]

