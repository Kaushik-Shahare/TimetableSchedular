# Automatic Timetable Scheduling System

## 📚 Project Overview

The Automatic Timetable Scheduling System is a web-based application designed to solve the complex problem of academic timetable generation. Using graph coloring algorithms and backtracking techniques, this system creates conflict-free schedules while respecting various constraints such as faculty availability, room capacity, and course requirements.

## 🎯 Why This Project?

Creating academic timetables manually is:
- **Time-consuming**: Often taking days or weeks to complete.
- **Error-prone**: Easy to create conflicts with manual scheduling.
- **Inflexible**: Difficult to adjust when requirements change.
- **Sub-optimal**: May not efficiently utilize available resources.

This project was created to automate the scheduling process, minimize human error, optimize resource utilization, and provide visual insights into the algorithm's operation.

## ✨ Key Features

- **Automated Scheduling**: Generate conflict-free timetables with a single click.
- **Constraint Management**: Handle faculty availability, room assignments, and course requirements.
- **Algorithm Visualization**: Watch the backtracking algorithm in action with step-by-step animation.
- **Multiple Views**: Filter and view timetables by faculty, room, or course.
- **User-friendly Interface**: Intuitive design with a responsive web interface.
- **Resource Management**: Easy management of faculty, courses, rooms, and time slots.
- **Print and Export Options**: Save and print final timetables for offline use.
- **Sample Data Generation**: Quickly populate the system with demo data.

## 🛠️ Technologies Used

- **Backend**: Python, Django
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Database**: SQLite (for development) and PostgreSQL (for production)
- **Algorithms**: Graph Coloring, Backtracking, Constraint Satisfaction
- **Visualization**: Vis.js for displaying algorithm steps

## 📋 Prerequisites

- Python 3.8+
- Django 4.0+
- pip (Python package manager)
- Virtual environment (recommended)

## 🚀 Getting Started

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Kaushik-Shahare/TimetableSchedular.git
   cd AutomaticTimetable
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**:
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the application**:
   Open your browser and navigate to `http://127.0.0.1:8000/`

### Quick Start Guide

1. **Create Sample Data**:
   - Use the web interface “Create Sample Data” option or run:
     ```bash
     python manage.py create_sample_data
     ```

2. **Set Up Resources**:
   - Add or modify data for faculty, courses, rooms, and time slots via the admin interface or provided forms.

3. **Generate Timetable**:
   - Click “Generate Timetable” for automatic schedule generation.
   - Alternatively, use “Generate with Steps” for detailed output or “Animated Generation” for visualization.

4. **View and Analyze**:
   - Utilize filtering options to see views by faculty, room, or course.
   - Print or export the final timetable as needed.

## 📊 Algorithm Explained

The timetable generation employs a **constraint satisfaction approach** using the following concepts:

1. **Graph Coloring Model**:
   - **Vertices**: Represent courses (or course sessions)
   - **Edges**: Represent conflicts (shared resources)
   - **Colors**: Represent time slots

2. **Backtracking Algorithm**:
   - Recursive assignment of time slots and rooms.
   - If conflicts occur, the algorithm backtracks to try alternate options.
   - Heuristics (e.g., most constrained variable first) are used to improve performance.

3. **Optimization Techniques**:
   - Prioritization of courses with the highest constraints.
   - Early backtracking on constraint violation.
   - Use of data structures to track assignments and minimize database lookups.

For a detailed explanation, refer to [Algo.md](Algo.md).


