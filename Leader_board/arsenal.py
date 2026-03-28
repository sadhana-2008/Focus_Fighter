import os
import json

class Item:
    def __init__(self, name, icon, rarity, item_type, stat, value, effects=None):
        self.name = name
        self.icon = icon # Phosphor icon class
        self.type = item_type # weapon, armor, etc.
        self.stat = stat # xp, health, etc.
        self.value = value
        self.rarity = rarity # common, rare, epic, legendary
        self.effects = effects or {}

class Character:
    def __init__(self, name, level, role, avatar_img, stats, inventory=None):
        self.name = name
        self.level = level
        self.role = role
        self.avatar_img = avatar_img
        self.stats = stats # {intellect, stamina, focus, creativity}
        self.inventory = inventory or []

def render_arsenal(characters):
    """
    Generates the complete HTML/JS/CSS for the Arsenal UI.
    Includes functional inventory grid with real icons and tooltips.
    """
    
    # Pre-process character data for JSON injection
    char_data_json = []
    for char in characters:
        char_data_json.append({
            "name": char.name,
            "level": char.level,
            "role": char.role,
            "avatar": char.avatar_img,
            "stats": char.stats,
            "inventory": [
                {
                    "name": item.name,
                    "icon": item.icon,
                    "type": item.type,
                    "stat": item.stat,
                    "value": item.value,
                    "rarity": item.rarity,
                    "effects": item.effects
                } for item in char.inventory
            ]
        })

    json_payload = json.dumps(char_data_json)

    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arsenal - Antigravity Field</title>
    
    <!-- Dependencies -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    
    <!-- React & Framer Motion from CDN -->
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://unpkg.com/framer-motion@10.16.4/dist/framer-motion.js"></script>

    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&family=Press+Start+2P&display=swap" rel="stylesheet">

    <style>
        :root {
            --neon-blue: #00f2ff;
            --neon-pink: #ff00cc;
            --neon-purple: #bc13fe;
            --glass-bg: rgba(10, 10, 15, 0.85);
            --rarity-common: #475569;
            --rarity-rare: #1d4ed8;
            --rarity-epic: #7e22ce;
            --rarity-legendary: #a16207;
            
            --rarity-bg-common: rgba(71, 85, 105, 0.4);
            --rarity-bg-rare: rgba(29, 78, 216, 0.4);
            --rarity-bg-epic: rgba(126, 34, 206, 0.4);
            --rarity-bg-legendary: rgba(161, 98, 7, 0.4);
        }

        body, html {
            margin: 0;
            padding: 0;
            background: #050508;
            color: #fff;
            font-family: 'Rajdhani', sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
            overflow-y: auto;
        }

        .inventory-slot {
            aspect-ratio: 1;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            overflow: hidden;
        }

        .inventory-slot.empty {
            cursor: default;
            opacity: 0.4;
            border-style: dashed;
        }

        .inventory-slot.selected {
            border-color: #fff;
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.4);
            transform: scale(1.05);
            z-index: 5;
        }

        .item-icon-container {
            width: 80%;
            height: 80%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            z-index: 2;
        }

        .item-rarity-bg {
            position: absolute;
            inset: 0;
            z-index: 1;
            opacity: 0.6;
        }

        .tooltip {
            position: fixed;
            background: rgba(0, 0, 0, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 12px;
            border-radius: 8px;
            z-index: 1000;
            pointer-events: none;
            width: 200px;
            backdrop-filter: blur(8px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }

        .dash-line {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            margin: 8px 0;
        }

        /* Rest of existing styles (Background, Dashboard, etc.) */
        .antigravity-bg { position: fixed; inset: 0; background: radial-gradient(circle at 50% 50%, #1a1a2e 0%, #050508 100%); z-index: -10; }
        .bg-gif { position: fixed; inset: 0; background-image: url('/static/bg_gif.gif'); background-size: cover; background-position: center; opacity: 0.2; mix-blend-mode: overlay; z-index: -9; }
        .dashboard-container { max-width: 1300px; margin: 40px auto; padding: 32px; display: grid; grid-template-columns: 400px 1fr; gap: 40px; background: var(--glass-bg); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 32px; }
        .profile-card { background: rgba(255, 255, 255, 0.03); border-radius: 24px; padding: 32px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.05); }
        .avatar-container { width: 200px; height: 200px; margin: 0 auto 24px; position: relative; }
        .avatar-image { width: 100%; height: 100%; object-fit: contain; filter: drop-shadow(0 0 20px var(--neon-blue)); }
        .char-name { font-family: 'Orbitron', sans-serif; font-size: 24px; font-weight: 900; color: #fff; margin-bottom: 4px; }
        .char-role { font-size: 14px; color: var(--neon-blue); text-transform: uppercase; letter-spacing: 4px; opacity: 0.8; }
        .stats-table { width: 100%; border-collapse: separate; border-spacing: 0 8px; }
        .stat-label { font-size: 12px; color: rgba(255, 255, 255, 0.6); text-transform: uppercase; letter-spacing: 1.5px; }
        .stat-value { font-family: 'Orbitron', sans-serif; font-size: 14px; text-align: right; padding-right: 12px; font-weight: 700; }
        .stat-bar-bg { height: 6px; background: rgba(255, 255, 255, 0.1); border-radius: 3px; overflow: hidden; width: 100%; }
        .stat-bar-fill { height: 100%; }
        .inventory-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }
    </style>
</head>
<body>
    <div class="antigravity-bg"></div>
    <div class="bg-gif"></div>
    <div id="root"></div>

    <script type="text/babel">
        const { motion, AnimatePresence } = window.FramerMotion || window.Motion || { motion: "div", AnimatePresence: React.Fragment };
        const { useState, useEffect } = React;

        const CHARACTERS = JSON_PAYLOAD;

        const getIconForStat = (stat) => {
            switch(stat?.toLowerCase()) {
                case 'xp': return '⚡';
                case 'health': return '❤️';
                case 'strength': return '⚔️';
                case 'stamina': return '🛡️';
                case 'focus': return '🎯';
                case 'creativity': return '✨';
                case 'dmg': return '🗡️';
                case 'int': return '🧠';
                case 'spd': return '💨';
                case 'def': return '🛡️';
                default: return '📦';
            }
        };

        const InventoryItem = ({ item, index, onHover, onClick, isSelected }) => {
            if (!item) return <div className="inventory-slot empty" />;

            const rarityColor = `var(--rarity-${item.rarity})`;
            const rarityBg = `var(--rarity-bg-${item.rarity})`;
            const displayIcon = item.icon && item.icon.startsWith('ph-') ? <i className={`ph ${item.icon}`}></i> : getIconForStat(item.stat);

            return (
                <motion.div 
                    className={`inventory-slot ${isSelected ? 'selected' : ''}`}
                    onClick={() => onClick(item)}
                    onMouseEnter={(e) => onHover(item, e)}
                    onMouseLeave={() => onHover(null, null)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                >
                    <div className="item-rarity-bg" style={{ backgroundColor: rarityBg }}></div>
                    <div className="item-icon-container" style={{ color: rarityColor }}>
                        {displayIcon}
                    </div>
                    {item.rarity === 'legendary' && (
                        <motion.div 
                            className="absolute inset-0 border-2 border-yellow-500/50 rounded-xl"
                            animate={{ opacity: [0.2, 0.8, 0.2] }}
                            transition={{ duration: 2, repeat: Infinity }}
                        />
                    )}
                </motion.div>
            );
        };

        const Tooltip = ({ data }) => {
            if (!data || !data.item) return null;
            const { item, x, y } = data;
            const rarityColor = `var(--rarity-${item.rarity})`;

            return (
                <div className="tooltip" style={{ left: x + 15, top: y + 15 }}>
                    <div className="flex justify-between items-start mb-1">
                        <span className="font-bold text-sm orbitron text-white">{item.name}</span>
                    </div>
                    <div className="text-[10px] uppercase font-bold tracking-widest" style={{ color: rarityColor }}>
                        {item.rarity} {item.type}
                    </div>
                    <div className="dash-line" />
                    <div className="flex justify-between text-xs">
                        <span className="text-gray-400 capitalize">{item.stat}</span>
                        <span className="text-white font-bold">+{item.value}</span>
                    </div>
                    {item.effects && Object.keys(item.effects).length > 0 && (
                        <div className="mt-2 text-[9px] text-gray-500 italic">
                            Bonus: {Object.entries(item.effects).map(([k,v]) => `${k}+${v}`).join(', ')}
                        </div>
                    )}
                </div>
            );
        };

        const CharacterDashboard = ({ char }) => {
            const [selectedItem, setSelectedItem] = useState(null);
            const [tooltip, setTooltip] = useState(null);

            useEffect(() => {
                console.log(`Inventory loaded for ${char.name}:`, char.inventory);
            }, [char]);

            const stats = [
                { label: "Intellect", value: char.stats.intellect, color: "#a855f7" },
                { label: "Stamina", value: char.stats.stamina, color: "#10b981" },
                { label: "Focus", value: char.stats.focus, color: "#00f2ff" },
                { label: "Creativity", value: char.stats.creativity, color: "#ec4899" }
            ];

            return (
                <div className="dashboard-container relative mb-12">
                    <Tooltip data={tooltip} />
                    
                    <div className="char-panel">
                        <div className="profile-card">
                            <div className="avatar-container">
                                <motion.img 
                                    src={`/static/characters/${char.avatar}`}
                                    className="avatar-image"
                                    animate={{ y: [-5, 5, -5] }}
                                    transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                                />
                            </div>
                            <h2 className="char-name">{char.name}</h2>
                            <p className="char-role">Lv. {char.level} Sovereign</p>
                        </div>

                        <div className="bg-white/5 rounded-2xl p-6 border border-white/5 mt-4">
                            <table className="stats-table">
                                <tbody>
                                    {stats.map((stat, i) => (
                                        <tr key={i}>
                                            <td className="stat-label">{stat.label}</td>
                                            <td className="stat-value">{stat.value}</td>
                                            <td width="40%">
                                                <div className="stat-bar-bg">
                                                    <motion.div 
                                                        className="stat-bar-fill"
                                                        initial={{ width: 0 }}
                                                        whileInView={{ width: `${stat.value}%` }}
                                                        style={{ background: stat.color, boxShadow: `0 0 10px ${stat.color}` }}
                                                    />
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div className="inventory-section">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="orbitron text-lg font-bold flex items-center gap-3">
                                <i className="ph ph-backpack text-cyan-400"></i> INVENTORY
                            </h3>
                            {selectedItem && (
                                <span className="text-[10px] text-gray-500 orbitron">SELECTED: {selectedItem.name}</span>
                            )}
                        </div>
                        
                        <div className="inventory-grid">
                            {Array.from({ length: 20 }).map((_, i) => {
                                const item = char.inventory[i];
                                return (
                                    <InventoryItem 
                                        key={i} 
                                        item={item} 
                                        index={i} 
                                        isSelected={selectedItem?.name === item?.name}
                                        onClick={setSelectedItem}
                                        onHover={(item, e) => setTooltip(item ? { item, x: e.clientX, y: e.clientY } : null)}
                                    />
                                );
                            })}
                        </div>
                        
                        <div className="mt-8 p-4 bg-white/5 rounded-xl border border-white/5 flex gap-4">
                            <button className="flex-1 py-3 rounded-lg bg-cyan-600 hover:bg-cyan-500 font-bold orbitron text-xs transition-colors">EQUIP ITEM</button>
                            <button className="flex-1 py-3 rounded-lg bg-purple-600 hover:bg-purple-500 font-bold orbitron text-xs transition-colors">UPGRADE</button>
                        </div>
                    </div>
                </div>
            );
        };

        const ArsenalApp = () => {
            return (
                <div className="py-20 px-4 max-w-7xl mx-auto">
                    <header className="mb-16 flex justify-between items-end border-l-4 border-cyan-500 pl-8">
                        <div>
                            <h1 className="orbitron text-5xl font-black tracking-tighter text-white mb-2">ARSENAL</h1>
                            <p className="text-gray-500 uppercase tracking-[0.4em] text-[10px] font-bold">Character Strategic Asset Management</p>
                        </div>
                        <a href="/" className="px-8 py-3 bg-white/5 hover:bg-white/10 rounded-full text-[10px] font-bold orbitron border border-white/10 transition-all flex items-center gap-2">
                            <i className="ph ph-house"></i> LOBBY
                        </a>
                    </header>
                    {CHARACTERS.map((char, i) => (
                        <CharacterDashboard key={i} char={char} />
                    ))}
                </div>
            );
        };

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<ArsenalApp />);
    </script>
</body>
</html>
"""
    return html_template.replace("JSON_PAYLOAD", json_payload)
