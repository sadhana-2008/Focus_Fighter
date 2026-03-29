# The Last Braincell — Product Requirements Document

## Overview

**The Last Braincell** is a multiplayer productivity accountability game that gamifies the Pomodoro technique. Players team up (or go solo) to survive timed work sessions while a boss mechanic punishes anyone who visits blocked websites. The core loop: stay focused → survive the boss → earn XP. Break focus → the whole squad suffers.

The game supports two modes: **Solo Mode** (single-player pomodoro timer) and **Group Mode** (up to 4 players with a shared boss fight, lobby codes, and team accountability).

---

## Core Features

| Feature | Solo Mode | Group Mode |
|---|---|---|
| Pomodoro Timer (work + break) | ✅ | ✅ |
| Pause / Resume | ✅ | ✅ |
| Custom work & break durations | ✅ (set before start) | ✅ (host sets before start) |
| Lobby code & multiplayer | ❌ | ✅ (6-char code, max 4 players) |
| Blocked websites list | ❌ | ✅ (team-approved) |
| Boss mechanic | ❌ | ✅ |
| XP & Health system | ❌ | ✅ |
| Focus Mode (safe browsing window) | ❌ | ✅ |
| Win / Game Over screen | ❌ | ✅ |

---

## Solo vs Group Mode

### Solo Mode
- Single player. No lobby code, no teammates.
- Pure pomodoro timer: alternating work and break phases.
- Player sets work duration and break duration before starting. **Cannot change mid-session.**
- Has a **Pause** button and a **Resume** button.
- No boss mechanic, no XP/health tracking, no blocked sites.
- Accessible from the landing page via **Create Lobby → Solo Mode**.

### Group Mode
- 2–4 players. Host generates a unique 6-character lobby code.
- Game starts **only when all 4 player slots are filled** and the host clicks **Start Game**.
- Includes the full boss mechanic, XP/health system, blocked sites, and focus mode.
- Accessible from the landing page via **Create Lobby → Group Mode**.

---

## Lobby & Setup Flow

### Landing Page
Two primary actions:
1. **Create Lobby** — Opens a sub-menu with two options:
   - **Solo Mode** — Immediately enters the solo pomodoro setup (no lobby code).
   - **Group Mode** — Generates a 6-character lobby code and opens the lobby waiting room.
2. **Join Lobby** — Player enters an existing 6-character lobby code to join a group session.

### Lobby Waiting Room (Group Mode)
- Displays the lobby code for sharing.
- Shows 4 player slots. Each player picks an **avatar** and **name** from preset characters.
- Host sets the **work duration** and **break duration** (custom pomodoro structure).
- Team collectively builds the **blocked websites list** (see approval rules below).
- The **Start Game** button is visible to host only and is enabled only when all 4 players have joined.

### Blocked Websites List (Group Mode)
- Any player can propose a website to block.
- A site is **only added** to the blocked list when **all 4 members approve** the addition.
- The blocked list is finalized before the game starts but can also be modified during break phases with unanimous approval.

---

## Pomodoro Structure

- Sessions alternate between **Work Phase** and **Break Phase**.
- Both durations are custom, set by the host (group) or the player (solo) **before the game starts**.
- **Work Phase**: Boss mechanic is active (group mode). Visiting blocked sites triggers attacks.
- **Break Phase**: Free time. No boss attacks. Players can visit any site without penalty.
- Both solo and group modes have a **Pause** button and a **Resume** button for the timer.
- Work/break durations **cannot be changed mid-session**.

---

## Game Loop (Group Mode)

```
┌─────────────────────────────────────────────────┐
│  LOBBY: Host sets timers, team blocks sites     │
│  All 4 players join → Host clicks Start Game    │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│  WORK PHASE                                     │
│  Timer counts down. Boss mechanic is ACTIVE.    │
│  Blocked site visit → screen shake, boss popup, │
│  team loses health, offender loses XP.          │
│  Any player dies → timer resets (full retry).   │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│  BREAK PHASE                                    │
│  Timer counts down. No boss attacks.            │
│  Players can browse freely.                     │
└──────────────────────┬──────────────────────────┘
                       ▼
              (repeat work/break cycle)
                       ▼
┌─────────────────────────────────────────────────┐
│  WIN: Survived all work phases                  │
│  All players earn 150 XP each.                  │
│  Celebration GIF + host controls next action.   │
└─────────────────────────────────────────────────┘
```

