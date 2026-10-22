import streamlit as st
import json
from pathlib import Path
from datetime import date, datetime

# ==========================================
# CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Notes Wave | StudyTrack AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path("study_data")
DATA_DIR.mkdir(exist_ok=True)


# ==========================================
# DATA STORAGE
# ==========================================

def load_data(filename, default=None):
    path = DATA_DIR / filename

    if not path.exists():
        return default if default is not None else []

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default if default is not None else []


def save_data(filename, data):
    path = DATA_DIR / filename
    temp_path = path.with_suffix(".tmp")

    temp_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    temp_path.replace(path)


# ==========================================
# SESSION STATE
# ==========================================

defaults = {
    "subjects": load_data("subjects.json", [
        {
            "id": "python",
            "name": "Python Programming",
            "color": "#6366f1",
        },
        {
            "id": "maths",
            "name": "Engineering Mathematics",
            "color": "#06b6d4",
        },
        {
            "id": "linear",
            "name": "Linear Algebra",
            "color": "#10b981",
        },
        {
            "id": "ai",
            "name": "Artificial Intelligence",
            "color": "#f59e0b",
        },
    ]),
    "topics": load_data("topics.json"),
    "notes": load_data("notes.json"),
    "revisions": load_data("revisions.json"),
    "goals": load_data("goals.json"),
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def persist():
    for key in [
        "subjects",
        "topics",
        "notes",
        "revisions",
        "goals",
    ]:
        save_data(f"{key}.json", st.session_state[key])


def make_id():
    return datetime.now().strftime("%Y%m%d%H%M%S%f")


def subject_names():
    return [s["name"] for s in st.session_state.subjects]


def subject_topic_count(subject):
    return sum(
        t["subject"] == subject
        for t in st.session_state.topics
    )


def completion_rate():
    topics = st.session_state.topics

    if not topics:
        return 0

    completed = sum(t["completed"] for t in topics)

    return int(completed / len(topics) * 100)


# ==========================================
# CUSTOM STYLING
# ==========================================

st.markdown("""
<style>
    .stApp {
        background-color: #0b1020;
        color: #f8fafc;
    }

    [data-testid="stSidebar"] {
        background-color: #11182b;
        border-right: 1px solid #26324a;
    }

    .hero {
        padding: 28px;
        border-radius: 20px;
        background: linear-gradient(120deg, #182449, #172033);
        border: 1px solid #34456a;
        margin-bottom: 24px;
    }

    .hero h1 {
        color: #ffffff;
        font-size: 2.3rem;
        margin-bottom: 8px;
    }

    .hero p {
        color: #bac7e0;
        margin-bottom: 0;
    }

    .metric-card {
        background: #141d32;
        padding: 20px;
        border: 1px solid #293752;
        border-radius: 16px;
        min-height: 115px;
    }

    .metric-label {
        color: #a7b5ce;
        font-size: 0.9rem;
    }

    .metric-value {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
        margin-top: 8px;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 24px;
        margin-bottom: 14px;
    }

    .subject-card {
        background: #141d32;
        border: 1px solid #293752;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 10px;
    }

    div[data-testid="stMetric"] {
        background: #141d32;
        border: 1px solid #293752;
        padding: 16px;
        border-radius: 14px;
    }

    .stButton > button {
        border-radius: 10px;
    }

    h1, h2, h3 {
        letter-spacing: -0.4px;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

with st.sidebar:
    st.markdown("# 📚 Notes Wave")
    st.caption("YOUR PERSONAL STUDY SPACE")

    st.divider()

    page = st.radio(
        "WORKSPACE",
        [
            "Dashboard",
            "Subjects",
            "Topics",
            "Notes",
            "Revision",
            "Goals",
        ],
        label_visibility="visible",
    )

    st.divider()

    st.markdown("### 🎯 Your progress")

    st.progress(completion_rate() / 100)

    st.caption(f"{completion_rate()}% of topics completed")

    st.divider()

    st.caption("Small steps. Consistent progress.")


# ==========================================
# DASHBOARD
# ==========================================

if page == "Dashboard":

    st.markdown("""
    <div class="hero">
        <h1>Your Learning Dashboard 👋</h1>
        <p>
            One space for your notes, subjects, revisions,
            and academic goals.
        </p>
    </div>
    """, unsafe_allow_html=True)

    topics = st.session_state.topics
    notes = st.session_state.notes
    goals = st.session_state.goals
    subjects = st.session_state.subjects

    completed_topics = sum(
        t["completed"] for t in topics
    )

    completed_goals = sum(
        g["completed"] for g in goals
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("📚 Subjects", len(subjects))

    with c2:
        st.metric("📝 Notes", len(notes))

    with c3:
        st.metric(
            "✅ Topics completed",
            f"{completed_topics}/{len(topics)}",
        )

    with c4:
        st.metric(
            "🎯 Goals completed",
            f"{completed_goals}/{len(goals)}",
        )

    st.markdown(
        '<div class="section-title">Your subjects</div>',
        unsafe_allow_html=True,
    )

    if subjects:

        columns = st.columns(2)

        for index, subject in enumerate(subjects):

            count = subject_topic_count(subject["name"])

            subject_topics = [
                t for t in topics
                if t["subject"] == subject["name"]
            ]

            done = sum(
                t["completed"] for t in subject_topics
            )

            progress = done / count if count else 0

            with columns[index % 2]:

                st.markdown(
                    f"""
                    <div class="subject-card">
                        <h3>{subject['name']}</h3>
                        <p>{count} topics · {done} completed</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.progress(progress)

    else:
        st.info("Add a subject to start tracking your studies.")

    st.markdown(
        '<div class="section-title">Upcoming revisions</div>',
        unsafe_allow_html=True,
    )

    today = date.today().isoformat()

    upcoming = sorted([
        r for r in st.session_state.revisions
        if not r["completed"] and r["date"] >= today
    ], key=lambda r: r["date"])

    if upcoming:

        for revision in upcoming[:5]:

            st.write(
                f"📅 **{revision['topic']}** — "
                f"{revision['date']}"
            )

    else:
        st.info("No upcoming revisions. Plan your next review!")

    st.markdown(
        '<div class="section-title">Recent notes</div>',
        unsafe_allow_html=True,
    )

    if notes:

        for note in reversed(notes[-5:]):

            with st.expander(
                f"📝 {note['title']} · {note['subject']}"
            ):
                st.write(note["content"])

    else:
        st.info("Your saved notes will appear here.")


# ==========================================
# SUBJECTS
# ==========================================

elif page == "Subjects":

    st.title("📚 Subjects")
    st.write("Organise your academic subjects in one place.")

    with st.form("add_subject_form"):

        name = st.text_input("Subject name")

        color = st.selectbox(
            "Subject color",
            [
                "#6366f1",
                "#06b6d4",
                "#10b981",
                "#f59e0b",
                "#ec4899",
                "#8b5cf6",
            ],
        )

        submitted = st.form_submit_button("＋ Add subject")

        if submitted:

            if not name.strip():
                st.error("Enter a subject name.")

            elif any(
                s["name"].lower() == name.strip().lower()
                for s in st.session_state.subjects
            ):
                st.warning("That subject already exists.")

            else:

                st.session_state.subjects.append({
                    "id": make_id(),
                    "name": name.strip(),
                    "color": color,
                })

                persist()
                st.success("Subject added!")
                st.rerun()

    st.divider()

    for subject in st.session_state.subjects:

        with st.container(border=True):

            col1, col2 = st.columns([4, 1])

            with col1:

                st.subheader(subject["name"])

                st.caption(
                    f"{subject_topic_count(subject['name'])} topics"
                )

            with col2:

                if st.button(
                    "Delete",
                    key=f"delete_subject_{subject['id']}",
                ):

                    name = subject["name"]

                    st.session_state.subjects = [
                        s for s in st.session_state.subjects
                        if s["id"] != subject["id"]
                    ]

                    st.session_state.topics = [
                        t for t in st.session_state.topics
                        if t["subject"] != name
                    ]

                    st.session_state.notes = [
                        n for n in st.session_state.notes
                        if n["subject"] != name
                    ]

                    st.session_state.revisions = [
                        r for r in st.session_state.revisions
                        if r["subject"] != name
                    ]

                    persist()
                    st.rerun()


# ==========================================
# TOPICS
# ==========================================

elif page == "Topics":

    st.title("🗂️ Topics")
    st.write("Break subjects into smaller learning milestones.")

    if not st.session_state.subjects:

        st.warning("Create a subject first.")

    else:

        with st.form("add_topic_form"):

            subject = st.selectbox(
                "Subject",
                subject_names(),
            )

            topic_name = st.text_input("Topic name")

            difficulty = st.selectbox(
                "Difficulty",
                ["Easy", "Medium", "Hard"],
            )

            submitted = st.form_submit_button("＋ Add topic")

            if submitted:

                if not topic_name.strip():
                    st.error("Enter a topic name.")

                else:

                    st.session_state.topics.append({
                        "id": make_id(),
                        "subject": subject,
                        "name": topic_name.strip(),
                        "difficulty": difficulty,
                        "completed": False,
                    })

                    persist()
                    st.success("Topic added!")
                    st.rerun()

    st.divider()

    filter_subject = st.selectbox(
        "Filter subjects",
        ["All subjects"] + subject_names(),
    )

    for topic in st.session_state.topics:

        if (
            filter_subject != "All subjects"
            and topic["subject"] != filter_subject
        ):
            continue

        with st.container(border=True):

            col1, col2, col3 = st.columns([4, 1, 1])

            with col1:

                st.markdown(f"**{topic['name']}**")

                st.caption(
                    f"{topic['subject']} · {topic['difficulty']}"
                )

            with col2:

                new_status = st.checkbox(
                    "Done",
                    value=topic["completed"],
                    key=f"topic_done_{topic['id']}",
                )

                if new_status != topic["completed"]:

                    topic["completed"] = new_status

                    persist()
                    st.rerun()

            with col3:

                if st.button(
                    "Delete",
                    key=f"topic_delete_{topic['id']}",
                ):

                    st.session_state.topics = [
                        t for t in st.session_state.topics
                        if t["id"] != topic["id"]
                    ]

                    persist()
                    st.rerun()


# ==========================================
# NOTES
# ==========================================

elif page == "Notes":

    st.title("📝 Notes")
    st.write("Capture ideas and keep your learning organised.")

    if not st.session_state.subjects:

        st.warning("Add a subject first.")

    else:

        with st.form("note_form"):

            subject = st.selectbox(
                "Subject",
                subject_names(),
            )

            title = st.text_input("Note title")

            content = st.text_area(
                "Write your notes",
                height=200,
            )

            tags = st.text_input(
                "Tags",
                placeholder="python, loops, examples",
            )

            submitted = st.form_submit_button("💾 Save note")

            if submitted:

                if not title.strip() or not content.strip():

                    st.error("Enter a title and some note content.")

                else:

                    st.session_state.notes.append({
                        "id": make_id(),
                        "subject": subject,
                        "title": title.strip(),
                        "content": content,
                        "tags": tags.strip(),
                        "created": datetime.now().strftime(
                            "%Y-%m-%d %H:%M"
                        ),
                    })

                    persist()
                    st.success("Note saved!")
                    st.rerun()

    st.divider()

    query = st.text_input("🔍 Search notes")

    matching_notes = [
        n for n in st.session_state.notes
        if query.lower() in (
            n["title"] + " " +
            n["content"] + " " +
            n["subject"] + " " +
            n["tags"]
        ).lower()
    ]

    if matching_notes:

        for note in reversed(matching_notes):

            with st.expander(
                f"📝 {note['title']} · {note['subject']}"
            ):

                st.caption(
                    f"Created {note['created']} · Tags: {note['tags']}"
                )

                st.write(note["content"])

                if st.button(
                    "Delete note",
                    key=f"delete_note_{note['id']}",
                ):

                    st.session_state.notes = [
                        n for n in st.session_state.notes
                        if n["id"] != note["id"]
                    ]

                    persist()
                    st.rerun()

    else:
        st.info("No matching notes found.")


# ==========================================
# REVISION
# ==========================================

elif page == "Revision":

    st.title("🔁 Revision Planner")
    st.write("Schedule reviews to strengthen your memory.")

    if not st.session_state.topics:

        st.info("Create topics before scheduling revisions.")

    else:

        topic_options = {
            f"{t['subject']} — {t['name']}": t
            for t in st.session_state.topics
        }

        with st.form("revision_form"):

            selected = st.selectbox(
                "Choose topic",
                list(topic_options.keys()),
            )

            revision_date = st.date_input(
                "Revision date",
                value=date.today(),
            )

            submitted = st.form_submit_button(
                "＋ Schedule revision"
            )

            if submitted:

                topic = topic_options[selected]

                st.session_state.revisions.append({
                    "id": make_id(),
                    "topic": selected,
                    "subject": topic["subject"],
                    "date": revision_date.isoformat(),
                    "completed": False,
                })

                persist()
                st.success("Revision scheduled!")
                st.rerun()

    st.divider()

    revisions = sorted(
        st.session_state.revisions,
        key=lambda r: r["date"],
    )

    for revision in revisions:

        with st.container(border=True):

            col1, col2 = st.columns([4, 1])

            with col1:

                st.markdown(f"**{revision['topic']}**")

                st.caption(f"Date: {revision['date']}")

                if (
                    revision["date"] < date.today().isoformat()
                    and not revision["completed"]
                ):
                    st.warning("Overdue")

            with col2:

                done = st.checkbox(
                    "Completed",
                    value=revision["completed"],
                    key=f"revision_done_{revision['id']}",
                )

                if done != revision["completed"]:

                    revision["completed"] = done

                    persist()
                    st.rerun()


# ==========================================
# GOALS
# ==========================================

elif page == "Goals":

    st.title("🎯 Study Goals")
    st.write("Set meaningful goals and measure your progress.")

    with st.form("goal_form"):

        title = st.text_input(
            "Goal name",
            placeholder="Complete Python recursion",
        )

        deadline = st.date_input(
            "Target date",
            value=date.today(),
        )

        submitted = st.form_submit_button("＋ Add goal")

        if submitted:

            if not title.strip():

                st.error("Enter a goal name.")

            else:

                st.session_state.goals.append({
                    "id": make_id(),
                    "title": title.strip(),
                    "deadline": deadline.isoformat(),
                    "completed": False,
                })

                persist()
                st.success("Goal created!")
                st.rerun()

    st.divider()

    goals = st.session_state.goals

    completed_goals = sum(
        goal["completed"] for goal in goals
    )

    if goals:

        st.progress(completed_goals / len(goals))

        st.caption(
            f"{completed_goals} of {len(goals)} goals completed"
        )

    for goal in goals:

        with st.container(border=True):

            col1, col2, col3 = st.columns([4, 1, 1])

            with col1:

                st.markdown(f"**{goal['title']}**")

                st.caption(f"Target: {goal['deadline']}")

            with col2:

                completed = st.checkbox(
                    "Done",
                    value=goal["completed"],
                    key=f"goal_done_{goal['id']}",
                )

                if completed != goal["completed"]:

                    goal["completed"] = completed

                    persist()
                    st.rerun()
    
            with col3:

                if st.button(
                    "Delete",
                    key=f"goal_delete_{goal['id']}",
                ):

                    st.session_state.goals = [
                        g for g in goals
                        if g["id"] != goal["id"]
                    ]

                    persist()
                    st.rerun()


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Notes Wave · Your personal learning workspace"
)