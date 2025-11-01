// Modal handling for Schedule, Bus, and Route forms

document.addEventListener('DOMContentLoaded', function() {
    // Schedule Modal Handlers
    const addScheduleBtn = document.getElementById('addScheduleBtn');
    const scheduleModal = document.getElementById('scheduleModal');
    const scheduleForm = document.getElementById('scheduleForm');
    const editScheduleBtns = document.querySelectorAll('.edit-schedule-btn');

    if (addScheduleBtn && scheduleModal) {
        const modal = new bootstrap.Modal(scheduleModal);

        // Add Schedule button click
        addScheduleBtn.addEventListener('click', function() {
            document.getElementById('modalTitle').textContent = 'Add Schedule';
            scheduleForm.action = '/schedule/create';
            scheduleForm.reset();
            modal.show();
        });

        // Edit Schedule button clicks
        editScheduleBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.dataset.id;
                const busId = this.dataset.busId;
                const routeId = this.dataset.routeId;
                const departure = this.dataset.departure;
                const arrival = this.dataset.arrival;

                document.getElementById('modalTitle').textContent = 'Edit Schedule';
                scheduleForm.action = `/schedule/update/${id}`;
                document.getElementById('bus_id').value = busId;
                document.getElementById('route_id').value = routeId;
                document.getElementById('departure_time').value = departure;
                document.getElementById('arrival_time').value = arrival;
                modal.show();
            });
        });
    }

    // Bus Modal Handlers
    const addBusBtn = document.getElementById('addBusBtn');
    const busModal = document.getElementById('busModal');
    const busForm = document.getElementById('busForm');
    const editBusBtns = document.querySelectorAll('.edit-bus-btn');

    if (addBusBtn && busModal) {
        const modal = new bootstrap.Modal(busModal);

        // Add Bus button click
        addBusBtn.addEventListener('click', function() {
            document.getElementById('modalTitle').textContent = 'Add Bus';
            busForm.action = '/bus/create';
            busForm.reset();
            modal.show();
        });

        // Edit Bus button clicks
        editBusBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.dataset.id;
                const busNumber = this.dataset.busNumber;

                document.getElementById('modalTitle').textContent = 'Edit Bus';
                busForm.action = `/bus/update/${id}`;
                document.getElementById('bus_number').value = busNumber;
                modal.show();
            });
        });
    }

    // Route Modal Handlers
    const addRouteBtn = document.getElementById('addRouteBtn');
    const routeModal = document.getElementById('routeModal');
    const routeForm = document.getElementById('routeForm');
    const editRouteBtns = document.querySelectorAll('.edit-route-btn');

    if (addRouteBtn && routeModal) {
        const modal = new bootstrap.Modal(routeModal);

        // Add Route button click
        addRouteBtn.addEventListener('click', function() {
            document.getElementById('modalTitle').textContent = 'Add Route';
            routeForm.action = '/route/create';
            routeForm.reset();
            modal.show();
        });

        // Edit Route button clicks
        editRouteBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.dataset.id;
                const routeName = this.dataset.routeName;
                const startLocation = this.dataset.startLocation;
                const endLocation = this.dataset.endLocation;
                const distance = this.dataset.distance;

                document.getElementById('modalTitle').textContent = 'Edit Route';
                routeForm.action = `/route/update/${id}`;
                document.getElementById('route_name').value = routeName;
                document.getElementById('start_location').value = startLocation;
                document.getElementById('end_location').value = endLocation;
                document.getElementById('distance').value = distance;
                modal.show();
            });
        });
    }
});
