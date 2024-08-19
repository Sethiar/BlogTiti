document.getElementById('toggleSize').addEventListener('click', function() {
    var localContainer = document.getElementById('localContainer');
    var remoteContainer = document.getElementById('remoteContainer');

    if (localContainer.style.width === '100%') {
        localContainer.style.width = '20%';
        localContainer.style.height = 'auto';
        remoteContainer.style.width = '80%';
        remoteContainer.style.height = '80%';
    } else {
        localContainer.style.width = '100%';
        localContainer.style.height = '100%';
        remoteContainer.style.width = '20%';
        remoteContainer.style.height = '20%';
    }
});