"""QA Copilot — AI assistant for manual QA work.

Run with: streamlit run app.py
"""

import streamlit as st

from core import llm
from core.export import markdown_table_to_csv
from core.history import delete_analysis, list_analyses, save_analysis
from core.prompts import render_prompt

st.set_page_config(page_title="QA Copilot", page_icon="🧪", layout="wide")

# ---------- Sidebar: settings ----------
with st.sidebar:
    st.title("🧪 QA Copilot")
    st.caption("AI assistant for user story analysis, test design and bug reporting.")

    language = st.selectbox("Output language", ["Spanish", "English"])
    detail_level = st.selectbox(
        "Detail level",
        ["junior", "senior"],
        help="junior = explains the reasoning · senior = concise, artifacts only",
    )
    model_label = st.selectbox("Model", list(llm.MODELS.keys()))
    model = llm.MODELS[model_label]

    if llm.get_api_key() is None:
        st.warning(
            "**No API key configured.**\n\n"
            "1. Create a free key at [aistudio.google.com](https://aistudio.google.com)\n"
            "2. Copy `.env.example` to `.env`\n"
            "3. Paste your key there and restart the app"
        )

# ---------- Helpers ----------

def run_generation(state_key: str, prompt_name: str, user_input: str) -> None:
    """Call the API and store the result (or error) in session state."""
    prompt = render_prompt(
        prompt_name, input=user_input, language=language, detail_level=detail_level
    )
    try:
        with st.spinner("Generating..."):
            st.session_state[state_key] = llm.generate(prompt, model=model)
        st.session_state.pop(state_key + "_error", None)
        try:
            save_analysis(
                prompt_name, user_input, st.session_state[state_key],
                language, detail_level, model,
            )
        except Exception:
            st.warning("The result could not be saved to history (it is still shown below).")
    except llm.LLMError as exc:
        st.session_state[state_key + "_error"] = str(exc)
        st.session_state.pop(state_key, None)


def show_result(state_key: str, download_name: str, with_csv: bool = False) -> None:
    """Render the stored result with download buttons, or the stored error."""
    error = st.session_state.get(state_key + "_error")
    if error:
        st.error(error)
        return
    result = st.session_state.get(state_key)
    if not result:
        return
    st.markdown(result)
    st.divider()
    col1, col2 = st.columns(2)
    col1.download_button(
        "⬇️ Download Markdown", result, file_name=f"{download_name}.md",
        key=state_key + "_md",
    )
    if with_csv:
        csv_text = markdown_table_to_csv(result)
        if csv_text:
            col2.download_button(
                "⬇️ Download CSV (test case table)", csv_text,
                file_name=f"{download_name}.csv", key=state_key + "_csv",
            )


# ---------- Main layout ----------
tab_analysis, tab_gaps, tab_tests, tab_bug, tab_history = st.tabs(
    ["📋 Story Analysis", "🔍 Gap Finder", "✅ Test Cases", "🐞 Bug Report", "📚 History"]
)

STORY_HINT = (
    "As a registered user, I want to reset my password via email, "
    "so that I can regain access to my account."
)

with tab_analysis:
    st.subheader("Analyze a user story")
    story = st.text_area("User story", key="story_analysis", height=180, placeholder=STORY_HINT)
    if st.button("Analyze story", type="primary", disabled=not story.strip()):
        run_generation("result_analysis", "analyze_story", story)
    show_result("result_analysis", "story_analysis")

with tab_gaps:
    st.subheader("Find gaps in a user story")
    story = st.text_area("User story", key="story_gaps", height=180, placeholder=STORY_HINT)
    if st.button("Find gaps", type="primary", disabled=not story.strip()):
        run_generation("result_gaps", "find_gaps", story)
    show_result("result_gaps", "gap_analysis")

with tab_tests:
    st.subheader("Generate test cases from a user story")
    story = st.text_area("User story", key="story_tests", height=180, placeholder=STORY_HINT)
    if st.button("Generate test cases", type="primary", disabled=not story.strip()):
        run_generation("result_tests", "test_cases", story)
    show_result("result_tests", "test_cases", with_csv=True)

with tab_bug:
    st.subheader("Write a bug report from an informal description")
    bug = st.text_area(
        "Describe the problem in your own words",
        key="bug_input", height=180,
        placeholder="When I leave the name field empty and press Save, nothing happens — no error, no save.",
    )
    if st.button("Write bug report", type="primary", disabled=not bug.strip()):
        run_generation("result_bug", "bug_report", bug)
    show_result("result_bug", "bug_report")

TOOL_LABELS = {
    "analyze_story": "📋 Story Analysis",
    "find_gaps": "🔍 Gap Finder",
    "test_cases": "✅ Test Cases",
    "bug_report": "🐞 Bug Report",
}

with tab_history:
    st.subheader("Saved analyses")
    filter_label = st.selectbox("Filter by tool", ["All"] + list(TOOL_LABELS.values()))
    tool_filter = next(
        (key for key, label in TOOL_LABELS.items() if label == filter_label), None
    )

    entries = list_analyses(tool=tool_filter)
    if not entries:
        st.info("Nothing here yet — every analysis you generate is saved automatically.")
    for entry in entries:
        snippet = entry["input"][:70].replace("\n", " ")
        title = f"{entry['created_at']} · {TOOL_LABELS[entry['tool']]} · {snippet}"
        with st.expander(title):
            st.caption(
                f"{entry['language']} · {entry['detail_level']} · {entry['model']}"
            )
            st.markdown("**Input**")
            st.text(entry["input"])
            st.markdown("**Result**")
            st.markdown(entry["output"])
            st.divider()
            col1, col2, col3 = st.columns(3)
            col1.download_button(
                "⬇️ Markdown", entry["output"],
                file_name=f"{entry['tool']}_{entry['id']}.md",
                key=f"hist_md_{entry['id']}",
            )
            if entry["tool"] == "test_cases":
                csv_text = markdown_table_to_csv(entry["output"])
                if csv_text:
                    col2.download_button(
                        "⬇️ CSV", csv_text,
                        file_name=f"test_cases_{entry['id']}.csv",
                        key=f"hist_csv_{entry['id']}",
                    )
            if col3.button("🗑️ Delete", key=f"hist_del_{entry['id']}"):
                delete_analysis(entry["id"])
                st.rerun()
