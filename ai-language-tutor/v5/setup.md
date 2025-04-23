┌─────────┐       HTTPS       ┌─────────────┐       → OpenAI API / fine‑tuned GPT  
│ Browser │ ───────────────── │  FastAPI    │ ───────────────────────────────→ LLM  
│ (React) │                   │  Backend    │  
└─────────┘                   └─────────────┘  
    ↓                              │  
 WebSockets                        ↓  
(for simulation)             PostgreSQL  
                              (JSONB storage)  


**Option 1: Direct Improvement (Cleaner & Clearer)**

"Let's outline the requirements for a motivational todo list application designed to combat procrastination and build agency.

**Core Problem:** User experiences a lack of urgency and follow-through on planned tasks.
**Primary Goal:** Increase daily task completion rates and build consistent habits through tracking and accountability.

**Key Features:**

1.  **Task Management:**
    *   Add daily tasks with descriptions.
    *   Mark tasks as complete or incomplete.
    *   Option for recurring tasks.
2.  **Scoring System:**
    *   Each task entered for the day is assigned a potential score (e.g., 10 points).
    *   Completed Task: User earns the full 10 points for that task instance.
    *   Incomplete Task: User earns 0 points for that task instance.
    *   **Habit Stagnation Adjustment:** If a specific *recurring* task shows a pattern of completion but the user feels minimal actual improvement in the underlying habit/performance (self-assessed during review?), deduct 1 point from its potential score for future instances, encouraging reflection or task adjustment. (Needs refinement on *how* this is triggered/tracked).
3.  **Progress Dashboard:**
    *   Visualize task completion scores and trends.
    *   Display progress views: Daily, Weekly, Monthly, Quarterly, Yearly (e.g., showing total score achieved vs. potential score, completion percentage).
4.  **Daily Review & Reminder:**
    *   A non-dismissible (or highly persistent) reminder at 9 PM daily.
    *   Prompt the user to:
        *   Mark the day's tasks as complete/incomplete.
        *   Briefly describe or reflect on the day's accomplishments and challenges.
        *   Potentially trigger the 'Habit Stagnation Adjustment' based on reflection.
5.  **Goal Tracking Integration:** (Slightly enhanced)
    *   Allow users to define overarching goals (e.g., "Exercise 3x/week", "Finish Project X").
    *   Optionally link specific tasks to these goals.
    *   Dashboard should also show progress towards these defined goals, possibly based on points accumulated from linked tasks."

---

**Option 2: More Comprehensive & Structured (Better for Development Spec)**

"**Project:** Design Specification for a Motivational Todo & Habit Tracking Application

**1. Introduction & Purpose:**
*   **Problem:** Address user difficulties with procrastination, lack of urgency, and poor follow-through on intentions.
*   **Solution:** Develop a digital tool that encourages daily task completion, builds accountability, tracks progress transparently, and fosters habit improvement.
*   **Core Philosophy:** Focus on consistent daily action, positive reinforcement, and mindful reflection.

**2. Target User:** Individuals struggling with task initiation, consistency, and translating plans into actions.

**3. Core Modules & Features:**

*   **3.1. Task Management:**
    *   Create, edit, delete tasks.
    *   Task attributes: Title, Description (optional), Due Date (primarily 'today'), Priority (optional), Recurring options (daily, weekly, specific days), Link to Goal (optional).
    *   Daily Task List view.
    *   Marking: Simple 'Complete' / 'Incomplete' status for each task instance.

*   **3.2. Scoring & Gamification Engine:**
    *   **Base Score:** Each task instance scheduled for a day has a default potential value (e.g., 10 points).
    *   **Completion:** Marking a task complete awards the full points for that instance to the daily/period total.
    *   **Non-Completion:** Marking incomplete (or leaving unmarked past the review) awards 0 points.
    *   **Habit Improvement Modifier (Refined Concept):**
        *   During the Daily Review (see 3.4), for *recurring* tasks completed, the user can optionally rate their *quality* or *perceived improvement* (e.g., scale of 1-3: Stagnant, Progressing, Mastered).
        *   Consistently rating a task as 'Stagnant' over X reviews could trigger a prompt: "This habit seems stuck. Consider adjusting the task or your approach? [Adjust Task] [Keep Score] [Reduce Potential Score by 1]". This makes the deduction user-driven and reflective rather than purely automatic.
    *   **Streaks:** Track consecutive days of meeting a minimum score threshold or completing all tasks.

*   **3.3. Dashboard & Reporting:**
    *   **Views:** Daily, Weekly, Monthly, Quarterly, Yearly.
    *   **Metrics Displayed:**
        *   Total score achieved vs. potential score.
        *   Task completion rate (%).
        *   Streaks (daily completion).
        *   Progress towards linked Goals (if implemented).
        *   Charts/Graphs visualizing trends over the selected period.
    *   Ability to filter/view scores related to specific Goals or task types (if categories are added).

*   **3.4. Daily Review & Reflection:**
    *   **Trigger:** Mandatory notification at 9 PM daily (user-configurable time).
    *   **Process:**
        1.  User is presented with the day's task list.
        2.  Must mark each task as Complete/Incomplete.
        3.  (Optional but encouraged) Rate quality/improvement for completed recurring tasks (triggers Habit Modifier logic).
        4.  Provide a text field for a brief "Daily Summary/Reflection" (e.g., What went well? What was challenging? Plan for tomorrow?).
        5.  Review completion unlocks the next day's view/full dashboard access (to encourage the habit).

*   **3.5. Goal Setting:**
    *   Create, edit, delete long-term goals.
    *   Goals can have descriptions and target metrics/deadlines (optional).
    *   Ability to associate tasks with one or more goals.

**4. Non-Functional Requirements:**
*   **Platform:** (Specify: Web App, iOS, Android, Cross-platform?)
*   **UI/UX:** Clean, intuitive, motivating design. Visual feedback for scoring and progress.
*   **Notifications:** Reliable daily review reminder. Optional reminders for tasks.
*   **Data Persistence:** User data should be saved reliably.

**5. Key Questions to Resolve:**
*   How exactly should the 'Habit Stagnation' logic be implemented to be fair and motivating?
*   What level of detail is needed for Goal tracking visualization?
*   What specific chart types are most effective for the dashboard?"

---

**Key Improvements Made:**

1.  **Clarity of Purpose:** Explicitly states the problem and how the app aims to solve it.
2.  **Structure:** Uses headings and bullet points for better organization.
3.  **Specificity:** Adds detail to features (e.g., task attributes, dashboard metrics, review process).
4.  **Refined Ambiguity:** Addresses the confusing "score deduction" by proposing a more interactive, user-driven mechanism tied to the daily review and recurring tasks.
5.  **Added Context:** Includes sections for Target User, Non-Functional Requirements, and Key Questions.
6.  **Action-Oriented Language:** Uses terms appropriate for design or development specifications.