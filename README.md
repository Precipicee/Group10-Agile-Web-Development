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
2. Follow steps 1-2 of running the application if not done already.
3. Activate the virtual environment:

```bash

source venv/bin/activate
```


3. Run all tests:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

**Note:** Ensure it is run in the base directory so it can find the directory `./test` (it is a relative path, not absolute).

