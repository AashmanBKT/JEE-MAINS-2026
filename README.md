# JEE Mains Mock Test Platform

This is a local web application that allows you to attempt the Jan 2026 JEE Mains papers.

## Features
- **All Jan 2026 Shifts:** Includes Physics, Chemistry, and Mathematics papers.
- **Redacted Papers:** The answers originally written in the PDFs have been removed so you can take a mock test fairly.
- **OMR Sheet Interface:** Provides an interface for 20 MCQs and 10 Numericals for each subject.
- **Time Limit:** A 3-hour timer is strictly enforced.
- **Scoring & Percentile:** Calculates +4 for correct, -1 for incorrect MCQs, and +4 for correct numericals with no negative marking. Attempt is restricted to the first 5 answered numericals. A simulated percentile calculation based on the score is shown at the end.

## How to Run

1. Open a terminal or command prompt in this directory (`c:\PIPO\Abhik\webapp`).
2. Run the command: `python app.py`
3. Open your web browser and go to: [http://localhost:5000](http://localhost:5000)

## Folder Structure
- `app.py`: The Flask server that serves the pages and evaluates scores.
- `answers.json`: Contains the parsed answer keys for all papers.
- `static/papers/`: Contains the PDFs with the original answers hidden.
- `templates/`: HTML templates for the UI.
