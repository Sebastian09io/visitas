document.addEventListener('DOMContentLoaded', function() {
    const monthNames = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ];

    const daysOfWeek = ["D", "L", "M", "M", "J", "V", "S"];

    const calendarContainer = document.getElementById('calendar-container');
    const yearElement = document.getElementById('year');

    const year = new Date().getFullYear();
    const today = new Date();

    yearElement.innerText = year;

    for (let month = 0; month < 12; month++) {
        const monthDiv = document.createElement('div');
        monthDiv.className = 'month';

        const monthHeader = document.createElement('div');
        monthHeader.className = 'month-header';
        monthHeader.innerText = monthNames[month]; // Nombres de meses en minúsculas
        monthDiv.appendChild(monthHeader);

        const monthTable = document.createElement('table');
        monthTable.className = 'month-table';

        const thead = document.createElement('thead');
        const tr = document.createElement('tr');

        daysOfWeek.forEach(day => {
            const th = document.createElement('th');
            th.innerText = day;
            tr.appendChild(th);
        });

        thead.appendChild(tr);
        monthTable.appendChild(thead);

        const tbody = document.createElement('tbody');
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        let row = document.createElement('tr');
        for (let i = 0; i < firstDay; i++) {
            const cell = document.createElement('td');
            row.appendChild(cell);
        }

        for (let day = 1; day <= daysInMonth; day++) {
            if (row.children.length === 7) {
                tbody.appendChild(row);
                row = document.createElement('tr');
            }
            const cell = document.createElement('td');
            cell.innerText = day;
            const dayOfWeek = (firstDay + day - 1) % 7;
            if (dayOfWeek === 0 || dayOfWeek === 6) {
                cell.classList.add('weekend');
            } else {
                cell.classList.add('weekday');
            }
            if (year === today.getFullYear() && month === today.getMonth() && day === today.getDate()) {
                cell.classList.add('today');
            }
            cell.addEventListener('click', function() {
                // Abrir el modal al hacer clic en un día
                $('#reservaModal').modal('show');
                // Configurar fecha de inicio en el formulario
                const fechaInicio = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}T09:00`;
                const fechaFin = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}T18:00`;
                document.getElementById('fecha_inicio').value = fechaInicio;
                document.getElementById('fecha_fin').value = fechaFin;
            });
            row.appendChild(cell);
        }

        while (row.children.length < 7) {
            const cell = document.createElement('td');
            row.appendChild(cell);
        }

        tbody.appendChild(row);
        monthTable.appendChild(tbody);

        monthDiv.appendChild(monthTable);
        calendarContainer.appendChild(monthDiv);
    }

    document.getElementById('submitReserva').addEventListener('click', function() {
        const form = document.getElementById('reservaForm');
        const formData = new FormData(form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('/gestion_reserva/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Reserva realizada con éxito.');
                $('#reservaModal').modal('hide');
            } else {
                alert('Error: ' + data.error);
            }
        });
    });

});
