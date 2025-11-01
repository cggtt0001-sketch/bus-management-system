# Bus Depot Management System

A comprehensive web-based management system for bus depots built with Flask, featuring fleet management, route planning, crew assignment, analytics dashboard, and reporting capabilities.

## Features

### Core Modules

- **Homepage/Dashboard Navigation**: Central hub with navigation cards to all system modules
- **Bus Management**: Full CRUD operations for managing bus fleet (registration, capacity, status, maintenance tracking)
- **Route Management**: Configure routes with start/end points, distances, and stops
- **Schedule Management**: Plan timetables, assign buses to routes with frequency settings
- **Crew Management**: Manage drivers, conductors, and maintenance staff with flexible assignment system
- **Analytics Dashboard**: Real-time statistics with Chart.js visualizations (pie and bar charts)
- **Reports Module**: Generate and export reports in PDF and CSV formats

### Key Capabilities

- ✅ CRUD operations for all entities (Buses, Routes, Schedules, Crew)
- ✅ Flexible crew-to-schedule assignment system
- ✅ Conflict detection (prevent double-booking buses)
- ✅ Visual analytics with interactive charts
- ✅ Export functionality (PDF/CSV) for all reports
- ✅ Responsive Bootstrap 5 UI with color-coded modules
- ✅ Form validation with WTForms
- ✅ Error handling and user-friendly messages

## Technology Stack

- **Backend**: Flask 3.0.0
- **Database**: SQLite with SQLAlchemy ORM
- **Forms**: Flask-WTF with WTForms
- **Frontend**: Bootstrap 5, Chart.js
- **PDF Generation**: ReportLab
- **Architecture**: Flask Blueprints (modular design)

## Project Structure

```
bus-management-system/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # Database models
│   ├── blueprints/              # Modular blueprints
│   │   ├── home/                # Homepage
│   │   ├── buses/               # Bus CRUD
│   │   ├── routes/              # Route CRUD
│   │   ├── schedules/           # Schedule CRUD
│   │   ├── crew/                # Crew Management
│   │   ├── dashboard/           # Analytics
│   │   └── reports/             # Reports & Export
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html            # Base template with navbar
│   │   ├── home/, buses/, routes/, schedules/
│   │   ├── crew/, dashboard/, reports/
│   │   └── errors/              # 404, 500 pages
│   └── static/
│       ├── css/styles.css       # Custom styles
│       └── js/charts.js         # Chart.js initialization
├── config.py                    # Configuration
├── requirements.txt             # Dependencies
└── run.py                       # Application entry point
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd bus-management-system
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
```

### Step 3: Activate Virtual Environment

**On Linux/Mac:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Set Environment Variables (Optional)

```bash
export SECRET_KEY='your-secret-key-here'
```

Or create a `.env` file (recommended for production)

### Step 6: Run the Application

```bash
python run.py
```

The application will be available at: **http://localhost:5000**

The database (`bus_management.db`) will be created automatically on first run.

## Usage Guide

### 1. Homepage

Navigate to the homepage to access all modules through intuitive navigation cards:
- Buses (Green)
- Routes (Yellow)
- Schedules (Blue)
- Crew Management (Orange)
- Dashboard (Teal)
- Reports (Purple)

### 2. Managing Buses

- **Add Bus**: Click "Add New Bus" and fill in registration number, capacity, model, status, purchase date
- **Edit Bus**: Click "Edit" button on any bus row
- **Delete Bus**: Only possible if bus is not assigned to any schedules
- **Status Options**: Active, Inactive, Maintenance

### 3. Managing Routes

- **Add Route**: Define route name, start point, end point, distance, and optional stops
- **Edit Route**: Modify any route details
- **Delete Route**: Only possible if route has no schedules

### 4. Managing Schedules

- **Add Schedule**: Select route and bus, set departure/arrival times, frequency, and active status
- **Frequency Options**: Daily, Weekday, Weekend, Custom
- **Conflict Detection**: System prevents scheduling same bus at overlapping times
- **Assign Crew**: Use "Assign Crew" button to link crew members to schedules

### 5. Crew Management

- **Add Crew Member**: Create crew with unique ID, name, role, contact info, hire date
- **Roles**: Driver, Conductor, Maintenance Staff
- **View Assignments**: Access all crew assignments with detailed schedule information
- **Assign to Schedule**: Link crew members to specific schedules with assignment dates and notes

### 6. Analytics Dashboard

View real-time statistics:
- **Summary Cards**: Total counts for buses, routes, schedules, crew
- **Bus Status**: Active vs Inactive breakdown
- **Pie Chart**: Schedule distribution by frequency
- **Bar Chart**: Route utilization (schedules per route)

### 7. Reports

Generate and export three types of reports:

**Daily Schedules Report**
- View all active schedules with assigned crew
- Export to CSV or PDF

**Crew Assignments Report**
- View all crew-to-schedule assignments
- Export to CSV or PDF

**Route Performance Summary**
- Analyze route utilization and metrics
- Export to CSV or PDF

## Database Schema

### Models

1. **Bus**: registration_number, capacity, model, status, purchase_date
2. **Route**: route_name, start_point, end_point, distance, stops
3. **Schedule**: route_id, bus_id, departure_time, arrival_time, frequency, active
4. **Crew**: crew_id, name, role, contact_info, hire_date
5. **CrewAssignment**: schedule_id, crew_id, assignment_date, notes

### Relationships

- Route → Schedule (One-to-Many)
- Bus → Schedule (One-to-Many)
- Schedule → CrewAssignment (One-to-Many)
- Crew → CrewAssignment (One-to-Many)

## Color Coding

Each module has a distinct color for easy navigation:
- 🟢 **Buses**: Green (#28a745)
- 🟡 **Routes**: Yellow (#ffc107)
- 🔵 **Schedules**: Blue (#007bff)
- 🟠 **Crew**: Orange (#fd7e14)
- 🟦 **Dashboard**: Teal (#20c997)
- 🟣 **Reports**: Purple (#6f42c1)

## Development

### Running in Debug Mode

The application runs in debug mode by default when using `run.py`. Debug mode enables:
- Auto-reload on code changes
- Detailed error messages
- Debug toolbar

### Database Management

The database is automatically created on first run. To reset the database:

```bash
rm bus_management.db
python run.py
```

## Production Deployment

For production deployment, consider:

1. **Change debug mode**: Set `debug=False` in `run.py`
2. **Use production WSGI server**: gunicorn, uWSGI
3. **Strong SECRET_KEY**: Generate and use from environment variable
4. **PostgreSQL**: Replace SQLite for multi-user scenarios
5. **Add authentication**: Implement user login and role-based access control
6. **Enable logging**: Configure proper application logging
7. **Database backups**: Implement regular backup strategy

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing patterns
- All forms have proper validation
- Templates maintain consistent styling
- Test functionality before submitting

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions, please open an issue in the repository.

---

**Built with Flask** | **Powered by SQLAlchemy** | **Styled with Bootstrap 5**
