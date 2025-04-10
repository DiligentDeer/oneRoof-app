# Quiz App with Google Sheets Integration

A modern, interactive quiz application built with Streamlit that uses Google Sheets as a database for storing questions, answers, and quiz results. The app includes an admin dashboard with visualizations for analyzing quiz performance.

## Features

- Interactive quiz interface with timer
- Google Sheets integration for data storage
- Admin dashboard with performance analytics
- Real-time score tracking
- Beautiful and responsive UI
- Print-friendly results page

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd quiz-app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Google Sheets API:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Google Sheets API
   - Create credentials (OAuth 2.0 Client ID)
   - Download the credentials and save as `credentials.json` in the project root

5. Create a `.env` file in the project root:
```
SPREADSHEET_ID=your_spreadsheet_id
ADMIN_PASSWORD=your_admin_password
```

6. Set up Google Sheets:
   - Create a new Google Sheet
   - Copy the spreadsheet ID from the URL
   - Create three sheets named:
     - "Quiz Attempts"
     - "Questions"
     - "Answers"
   - Add the following headers to each sheet:
     - Quiz Attempts: timestamp, name, score, total_questions, time_taken, completed
     - Questions: id, question, options, correct_answer
     - Answers: attempt_id, question_id, answer, correct

## Running the Application

1. Start the Streamlit server:
```bash
streamlit run app.py
```

2. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

## Usage

### For Quiz Takers
1. Enter your name on the landing page
2. Click "Start Quiz"
3. Answer the questions within the time limit
4. View your results and print if desired

### For Administrators
1. Use the sidebar to access the admin login
2. Enter the admin password
3. View analytics and performance metrics
4. Monitor quiz attempts and results

## Security Notes

- Change the default admin password in production
- Keep your `credentials.json` and `.env` files secure
- Never commit sensitive credentials to version control

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 