document.addEventListener('DOMContentLoaded', function() {
    const avatar = document.querySelector('.avatar');
    const zones = document.querySelectorAll('.zone, .zone2'); // Inclure les deux classes
    let currentZone = 0;

    function moveToNextZone() {
        if (currentZone < zones.length) {
            const zone = zones[currentZone];
            const rect = zone.getBoundingClientRect();
            const animationClasses = ['right', 'up', 'down'];
            const nextClass = animationClasses[currentZone % animationClasses.length];

            avatar.className = 'avatar ' + nextClass;

            const avatarWidth = avatar.offsetWidth;
            const avatarHeight = avatar.offsetHeight;

            let newLeft, newTop;

            if (currentZone === 0) {
                // Calculer la position centrée uniquement pour la première zone.
                newLeft = rect.left + (rect.width / 2) - (avatarWidth / 2);
                newTop = rect.top + (rect.height / 2) - (avatarHeight / 2);
            } else {
                // Utiliser les coordonnées de la zone comme telles pour les autres zones.
                newLeft = rect.left;
                newTop = rect.top;
            }

            console.log(`Moving to zone ${currentZone}: (${newLeft}px, ${newTop}px)`);

            avatar.style.transition = 'left 2s linear, top 2s linear';
            avatar.style.left = `${newLeft}px`;
            avatar.style.top = `${newTop}px`;

            setTimeout(() => {
                avatar.classList.remove(nextClass);
                if (zone.id !== 'tools') {
                    avatar.classList.add('work');
                }

                // Déclencher l'animation de la spritesheet uniquement pour la zone #building
                if (zone.id === 'building') {
                    const spritesheet = zone.querySelector('.spritesheet');
                    if (spritesheet) {
                        spritesheet.classList.add('animate');
                        spritesheet.addEventListener('animationend', () => {
                            spritesheet.classList.add('final'); // Ajouter la classe final
                        }, { once: true });
                    }
                }

                setTimeout(() => {
                    if (zone.id !== 'tools') {
                        changeZoneImage(zone);
                        avatar.classList.remove('work');
                    }
                    currentZone++;
                    if (currentZone < zones.length) {
                        setTimeout(moveToNextZone, 0); // Move to the next zone immediately
                    } else {
                        // Retourner à la zone 'tools' et continuer l'animation 'work'
                        const toolsZone = document.querySelector('#tools');
                        const toolsRect = toolsZone.getBoundingClientRect();

                        // Positionner l'avatar au centre de la zone 'tools'
                        const centeredToolsLeft = toolsRect.left + (toolsRect.width / 2) - (avatarWidth / 2);
                        const centeredToolsTop = toolsRect.top + (toolsRect.height / 2) - (avatarHeight / 2);

                        avatar.style.transition = 'left 2s linear, top 2s linear';
                        avatar.style.left = `${centeredToolsLeft}px`;
                        avatar.style.top = `${centeredToolsTop}px`;

                        setTimeout(() => {
                            avatar.classList.add('work');

                            setTimeout(() => {
                                avatar.classList.remove('work');
                                avatar.classList.add('happy');

                                setTimeout(() => {
                                    avatar.classList.remove('happy');
                                    avatar.classList.add('sleep');

                                    setTimeout(() => {
                                        avatar.classList.remove('sleep');
                                        currentZone = 0; // Réinitialiser à la première zone
                                        resetImages(); // Réinitialiser les images à l'état initial
                                        setTimeout(moveToNextZone, 0); // Démarrer le cycle à nouveau immédiatement
                                    }, 5000); // Durée de l'animation 'sleep'
                                }, 4000); // Durée de l'animation 'happy'
                            }, 5000); // Durée de l'animation 'work'
                        }, 2000); // Temps pour revenir à la zone 'tools'
                    }
                }, zone.id === 'tools' ? 0 : 5000); // délai de 5 secondes pour l'animation work.
            }, 2000); // 2-second delay to allow for the movement animation
        }
    }

    function changeZoneImage(zone) {
        const img = zone.querySelector('img');
        const spritesheet = zone.querySelector('.spritesheet');
        if (img) {
            const nextSrc = img.getAttribute('data-next');
            if (zone.id !== 'tools') {
                console.log(`Changing image from ${img.src} to ${nextSrc}`);
                img.src = nextSrc;
            }
        }
        if (spritesheet) {
            spritesheet.classList.add('animate');
        }
    }

    function resetImages() {
        zones.forEach(zone => {
            const img = zone.querySelector('img');
            const spritesheet = zone.querySelector('.spritesheet');
            if (img) {
                const initialSrc = img.getAttribute('data-initial');
                console.log(`Resetting image to ${initialSrc}`);
                img.src = initialSrc;
            }
            if (spritesheet) {
                spritesheet.classList.remove('animate');
                spritesheet.classList.remove('final'); // Enlever la classe final lors de la réinitialisation
            }
        });
    }

    moveToNextZone(); // Start the animation cycle
});
