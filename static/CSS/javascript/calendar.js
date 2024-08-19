document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'fr',  // Configuration pour le format français
        events: rdvData,  // Utilisation des données passées du template HTML
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        selectable: true,
        select: function(info) {
            // Logique pour gérer la sélection de date.
            var selectedDate = info.startStr;
            alert('Date sélectionnée : ' + formatDateToFrench(selectedDate));

            // Ouvrir une modale pour ajouter un rendez-vous à cette date.
            openModalForDate(selectedDate);
        },
        eventTimeFormat: { // Personnalisation de l'affichage de l'heure.
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
        },
        eventClick: function(info) {
            // Logique pour gérer le clic sur un événement.
            var eventTitle = info.event.title;
            var eventDate = info.event.start.toISOString().slice(0, 10);
            var eventTime = info.event.start.toISOString().slice(11, 16);
            alert('Rendez-vous avec ' + eventTitle + ' le ' + formatDateToFrench(eventDate) + ' à ' + eventTime);

            // Ouvrir une modale pour afficher les détails ou proposer des actions.
            openModalForEvent(info.event);
        }
    });

    calendar.render();

    // Fonction pour formater la date en format français
    function formatDateToFrench(dateStr) {
        var options = { year: 'numeric', month: 'long', day: 'numeric' };
        var date = new Date(dateStr);
        return date.toLocaleDateString('fr-FR', options);
    }

    // Fonction pour ouvrir une modale lors de la sélection d'une date.
    function openModalForDate(date) {
        // Implémentation de la logique pour afficher un formulaire ou une modale ici.
        console.log('Ouverture de la modale pour la date : ' + formatDateToFrench(date));
        // Utilisez un framework comme Bootstrap pour gérer les modales
        $('#yourModalId').modal('show');
    }

    // Fonction d'exemple pour ouvrir une modale lors du clic sur un événement
    function openModalForEvent(event) {
        // Implémentation de la logique pour afficher les détails de l'événement ou modifier/supprimer
        console.log('Ouverture de la modale pour l\'événement : ' + event.title);
        // Afficher une modale avec les détails de l'événement
        $('#yourModalId').modal('show');
    }
});