---

## XP & Health Rules

### Health
- All players start each session at **100 HP**.
- When a player visits a blocked site during work phase: **all players lose 10 HP** (shared punishment).
- Every **5 seconds** the offending player stays on the blocked site: the offender takes **heavy additional health damage**.
- If any player's health reaches **0**: that player dies.
  - **All players** lose **10 XP**.
  - The **offender** loses an additional **20 XP**.
  - The **timer resets** — the session restarts from the beginning (full retry).

### XP
- **Session win** (survive all work phases): all players earn **150 XP each**.
- **Blocked site offense** (every 5 seconds on a blocked site during work): offender loses **20 XP**.
- **Player death**: all players lose **10 XP**, offender loses **20 XP**.
- XP persists across sessions (lifetime stat).

---

## Boss Mechanic

> Active during **Work Phase only** in **Group Mode**.

### Trigger
A player navigates to a website on the team's blocked list during a work phase.

### Attack Sequence
1. **Screen Shake** — The offending player's screen shakes (ground trembles effect).
2. **Boss Popup** — A dramatic boss character appears on screen with visual/audio cues.
3. **Team Damage** — All players immediately lose **10 HP**.
4. **Sustained Penalty** — Every **5 seconds** the offender remains on the blocked site:
   - Offender loses **20 XP**.
   - Offender takes **heavy health damage**.
5. **Death Check** — If any player's HP hits 0, the session fails (see Health rules above).

### Resolution
- The offender navigates away from the blocked site → boss retreats, attack stops.
- The damage already dealt is **not reversible**.

---

## Focus Mode

> Available in **Group Mode only**.

- Any player can **request permission** from the team to enter Focus Mode for a **set duration**.
- The team must approve the request.
- During Focus Mode:
  - The player is **safe** — no boss attacks even if they visit sites outside the blocked list.
  - Intended for research, reference browsing, etc.
- If the player **does not return** (exit Focus Mode) within the allotted time:
  - Their **health starts reducing** gradually.
  - **No XP penalty** — health reduction only.

---

## Win & Game Over Screen

### Win Screen
- Displayed when the team survives all work phases in a session.
- Shows a **celebration GIF**.
- **Host** sees two buttons:
  - **Back to Home** — Redirects all players to the home/landing page.
  - **Replay** — Restarts the session with same lobby settings.
- **Other players** see:
  - **Back to Home** — Redirects them individually.
  - **"Waiting for host..."** — Displayed until the host makes a decision.

### Game Over (Player Death)
- Triggered when any player's HP reaches 0.
- All players lose XP (see XP rules).
- Timer resets — the full session must be retried.
- Players remain in the lobby; the host can restart.

### Host End-Game Behavior
- If the host clicks **Back to Home**, **all players** are redirected to the landing page.
- The lobby is dissolved.

---

## What's Already Done

| Component | Status |
|---|---|
| Create Lobby UI | ✅ Built |
| Join Lobby UI | ✅ Built |
| Dark / Light mode toggle | ✅ Built |
| Room code generation & display | ✅ Built |
| Player avatar selection | ✅ Built |
| Pomodoro timer display (lobby) | ✅ Built |
| Battle HUD (center timer + squad sidebar) | ✅ Built |
| GSAP animations & transitions | ✅ Built |
| localStorage sync (host ↔ guest) | ✅ Built |

## What Needs Building

| Component | Priority |
|---|---|
| Solo Mode flow (standalone pomodoro, no lobby) | High |
| Blocked websites list with team approval UI | High |
| Boss attack sequence (shake, popup, damage) | High |
| XP & Health tracking system | High |
| Pomodoro timer with pause/resume (functional) | High |
| Work/break phase alternation logic | High |
| Game start trigger (host-only, 4-player gate) | High |
| Win screen with celebration GIF | Medium |
| Game over / retry flow | Medium |
| Focus Mode (request, approve, timer, health drain) | Medium |
| Host end-game redirect (all players kicked) | Medium |
| Persistent XP across sessions | Low |
