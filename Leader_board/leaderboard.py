import json

def render_leaderboard(players_data):
    """
    Generates a premium AAA 'Pantheon of Champions' Leaderboard UI.
    Features:
    - Top 3 Podium (centerpiece)
    - Hall of Warriors (rank 4+ horizontal list)
    - Global Stats section
    - Dark maroon / Neon aesthetic
    """
    
    # Sort by calculated score DESC
    for p in players_data:
        p['score'] = int(sum(p['stats'].values()) / len(p['stats']) * 10)
    
    sorted_players = sorted(players_data, key=lambda x: x['score'], reverse=True)
    json_payload = json.dumps(sorted_players)

    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pantheon of Champions - Leaderboard</title>
    
    <!-- Dependencies -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://unpkg.com/framer-motion@10.16.4/dist/framer-motion.js"></script>

    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&display=swap" rel="stylesheet">

    <style>
        :root {
            --pantheon-red: #4a0404;
            --pantheon-maroon: #2d0202;
            --gold-glow: #fbbf24;
            --silver-glow: #94a3b8;
            --bronze-glow: #b45309;
            --neon-blue: #00f2ff;
        }

        body, html {
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, var(--pantheon-maroon), var(--pantheon-red));
            background-attachment: fixed;
            color: #fff;
            font-family: 'Rajdhani', sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
            overflow-y: auto;
        }

        .orbitron { font-family: 'Orbitron', sans-serif; }
        
        .glass-card {
            background: rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
        }

        .podium-card {
            position: relative;
            transition: transform 0.3s;
        }

        .podium-card:hover { transform: translateY(-10px); }

        .rank-1 { border: 2px solid var(--gold-glow); box-shadow: 0 0 40px rgba(251, 191, 36, 0.3), inset 0 0 20px rgba(251, 191, 36, 0.1); }
        .rank-2 { border: 2px solid var(--silver-glow); box-shadow: 0 0 30px rgba(148, 163, 184, 0.3); }
        .rank-3 { border: 2px solid var(--bronze-glow); box-shadow: 0 0 30px rgba(180, 83, 9, 0.3); }

        .crown-icon {
            position: absolute;
            top: -30px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 48px;
            color: var(--gold-glow);
            filter: drop-shadow(0 0 10px var(--gold-glow));
        }

        .warrior-row {
            background: linear-gradient(90deg, rgba(255, 255, 255, 0.05), transparent);
            border-left: 4px solid var(--neon-blue);
            transition: all 0.2s;
        }

        .warrior-row:hover {
            background: linear-gradient(90deg, rgba(255, 255, 255, 0.1), rgba(0, 242, 255, 0.05));
            transform: translateX(10px);
        }

        .diagonal-stripes {
            background-image: repeating-linear-gradient(
                45deg,
                transparent,
                transparent 10px,
                rgba(255, 255, 255, 0.02) 10px,
                rgba(255, 255, 255, 0.02) 20px
            );
        }

        /* Responsive Podium */
        .podium-grid {
            display: grid;
            grid-template-columns: 1fr 1.2fr 1fr;
            align-items: flex-end;
            gap: 20px;
        }

        @media (max-width: 768px) {
            .podium-grid {
                grid-template-columns: 1fr;
                gap: 40px;
            }
            .rank-1 { order: -1; }
        }

        ::-webkit-scrollbar { width: 10px; }
        ::-webkit-scrollbar-track { background: var(--pantheon-maroon); }
        ::-webkit-scrollbar-thumb { background: var(--pantheon-red); border-radius: 5px; border: 2px solid var(--pantheon-maroon); }
        ::-webkit-scrollbar-thumb:hover { background: #600; }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { motion, AnimatePresence } = window.FramerMotion || window.Motion || { motion: "div", AnimatePresence: React.Fragment };

        const PLAYERS = JSON_PAYLOAD;

        const PodiumCard = ({ player, rank, size, title, color }) => {
            if (!player) return null;
            
            return (
                <motion.div 
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: rank * 0.2 }}
                    className={`podium-card glass-card p-8 text-center rank-${rank} ${size}`}
                >
                    {rank === 1 && <i className="ph ph-crown-simple crown-icon"></i>}
                    
                    <div className="mb-4 flex flex-col items-center">
                        <div className="w-24 h-24 rounded-full border-4 border-white/10 p-2 mb-4 bg-black/20">
                            <img src={`/static/characters/${player.avatar}`} className="w-full h-full object-contain" />
                        </div>
                        <h2 className="orbitron font-black text-xl text-white tracking-widest">{player.username}</h2>
                        <span className="text-[10px] uppercase tracking-[0.3em] font-bold text-gray-400 mt-1">{title}</span>
                    </div>

                    <div className="dash-line h-px bg-white/10 my-4 w-full"></div>

                    <div className="flex flex-col items-center">
                        <span className="text-[10px] uppercase text-gray-500 font-bold mb-1">Combat Score</span>
                        <div className={`orbitron text-3xl font-black drop-shadow-md`} style={{ color: color, filter: `drop-shadow(0 0 10px ${color})` }}>
                            {player.score}
                        </div>
                    </div>
                </motion.div>
            );
        };

        const WarriorRow = ({ player, rank, color }) => (
            <motion.div 
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                className={`warrior-row glass-card p-4 mb-3 flex items-center justify-between diagonal-stripes`}
                style={{ borderLeftColor: color }}
            >
                <div className="flex items-center gap-6">
                    <div className="w-10 h-10 rounded-lg flex items-center justify-center font-black orbitron text-xl text-white/50">
                        #{rank}
                    </div>
                    <div>
                        <h4 className="orbitron font-bold text-white text-lg leading-none">{player.username}</h4>
                        <span className="text-[10px] text-gray-500 uppercase font-bold tracking-widest">Brave Fighter</span>
                    </div>
                    <i className="ph ph-swords text-gray-600 text-xl ml-4"></i>
                </div>

                <div className="text-right">
                    <span className="text-[10px] text-gray-500 uppercase font-bold">Points</span>
                    <div className="orbitron text-xl font-bold text-white leading-none">{player.score}</div>
                </div>
            </motion.div>
        );

        const StatCard = ({ title, value, icon, color }) => (
            <div className="glass-card p-6 flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl flex items-center justify-center text-3xl" style={{ backgroundColor: color + '20', color: color }}>
                    <i className={icon}></i>
                </div>
                <div>
                    <div className="text-[10px] text-gray-500 font-bold uppercase tracking-widest leading-none mb-1">{title}</div>
                    <div className="orbitron text-2xl font-black text-white">{value}</div>
                </div>
            </div>
        );

        const PantheonApp = () => {
            const top3 = PLAYERS.slice(0, 3);
            const others = PLAYERS.slice(3);
            const totalPoints = PLAYERS.reduce((sum, p) => sum + p.score, 0);
            const avgPoints = PLAYERS.length > 0 ? Math.floor(totalPoints / PLAYERS.length) : 0;

            return (
                <div className="max-w-6xl mx-auto py-20 px-4">
                    <header className="text-center mb-24 relative">
                        <motion.h1 
                            initial={{ scale: 0.8, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            className="orbitron text-6xl font-black tracking-tighter text-white mb-2 drop-shadow-[0_0_20px_rgba(255,255,255,0.3)]"
                        >
                            PANTHEON <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-500 via-white to-yellow-500">OF CHAMPIONS</span>
                        </motion.h1>
                        <p className="orbitron text-gray-400 uppercase tracking-[0.5em] text-xs font-bold">Global Strategic Ranking</p>
                    </header>

                    {/* PODIUM SECTION */}
                    <div className="podium-grid mb-32 items-end">
                        <PodiumCard player={top3[1]} rank={2} size="h-[400px]" title="Mythic Hero" color="#94a3b8" />
                        <PodiumCard player={top3[0]} rank={1} size="h-[480px] z-10" title="Divine Champion" color="#fbbf24" />
                        <PodiumCard player={top3[2]} rank={3} size="h-[360px]" title="Brave Legend" color="#b45309" />
                    </div>

                    {/* HALL OF WARRIORS */}
                    <div className="mb-24">
                        <h3 className="orbitron text-2xl font-black text-white mb-8 border-b border-white/10 pb-4 inline-block">
                            <i className="ph ph-shield-chevron text-cyan-400 mr-3"></i> HALL OF WARRIORS
                        </h3>
                        <div className="max-h-[600px] overflow-y-auto pr-4">
                            {others.map((p, i) => (
                                <WarriorRow key={i} rank={i + 4} player={p} color={i % 3 === 0 ? '#ef4444' : i % 3 === 1 ? '#22c55e' : '#a855f7'} />
                            ))}
                            {others.length === 0 && <p className="text-gray-500 italic pb-10">Searching for battle records...</p>}
                        </div>
                    </div>

                    {/* STATS SECTION */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-20">
                        <StatCard title="Total Heroes" value={PLAYERS.length} icon="ph ph-users-three" color="#00f2ff" />
                        <StatCard title="Accumulated Power" value={totalPoints.toLocaleString()} icon="ph ph-lightning" color="#fbbf24" />
                        <StatCard title="Average Mastery" value={avgPoints} icon="ph ph-chart-line-up" color="#a855f7" />
                    </div>

                    <div className="text-center">
                        <a href="/" className="orbitron font-black text-sm text-gray-400 hover:text-white transition-all border border-white/10 px-10 py-4 rounded-full glass-card inline-flex items-center gap-3">
                            <i className="ph ph-arrow-left"></i> RETURN TO STRATEGY HUB
                        </a>
                    </div>
                </div>
            );
        };

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<PantheonApp />);
    </script>
</body>
</html>
"""
    return html_template.replace("JSON_PAYLOAD", json_payload)
