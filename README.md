# 🧠 The Last Braincell
### *Multiplayer Productivity or Team Extinction.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Socket.IO](https://img.shields.io/badge/Socket.IO-010101?style=flat&logo=socket.io&logoColor=white)](https://socket.io/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

**The Last Braincell** is a multiplayer productivity accountability game designed to transform the Pomodoro technique into a high-stakes survival challenge. Created for the FOSS Hackathon, it forces teams of up to 4 players to stay focused together—because if one person slips up and visits a blocked site, the entire squad pays the price.

---

## 🔗 Live Demo
**Play Now**: [https://the-last-braincell.onrender.com](https://the-last-braincell.onrender.com)

---

## 📸 Screenshots
*(Coming Soon: Add gameplay and lobby screenshots here)*  
> [!TIP]
> Check out the dynamic pixel-art avatars and GSAP-powered battle transitions in the live demo!

---

## 🎮 How to Play

1.  **Assemble Your Squad**: Create a lobby and share your unique 6-character room code with up to 3 friends.
2.  **Pick Your Avatar**: Choose from 8 unique pixel-art characters (The Mage, the Knight, etc.) and set your gamer tag.
3.  **Establish Rules**: Collaborate to build a **Blocked Sites List**. Every member must approve a site before it's added.
4.  **The Grind**: Enter the **Work Phase**. All players must avoid blocked sites. If anyone visits a forbidden URL, a **Boss Attack** is triggered!
5.  **Recharge**: Survive the work phase to enter the **Break Phase**, where all restrictions are lifted.
6.  **Survive & Earn**: Complete all work sessions without anyone's health reaching zero to claim your **150 XP Reward**.

---

## 🔥 Key Features

-   **Multiplayer Synergy**: Real-time synchronization via Socket.IO ensures every player sees every health drop and boss attack instantly.
-   **The Boss Mechanic**: A dramatic, screen-shaking experience that punishes focus-breakers with shared team damage.
-   **Democratic Blocking**: A site is only blocked if the entire team agrees—total accountability or total freedom.
-   **Persistent Progression**: Earn XP for surving sessions. Your status as a "Focus Fighter" grows with every successful Pomodoro.
-   **Focus Mode**: Request safe-browsing permission from your team for research or reference—but don't stay away too long or you'll bleed health!
-   **Pixel-Perfect Aesthetic**: A pixel-art UI built with **GSAP** for smooth transitions and a premium "retro-future" feel.

---

## 🛠️ Tech Stack

### Backend
-   ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) **Python 3.11** Core logic and data processing.
-   ![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white) **Flask** Lightweight web server.
-   ![Socket.IO](https://img.shields.io/badge/Socket.IO-010101?style=flat&logo=socket.io&logoColor=white) **Flask-SocketIO** Real-time bidirectional communication.
-   ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white) **SQLite** Local server-side data persistence.

### Frontend
-   ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white) ![JS](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black) **Vanilla Stack** Core UI logic without heavy frameworks.
-   ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white) **Tailwind CSS** Modern utility-first styling.
-   ![GSAP](https://img.shields.io/badge/GSAP-88CE02?style=flat&logo=greensock&logoColor=white) **GSAP 3** High-performance UI animations.
-   ![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB) **React 18** Powering the Arsenal and Leaderboard views (via CDN).

### Deployment
-   ![Render](https://img.shields.io/badge/Render-46E3B7?style=flat&logo=render&logoColor=white) **Render** Automated CI/CD and hosting.

---

## 🚀 Local Setup

To run **The Last Braincell** on your own machine, follow these steps:

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/sadhana-2008/Focus_Fighter.git
    cd Focus_Fighter
    ```

2.  **Set Up Virtual Environment** (Optional but Recommended)
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize Database**
    ```bash
    python init_db.py
    ```

5.  **Launch the App**
    ```bash
    python main.py
    ```

6.  **Play!**
    Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 👥 The Team
-   **[Your Name / Team Name Here]** — Core Development, UI/UX, Backend Engine.

---

## 📄 License
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

> [!NOTE]
> Created for the **FOSS Hackathon**. We believe productivity should be social, accountability should be fun, and code should be free.
