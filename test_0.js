
                    // Generate exactly 8 cards
                    for (let i = 1; i <= 8; i++) {
                        document.write(`
                        <div class="char-card w-[240px] h-[360px] shrink-0 relative flex flex-col items-center justify-end overflow-visible cursor-pointer" 
                             style="scroll-snap-align: center; background: transparent; border: none; opacity: 1;" data-char="char${i}.png">
                            <img src="/static/characters/char${i}.png" class="absolute inset-x-0 bottom-12 w-full h-[120%] object-contain pointer-events-none drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]">
                            <span class="select-text absolute bottom-2 text-[10px] text-white/50 opacity-0 transition-opacity duration-300 pointer-events-none" style="font-family: 'Press Start 2P', monospace;">CLICK TO SELECT</span>
                        </div>
                    `);
                    }
                