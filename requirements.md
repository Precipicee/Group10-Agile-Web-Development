# Project Requirements - FitTrack

## Completed Features

### 1. Static Webpage Setup
- Basic UI built using HTML, CSS, and JavaScript.
- Includes homepage, registration page, data upload page, etc.

### 2. Button Functionality
- Implemented core button functions such as adding/removing entries and submitting forms.

### 3. SQLite Database Integration
- Uses SQLite to store user information, weight logs, and diet/exercise records.
- Database schema and data writing/reading functionalities are in place.

### 4. User Registration & Login
- Enables user registration with username and password validation.
- (Optionally) can add "remember me" or access control in future.

### 5. Data Upload Functionality
- Users can upload their daily logs for weight, diet, and exercise through a form.
- Supports multiple entries and connects with the database.

### 6. Data Display Feature
- Uploaded data is successfully displayed in the frontend.
- Users can browse their history of weight and habit logs.

---

## Pending Features

### 1. Data Analysis Module
#### A. Weight Analysis
- Analyze user weight trends.
- Predict the estimated date to reach the target weight.

#### B. Diet and Exercise Analysis
- Evaluate if the diet and exercise patterns are healthy.
- AI API may be used to generate personalized suggestions.

#### C. Combined Analysis (Weight + Habit)
- Correlate weight change with exercise and diet habits.
- E.g., check if stagnation in weight loss is due to reduced physical activity or diet issues.
- Consider using AI API for comprehensive pattern analysis.

### 2. Analysis Display Page (Frontend)
- Design a dedicated page for showing analysis results with charts and AI feedback.
- Support paginated view of analysis history and allow re-analysis using a button.

### 3. Backend Logic for Analysis
- Implement backend logic to collect and send user data to AI API.
- Add caching and error handling to avoid repeat requests and handle API failures.

---

## Optional Future Features

- Health score evaluation system.
- Export personal monthly report or health summary as PDF.
- Data sharing via email or social media.
- Etc.
