document.addEventListener('DOMContentLoaded', function() {
    const avatar = document.querySelector('.avatar');
    const zones = document.querySelectorAll('.zone, .zone2');
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

            // Calculer les positions avec correction pour le défilement et de la zone.
            if (zone.id === 'gardening') {
                // Centrer l'avatar dans la zone gardening
                newLeft = rect.left + window.pageXOffset - avatar.parentElement.offsetLeft + avatarWidth;
                newTop = rect.top + window.pageYOffset - avatar.parentElement.offsetTop + (rect.height / 2) + (avatarHeight / 2);
            } else if (zone.id === 'building' || zone.id === 'mechanic') {
                // Positionner l'avatar en bas de la zone
                newLeft = rect.left + window.pageXOffset - avatar.parentElement.offsetLeft;
                newTop = rect.bottom + window.pageYOffset - avatar.parentElement.offsetTop - rect.height + (avatarHeight / 2);
            } else if (zone.id === 'tools') {
                // Positionner l'avatar en bas de la zone tools
                newLeft = rect.left + window.pageXOffset - avatar.parentElement.offsetLeft + (rect.width / 2) - avatarWidth;
                newTop = rect.bottom + window.pageYOffset - avatar.parentElement.offsetTop - avatarHeight;
            }

            // Utilisation de GSAP pour animer l'avatar.
            gsap.to(avatar, {
                duration: 2,
                left: newLeft,
                top: newTop,
                ease: "power1.out",
                onComplete: () => {
                    avatar.classList.remove(nextClass);
                    if (zone.id !== 'tools') {
                        avatar.classList.add('work');
                    }

                    if (zone.id === 'building') {
                        const spritesheet = zone.querySelector('.spritesheet');
                        if (spritesheet) {
                            spritesheet.classList.add('animate');
                            spritesheet.addEventListener('animationend', () => {
                                spritesheet.classList.add('final');
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
                            setTimeout(moveToNextZone, 0);
                        } else {
                            // Retourner à la zone 'tools'
                            const toolsZone = document.querySelector('#tools');
                            const toolsRect = toolsZone.getBoundingClientRect();

                            const centeredToolsLeft = rect.left + window.pageXOffset - avatar.parentElement.offsetLeft + (rect.width / 2) - avatarWidth;
                            const centeredToolsTop = rect.bottom + window.pageYOffset - avatar.parentElement.offsetTop - avatarHeight;

                            gsap.to(avatar, {
                                duration: 0,
                                left: centeredToolsLeft,
                                top: centeredToolsTop,
                                ease: "power1.out",
                                onComplete: () => {
                                    avatar.classList.add('work');

                                    setTimeout(() => {
                                        avatar.classList.remove('work');
                                        avatar.classList.add('happy');

                                        setTimeout(() => {
                                            avatar.classList.remove('happy');
                                            avatar.classList.add('sleep');

                                            setTimeout(() => {
                                                avatar.classList.remove('sleep');
                                                currentZone = 0;
                                                resetImages();
                                                setTimeout(moveToNextZone, 0);
                                            }, 5000); // Durée de l'animation 'sleep'
                                        }, 4000); // Durée de l'animation 'happy'
                                    }, 5000); // Durée de l'animation 'work'
                                }
                            });
                        }
                    }, zone.id === 'tools' ? 0 : 5000);
                }
            });
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
                spritesheet.classList.remove('final');
            }
        });
    }

    moveToNextZone(); // Start the animation cycle
});
