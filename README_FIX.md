# 🚌 Bus Depot Management System - Database Fix

## Issue: "no such column: buses.location_lat" Error

If you're encountering this error when trying to access the Live Map feature, it means your existing database doesn't have the new GPS location fields that were added in the recent update.

## 🔧 Quick Fix

### Option 1: Automated Fix (Recommended)
Run the database fix tool:

```bash
python fix_database.py
```

This tool will:
- ✅ Find your existing database
- ✅ Add missing GPS location columns
- ✅ Create the working_hours table
- ✅ Add sample data if needed
- ✅ Verify everything works

### Option 2: Manual Fix
If the automated tool doesn't work, you can manually update your database:

```bash
# Create a fresh database with all features
python setup_database.py
```

## 🗺️ After Fixing

Once the database is fixed, you can access all new features:

- **Live Map**: http://localhost:5000/dashboard/map
- **Enhanced Crew**: http://localhost:5000/crew/enhanced
- **Smart Bus Creation**: http://localhost:5000/buses/create
- **Active Buses by Route**: http://localhost:5000/buses/active-by-route

## 🚀 Run the Application

```bash
python run.py
```

## 📋 New Features Added

### 🗺️ Live Map Dashboard
- Real-time bus tracking with GPS coordinates
- Interactive map with bus markers
- Click markers for bus details
- Driver information modals
- Refresh and center controls

### 👥 Enhanced Crew Management
- Role-based filtering (Drivers, Conductors, Maintenance)
- Search by name
- Working hours tracking
- Assignment status display

### 🚌 Smart Bus Creation
- Assign routes during bus creation
- Assign drivers and conductors
- Automatic schedule creation
- Assignment preview

### 📊 Route-Based Views
- View active buses by route
- Filter buses by specific routes
- Complete crew assignment details

## 🔍 Troubleshooting

### Still Getting Database Errors?
1. Delete your old database file (`bus_depot.db`)
2. Run `python setup_database.py` to create a fresh database
3. Start the application with `python run.py`

### Flask Import Errors?
Make sure you have the required dependencies:

```bash
pip install -r requirements.txt
```

### Database Not Found?
The fix tool searches for databases in these locations:
- `bus_depot.db`
- `instance/bus_depot.db`
- `app.db`
- `database.db`

## 🎯 What the Fix Does

The database fix adds these new features:

1. **GPS Tracking Fields** to the buses table:
   - `location_lat` - Latitude for map display
   - `location_lng` - Longitude for map display
   - `last_location_update` - When GPS was last updated

2. **Working Hours Table** for crew tracking:
   - Tracks hours worked per crew member
   - Links to schedules and assignments
   - Includes 150 sample records

3. **Sample Data** for testing:
   - 5 buses with GPS coordinates
   - 4 routes with distances
   - 5 crew members
   - 4 schedules with assignments

## 🆘 Need Help?

If you continue to experience issues:

1. Check that you're running the fix script from the correct directory
2. Ensure you have write permissions in the project folder
3. Try creating a completely fresh database by deleting old files first

The system is designed to be robust and should handle most database configurations automatically!