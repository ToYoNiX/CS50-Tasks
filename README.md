# CS50 Tasks
CS50 Tasks is a task management application created with simplicity and maintainability in mind. Its purpose is to help users efficiently manage their daily, overdue, and recurring tasks, with features for adding, editing, and tracking task progress over time.

## Video URL
https://youtu.be/axKCVicUna0

## Tools
- **Flask**: The backend framework used for handling server requests and processing data.
- **HTML**, **CSS**, **JavaScript**: These are used to build the frontend, with **Bootstrap** for styling and responsive design.
- **SQLite**: A lightweight database used to store tasks, user information, and recurring task schedules.

## Web Design
The application comprises eight main pages, each tailored to a specific task management function:
1. **Add**
2. **Today**
3. **Overdue**
4. **Recurring**
5. **History**
6. **Info**
7. **Register**
8. **Login**

### Add Webpage
The "Add" page allows users to create new tasks. It is a form-based page where users can input the task name, description, and select its priority from High, Normal, or Low. Additionally, a checkbox is available for marking the task as recurring.

By default, the recurring checkbox is unchecked, and users only need to select a single date, indicating that the task is a one-time event. If the recurring checkbox is selected, the form expands to include fields for the start date, end date, and a list of weekdays to specify when the task should recur.

Once the form is submitted, the data is sent to the Flask backend, which processes the information and stores it in the SQLite database. This page also functions as an editor for existing tasks, as described in the "Today" section below.

### Today
The "Today" page displays all tasks scheduled for the current day by querying the database. Each task listed comes with three action buttons:
- **Check**: Marks the task as completed.
- **Delete**: Permanently removes the task from the database.
- **Edit**: Opens the task in the "Add" form, allowing users to modify the details.

The tasks are displayed in order of priority, with High-priority tasks listed first. The design ensures that the most important tasks are always at the top, making it easier to manage what's urgent.

### Overdue
The "Overdue" page lists tasks that were supposed to be completed before today. In addition to listing overdue tasks, this page includes two important features:

- **Sorting**: Tasks can be sorted by either their due date or priority.
- **Rescheduling**: Users can move overdue tasks to today's list, and when this action is taken, the task's priority is automatically updated to "High" to indicate its urgency.

This page provides an effective way to stay on top of any missed tasks and ensure that nothing falls through the cracks.

### Recurring
The "Recurring" page is dedicated to managing recurring tasks. It lists all tasks that are set to repeat on a scheduled basis, allowing users to edit or delete them just as they would on the "Today" page. This feature ensures flexibility in handling long-term tasks that span across multiple dates.

### History
The "History" page serves as a record of all completed and pending tasks. Users can query tasks by specifying a date, allowing them to review tasks they have worked on in the past or view the status of tasks from a previous day. The page also shows whether each task was completed or not, providing a detailed history of task progress.

### Info
The "Info" page is a simple page that provides general information about the application and its purpose. It's a straightforward page designed to explain the features and functionalities of CS50 Tasks.

### Register and Login
In addition to the main task management pages, the app includes **Register** and **Login** pages to manage user authentication. Each user can register for an account and log in to view and manage their own tasks, ensuring that task data is personalized and secure.

## Backend
The backend of CS50 Tasks is powered by Flask, a lightweight Python web framework. The inspiration for this project came from the CS50x finance problem set, which served as a foundation for building out the app. However, the app has been significantly expanded beyond the original scope, with new features added to meet the needs of a full task management system.

In `app.py`, you can explore how the backend handles routing, user authentication, form submissions, and database queries. While the backend may not be the most polished in terms of design, it is functional and represents my first complete full-stack web application.
## Database
The database schema is relatively simple and consists of three main tables: `users`, `tasks`, and `recurrence`.
- **users**: Stores user information such as usernames and passwords, allowing for user registration and login.
- **tasks**: Contains the details of each task, including the task name, description, priority, due date, and user ID (to associate tasks with a specific user).
- **recurrence**: Handles recurring tasks. Since a task can have multiple recurring days (e.g., every Monday and Wednesday), there is a one-to-many relationship between `tasks` and `recurrence`.

This relational structure ensures that tasks can be managed efficiently, and recurring tasks can be tracked over time. You can explore the full database schema in the `schema.sql` file.
