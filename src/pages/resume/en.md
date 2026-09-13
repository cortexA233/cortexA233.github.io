---
title: Resume
---

**Mengxiang Wang**<br>
**Gameplay / Systems Programmer**<br>
Game clients · Combat and camera systems · Editor tools

**Email:** [cortexA233@outlook.com](mailto:cortexA233@outlook.com)<br>
**GitHub:** [github.com/cortexA233](https://github.com/cortexA233)<br>
**LinkedIn:** [Mengxiang Wang](https://www.linkedin.com/in/mengxiang-wang-b4b0a4381/)<br>
**Portfolio:** [cortexa233.itch.io](https://cortexa233.itch.io/)

Game programmer focused on game clients, combat and camera systems, and editor tools. Developed commercial games at NetEase Games and Papergames; currently works on AI game-development evaluation and 3D generation workflows at Philo Labs. Lead programmer on **Exp10sion**, released on Steam and Nintendo Switch.

## Technical Skills

- **Programming languages:** C#, Python, Lua, C++, GDScript.
- **Engineering:** Game clients, combat and camera systems, skill and presentation editors, spatial data structures and performance optimization, automated testing and evaluation.
- **Engines and tools:** Unity, Godot, Unreal Engine, Messiah, Three.js, Phaser, Qt/PyQt, IMGUI.
- **AI workflows:** Familiar with Codex and Claude Code; combines game-engine MCP integrations, Skills, and automation scripts for batch development, validation, and evaluation.
- **DCC software:** Basic knowledge of Maya and its Python scripting workflow.
- **Spoken languages:** English (CET-6; TOEFL iBT 102, section scores 28/29/22/23), Japanese (JLPT N1).

## Professional Experience

### Philo Labs — San Francisco, CA, USA

**Member of Technical Staff, Intern | July 2025 – Present**<br>
Python, Three.js, RAG, Unity, Godot, GDScript, C#

- Built a **Three.js workflow for agent-generated 3D models and scenes**, using a reference asset library for RAG retrieval and authoring supporting Skills, Evals, and workflow scripts to improve output quality, controllability, and stability.
- Created agentic game-development benchmark tasks and acceptance criteria for **Unity, Unreal Engine, and Godot**. Translated gameplay requirements into scoring rules and completion criteria covering functional correctness, interaction feedback, audiovisual presentation, and stability; collaborated with engineers on agent operation, result collection, and reproducible validation for automated evaluation across models, engines, and versions.
- Analyzed defects, regressions, near-misses, and implementations that exceeded task boundaries or exploited scoring rules; converted failure patterns into reproducible tests and grader rules to improve benchmark discrimination and reliability.

### NetEase Games — Hangzhou — Joker Studio — Sea of Remnants

**Senior Game Development Engineer | November 2023 – May 2025**<br>
Python, Messiah (in-house engine)

- Maintained and developed the game-wide camera system: standardized integration interfaces for other pipelines and node graphs, implemented camera inertia and collision modules, and built camera GM tools for debugging and invoking game logic. Helped other pipelines integrate the camera system and implement camera effects.
- Built designer-facing camera **Modifiers** to manage position, rotation, viewing distance, and FOV consistently, with configurable, reusable effects such as camera movement along tracks and dolly zooms.
- Developed ground-combat features on both server and client: movement synchronization and character positioning on the server; camera presentation, scene loading, and character poses on the client.
- Extended skill-editor keyframes and event nodes, and implemented frame events and designer-facing pseudocode scripting APIs for authoring skills, flow logic, and combat presentation.
- Built a **PyQt and Timeline** combat-presentation editor that previewed content outside combat, reproducing turn-based combat presentation rules so designers and artists could create skill, buff, and cinematic assets efficiently.
- Built an **IMGUI** runtime character-lighting editor to add game-specific lighting configuration capabilities missing from the engine.

### Papergames — Shanghai — Shining Nikki

**Game Client Development Engineer | December 2020 – June 2023**<br>
C#, Lua, Unity

- Independently developed multiple **2D/3D minigames** for events and the main story, using new gameplay ideas to strengthen narrative immersion and interactivity.
- Contributed image-enhancement and effects modules to photo editing, including stickers with custom text, effects, and Transform editing; implemented a dual-anchor positioning algorithm to synchronize UGUI effects with a 3D character's position, scale, and rotation.
- Developed low-level Lua components: optimized AABB ray tests and implemented OBB support for arbitrary transforms, OBB/AABB intersections, and ray tests. Designed a hybrid octree/BVH spatial-partitioning strategy for frequent global object queries, making ray tests **2–5× faster than Unity's `RaycastAll`**.
- Organized technical knowledge-sharing sessions on **SDF, TextMesh, and Ray Marching**, and implemented stylized UI text using pregenerated SDF base images.

### NetEase Games — Shanghai — Singularity Studio — LifeAfter

**Game Development Engineer Intern | July 2020 – September 2020**<br>
Python, NeoX (in-house engine)

- Maintained and improved a tool that exported designers' Excel configurations as Python dictionaries; designed parallel export processing to increase throughput from approximately **550 to 1,500 tables per minute**.
- Added features to a **NetEase POPO** chatbot for checking the export tool's status on local machines and servers.

## Personal Projects

### Gacha Seed — UE5 Management Simulation + Roguelike

**Independent Development / Gameplay Systems / 3C Design and Polish | August 2026**<br>
Unreal Engine 5, three-day Game Jam

- Delivered a playable prototype combining management simulation and Roguelike gameplay in **a three-day Game Jam** using UE5.
- Independently implemented the gameplay systems, integrating management and Roguelike mechanics into the core game loop.
- Contributed to **3C (character, camera, controls)** design and polish, iterating on feedback and game feel.

### Exp10sion and Unity Framework KToolkit

**Lead Programmer / Framework Developer / Project Manager | July 2023 – November 2023**<br>
C#, Unity

- Proposed the core **10-second loop** rule and built the Game Jam prototype levels that became the full game's first chapter; contributed to menu interactions and UI experience design.
- Implemented most of the game as lead programmer and extracted reusable logic into **KToolkit** for subsequent projects.
- Built KToolkit's global event system using event-name enums and delegate mappings, plus a UI framework covering managers, pages, data handling, and page lifecycles. Implemented an extensible **FSM** that binds state components through `MonoBehaviour` to manage gameplay transitions and lifecycles consistently.
- Helped refine platforming feel, using industry examples, literature, and GDC talks to define movement parameters and implementation guidelines.
- Planned development schedules and controlled scope and level count for a **3–6-person team**; worked with art project management on asset organization, iteration, and standards, adjusting schedules and milestones in weekly meetings.
- Integrated Steam SDK features for statistics, achievements, and leaderboards; helped ship the game on **Steam and Nintendo Switch**, then iterated on player feedback.
- Links: [Steam](https://store.steampowered.com/app/2618850/Exp10sion/) · [KToolkit on GitHub](https://github.com/cortexA233/KToolkit_for_unity) · [Nintendo Switch store](https://www.nintendo.com/us/store/products/10-second-ghost-switch/).

### Daddy Gaiden — Fast-Paced 2D Action Roguelike Prototype

**Lead Programmer / Combat Systems Developer / Project Manager | December 2025**<br>
Game Jam project

- Created a fast-paced combat experience inspired by *Ninja Gaiden 2* within a 2D side-scrolling framework, incorporating Roguelike resource management and progression.
- As project creator and combat designer, designed the complete combat mechanics and supporting resource systems; as lead programmer, implemented all gameplay features, focusing on input feedback, combat rhythm, and overall presentation.
- Planned tasks and schedules, coordinated contributors across disciplines, and guided the team to deliver a playable build within the Game Jam.
- [Play on itch.io](https://cortexa233.itch.io/daddy-gaiden).

### SmallTalker — LLM-Based Social Simulation Serious Game

**Programmer / Technical Artist | December 2025**<br>
Northeastern University research project

- Contributed to interaction flow and experience design for a serious game that trains conversation and social skills in simulated workplace settings.
- Implemented the complete gameplay logic and interactions across multiple scenes, connecting voice input, conversation history, scene state, failure retries, and system feedback into a continuous training loop that supports reviewing past sessions.
- Helped develop **NPC Personas** and dialogue transitions following player interventions; used a shared character graph, transition lines, and intervention feedback to maintain consistency across scenes and control branching transitions.
- Created scene and character shaders and post-processing, and integrated art assets to achieve a hand-drawn visual style.

## Open-Source Contributions

### Tiled — Cross-Platform, Cross-Engine Game Map Editor

**Open-Source Contributor**<br>
C++, Qt

- Contributed maintenance fixes for longstanding issues and small features to improve usability.
- Designed and implemented automatic unloading of old images and cache cleanup to keep memory and cache usage bounded when multiple images were open.
- [Tiled on GitHub](https://github.com/mapeditor/tiled).

## Education

**Northeastern University — M.S. in Game Science and Design**<br>
September 2025 – May 2027 (expected)

**Shanghai University — B.Eng. in Communication Engineering**<br>
September 2017 – July 2021
