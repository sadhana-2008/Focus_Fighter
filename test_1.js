
        const profileOverlay = document.getElementById('profile-overlay');
        const fsLobby = document.getElementById('fullscreen-lobby');
        const mainMenu = document.getElementById('main-menu');
        const profileBtnTop = document.querySelector('.profile-btn');
        const fsCodeSlots = document.getElementById('fs-code-slots');

        // Initial setup for code slots DOM
        const rollChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        const initialCode = "AX72-P";

        initialCode.split('').forEach((char, index) => {
            if (char === '-') {
                const dash = document.createElement('div');
                dash.className = 'dash-char';
                dash.innerText = '-';
                fsCodeSlots.appendChild(dash);
            } else {
                const slot = document.createElement('div');
                slot.className = 'slot';

                const inner = document.createElement('div');
                inner.className = 'slot-inner';

                const spinCount = 15 + (index * 4);
                for (let i = 0; i < spinCount; i++) {
                    const randomChar = document.createElement('div');
                    randomChar.className = 'char text-white/40';
                    randomChar.innerText = rollChars.charAt(Math.floor(Math.random() * rollChars.length));
                    inner.appendChild(randomChar);
                }

                const finalCharDOM = document.createElement('div');
                finalCharDOM.className = 'char final-char';
                finalCharDOM.innerText = char;
                inner.appendChild(finalCharDOM);

                slot.appendChild(inner);
                fsCodeSlots.appendChild(slot);
            }
        });

        const slotInners = document.querySelectorAll('#fs-code-slots .slot-inner');

        function toggleUI(screenID) {
            // Unify Logic Guard
            // Hide everything first cleanly
            profileOverlay.classList.add('hidden');
            profileOverlay.style.display = 'none';

            gsap.killTweensOf(fsLobby);
            fsLobby.classList.remove('active');
            fsLobby.style.opacity = '0';

            mainMenu.style.opacity = '0';
            mainMenu.style.pointerEvents = 'none';
            profileBtnTop.style.opacity = '0';
            profileBtnTop.style.pointerEvents = 'none';

            if (screenID === 'profile') {
                profileOverlay.classList.remove('hidden');
                profileOverlay.style.display = 'flex';

                // GSAP Fallback
                gsap.killTweensOf('.char-card');
                gsap.set('.char-card', { opacity: 1 });

                gsap.fromTo('.char-card',
                    { y: 40, opacity: 0 },
                    { y: 0, opacity: 1, stagger: 0.1, duration: 0.8, ease: 'back.out(1.5)', clearProps: 'transform' }
                );
            } else if (screenID === 'lobby') {
                fsLobby.classList.add('active');
                gsap.to(fsLobby, { opacity: 1, duration: 0.5 });

                // Live Code Generation
                let generatedCode = '';
                for (let i = 0; i < 5; i++) {
                    generatedCode += rollChars.charAt(Math.floor(Math.random() * rollChars.length));
                }
                generatedCode = generatedCode.substring(0, 2) + '-' + generatedCode.substring(2);

                // Update DOM final slots
                const newChars = generatedCode.split('').filter(c => c !== '-');
                document.querySelectorAll('.final-char').forEach((el, index) => {
                    if (newChars[index]) {
                        el.innerText = newChars[index];
                    }
                    el.classList.remove('heavy-glow');
                });

                // Reset and run GSAP Spinner
                gsap.set(slotInners, { y: 0 });
                slotInners.forEach((inner, index) => {
                    const totalElements = inner.children.length;
                    const distance = -((totalElements - 1) * 90);

                    gsap.to(inner, {
                        y: distance,
                        duration: 1.5 + (index * 0.2), // Base 1.5s
                        ease: "power4.inOut",
                        onComplete: () => {
                            const finalChar = inner.querySelector('.final-char');
                            if (finalChar) {
                                finalChar.classList.add('heavy-glow');
                            }
                        }
                    });
                });

                // Fade components
                gsap.fromTo('.pomodoro-panel', { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.8, delay: 0.5, ease: "power2.out" });
                gsap.fromTo('.footer-btn', { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, stagger: 0.1, delay: 0.8 });
                gsap.fromTo('.player-slot-card', { scale: 0.8, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.4, stagger: 0.1, delay: 0.6, ease: "back.out(1.5)" });

            } else if (screenID === 'menu') {
                mainMenu.style.opacity = '1';
                mainMenu.style.pointerEvents = 'auto';
                profileBtnTop.style.opacity = '1';
                profileBtnTop.style.pointerEvents = 'auto';
            }
        }

        // Hover & Click Logic
        const cards = document.querySelectorAll('.char-card');

        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                if (!card.classList.contains('selected-card')) {
                    gsap.to(card, { scale: 1.05, duration: 0.3, ease: 'power2.out' });
                    const img = card.querySelector('img');
                    if (img) img.style.filter = 'drop-shadow(0 0 25px rgba(255, 255, 255, 0.8))';
                    card.style.textShadow = '0 0 15px white';

                    const sText = card.querySelector('.select-text');
                    if (sText) {
                        sText.classList.remove('opacity-0', 'text-white/50');
                        sText.classList.add('opacity-100', 'text-white');
                    }
                }
            });

            card.addEventListener('mouseleave', () => {
                if (!card.classList.contains('selected-card')) {
                    gsap.to(card, { scale: 1, duration: 0.3, ease: 'power2.out' });
                    const img = card.querySelector('img');
                    if (img) img.style.filter = 'drop-shadow(0 0 15px rgba(255, 255, 255, 0.3))';
                    card.style.textShadow = 'none';
                    const sText = card.querySelector('.select-text');
                    if (sText) {
                        sText.classList.remove('opacity-100', 'text-white');
                        sText.classList.add('opacity-0', 'text-white/50');
                    }
                }
            });

            card.addEventListener('click', (e) => {
                e.stopPropagation();

                // Clear others
                cards.forEach(c => {
                    c.classList.remove('selected-card');
                    gsap.to(c, { scale: 1, duration: 0.3 });
                    const img = c.querySelector('img');
                    if (img) img.style.filter = 'drop-shadow(0 0 15px rgba(255, 255, 255, 0.3))';
                    c.style.textShadow = 'none';

                    const cText = c.querySelector('.select-text');
                    if (cText) {
                        cText.innerText = 'CLICK TO SELECT';
                        cText.classList.remove('opacity-100', 'text-white');
                        cText.classList.add('opacity-0', 'text-white/50');
                    }
                });

                // Set selected state & Memory
                card.classList.add('selected-card');
                const img = card.querySelector('img');
                if (img) img.style.filter = 'drop-shadow(0 0 30px rgba(255, 255, 255, 1))';
                card.style.textShadow = '0 0 20px white';
                const sText = card.querySelector('.select-text');
                if (sText) {
                    sText.innerText = 'SELECTED';
                    sText.classList.remove('opacity-0', 'text-white/50');
                    sText.classList.add('opacity-100', 'text-white');
                }

                // Save Character Selection internally
                const charImgSrc = card.querySelector('img').src;
                // Extract 'charX.png'
                const charName = charImgSrc.substring(charImgSrc.lastIndexOf('/') + 1);
                localStorage.setItem('selectedChar', charName);

                // Instantly update Lobby host slot without reloading
                const hostAvatar = document.getElementById('host-avatar');
                if (hostAvatar) {
                    hostAvatar.src = '/static/characters/' + charName;
                }

                // Click Bounce
                gsap.fromTo(card,
                    { scale: 0.95 },
                    { scale: 1.08, ease: 'elastic.out(1, 0.4)', duration: 0.6 }
                );
            });
        });

        // Toggle Pixel-Logic
        function toggleBreaks() {
            const tgl = document.getElementById('breaks-toggle');
            const icon = document.getElementById('breaks-icon');
            const breakPanel = document.getElementById('break-timer-panel');

            if (tgl.classList.contains('active')) {
                tgl.classList.remove('active');
                icon.className = "ph ph-x-circle";
                gsap.fromTo(tgl, { scale: 0.9 }, { scale: 1, duration: 0.5, ease: "elastic.out(1,0.5)" });

                // Hide Break Timer & Reset
                gsap.to(breakPanel, {
                    height: 0,
                    opacity: 0,
                    marginTop: 0,
                    duration: 0.4,
                    ease: "power2.in",
                    onComplete: () => {
                        breakPanel.style.display = 'none';
                        document.getElementById('break-min').innerText = '05';
                        document.getElementById('break-sec').innerText = '00';
                    }
                });
            } else {
                tgl.classList.add('active');
                icon.className = "ph ph-check-circle";
                gsap.fromTo(tgl, { scale: 0.9 }, { scale: 1, duration: 0.5, ease: "elastic.out(1,0.5)" });

                // Show Break Timer
                breakPanel.style.display = 'flex';
                gsap.fromTo(breakPanel,
                    { height: 0, opacity: 0, marginTop: -20 },
                    { height: 'auto', opacity: 1, marginTop: 0, duration: 0.5, ease: "back.out(1.2)" }
                );
            }
        }

        // Jitter Animation for Timer Controls
        document.querySelectorAll('.timer-ctrl').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const targetNum = btn.parentNode.querySelector('.pomo-num');
                if (targetNum) {
                    gsap.fromTo(targetNum,
                        { scale: 1.2 },
                        { scale: 1, duration: 0.2, ease: "bounce.out" }
                    );
                }
            });
        });

        // Elite Logic: Timer Adjusment
        function adjustTime(elementId, amount) {
            const el = document.getElementById(elementId);
            let current = parseInt(el.innerText);
            let newTime = current + amount;

            if (newTime < 5) newTime = 5;
            if (newTime > 60) newTime = 60;

            el.innerText = newTime < 10 ? '0' + newTime : newTime;
        }

        // Elite Logic: Seconds Adjustment
        function adjustSeconds(minId, secId, amount) {
            const secEl = document.getElementById(secId);
            const minEl = document.getElementById(minId);
            let secCurrent = parseInt(secEl.innerText);
            let minCurrent = parseInt(minEl.innerText);

            let newSec = secCurrent + amount;

            if (newSec >= 60) {
                newSec -= 60;
                adjustTime(minId, 1);
            } else if (newSec < 0) {
                // Check if min is > 5 to allow subtraction
                if (minCurrent >= 5) {
                    if (minCurrent === 5 && newSec < 0) {
                        newSec = 0; // Don't let it go below 5:00
                    } else {
                        newSec = 60 + newSec;
                        minEl.innerText = (minCurrent - 1) < 10 ? '0' + (minCurrent - 1) : (minCurrent - 1);
                    }
                } else {
                    newSec = 0;
                }
            }

            secEl.innerText = newSec === 0 ? '00' : newSec;

            // Re-apply jitter to the seconds element
            gsap.fromTo(secEl,
                { scale: 1.2 },
                { scale: 1, duration: 0.2, ease: "bounce.out" }
            );
        }

        // Elite Logic: Copy Code
        function copyRoomCode() {
            // Grab the current characters from the DOM code slots
            let currentCode = '';
            const slotElements = document.getElementById('fs-code-slots').children;
            for (let el of slotElements) {
                if (el.classList.contains('dash-char')) {
                    currentCode += '-';
                } else {
                    const finalChar = el.querySelector('.final-char');
                    if (finalChar) currentCode += finalChar.innerText;
                }
            }

            // Secure Clipboard Logic with Hidden Input Fallback
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(currentCode).catch(() => fallbackCopy(currentCode));
            } else {
                fallbackCopy(currentCode);
            }

            function fallbackCopy(text) {
                const hiddenInput = document.createElement("input");
                hiddenInput.value = text;
                hiddenInput.style.position = "absolute";
                hiddenInput.style.opacity = "0";
                document.body.appendChild(hiddenInput);
                hiddenInput.select();
                try {
                    document.execCommand("copy");
                } catch (err) { }
                document.body.removeChild(hiddenInput);
            }

            const copyBtn = document.getElementById('copy-btn');
            const copyText = document.getElementById('copy-text');
            const codeSlots = document.getElementById('fs-code-slots');

            copyText.innerText = "COPIED! ✨";
            copyBtn.classList.add('primary-glow');

            // Button Flash (White Neon Glow to Border)
            gsap.fromTo(copyBtn,
                { scale: 1.1, backgroundColor: 'rgba(255,255,255,0.3)', borderColor: '#ffffff', boxShadow: '0 0 20px white' },
                { scale: 1, backgroundColor: 'rgba(20, 20, 20, 0.6)', borderColor: 'rgba(255,255,255,0.2)', boxShadow: '0 0 0px transparent', duration: 0.5 }
            );

            // Slots Neon "Photo" Flash
            gsap.fromTo(codeSlots,
                { filter: "brightness(2) drop-shadow(0 0 40px white)" },
                { filter: "brightness(1) drop-shadow(0 0 0px transparent)", duration: 0.8, ease: "power2.out" }
            );

            setTimeout(() => {
                copyText.innerText = "COPY CODE";
                copyBtn.classList.remove('primary-glow');
            }, 2000);
        }

        // Elite Logic: Bulletproof Character Sync
        function initCharacterSync() {
            const savedChar = localStorage.getItem('selectedChar') || 'char1.png';
            const charFallback = savedChar.includes('.png') ? savedChar : `char${savedChar}.png`;

            // Apply selected styling to the correct card in profile menu
            const cardsNodes = document.querySelectorAll('.char-card');
            cardsNodes.forEach(c => {
                if (c.getAttribute('data-char') === charFallback) {
                    c.classList.add('selected-card');
                    const img = c.querySelector('img');
                    if (img) img.style.filter = 'drop-shadow(0 0 30px rgba(255, 255, 255, 1))';
                    c.style.textShadow = '0 0 20px white';
                    const sText = c.querySelector('.select-text');
                    if (sText) {
                        sText.innerText = 'SELECTED';
                        sText.classList.remove('opacity-0', 'text-white/50');
                        sText.classList.add('opacity-100', 'text-white');
                    }
                }
            });

            // Update main lobby
            const hostAvatar = document.getElementById('host-avatar');
            const hostSlot = document.getElementById('host-player-slot');

            if (hostAvatar) {
                hostAvatar.src = '/static/characters/' + charFallback;
            }
            if (hostSlot) {
                hostSlot.style.filter = "drop-shadow(0 0 12px white)";
                hostSlot.classList.add('host-glow');
            }
        }

        document.addEventListener('DOMContentLoaded', initCharacterSync);
    