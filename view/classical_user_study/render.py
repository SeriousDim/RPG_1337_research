from pathlib import Path

import streamlit as st
import yaml

from view.classical_user_study.criteria import CRITERIA
from view.classical_user_study.suggest import get_leaf_subfolders
from view.read import read_prompt_and_generated_quest
from view.save import save_current_answers


def load_quest_data(quest_path: Path) -> dict[str, object]:
    loaded_data = yaml.safe_load(quest_path.read_text(encoding="utf-8"))
    return loaded_data if isinstance(loaded_data, dict) else {}


def get_quest_section(quest_path: Path) -> dict[str, object]:
    quest_data = load_quest_data(quest_path).get("quest", {})
    return quest_data if isinstance(quest_data, dict) else {}


def to_yaml_text(value: object) -> str:
    if value is None:
        return ""
    return yaml.safe_dump(value, allow_unicode=True, sort_keys=False, indent=8).rstrip()



def get_current_answers(quest_path: Path) -> dict[str, object]:
    return {
        "quest": str(quest_path),
        "metrics": {
            title: st.session_state[f"criterion_{idx}"]
            for idx, (title, _description, _scale) in enumerate(CRITERIA, start=1)
        },
        "comment": st.session_state.get("free_comment", ""),
    }


def reset_ratings_and_comment() -> None:
    for idx, _criterion in enumerate(CRITERIA, start=1):
        st.session_state[f"criterion_{idx}"] = 5
    st.session_state["free_comment"] = ""


def handle_next_click(quest_path: Path) -> None:
    answers = get_current_answers(quest_path)
    save_current_answers(answers)
    st.session_state["current_selection_position"] += 1
    st.session_state["reset_inputs_after_rerun"] = True
    st.rerun()


def render_classical_study() -> None:
    quests_root = Path(__file__).resolve().parents[1] / "resources" / "quests"
    leaf_subfolders = get_leaf_subfolders(quests_root)

    st.session_state.setdefault("current_selection_position", 0)
    for idx, _criterion in enumerate(CRITERIA, start=1):
        st.session_state.setdefault(f"criterion_{idx}", 5)
    st.session_state.setdefault("free_comment", "")

    if st.session_state.pop("reset_inputs_after_rerun", False):
        reset_ratings_and_comment()

    selection_indices = st.session_state.get("selection_indices", [])

    current_selection_position = st.session_state["current_selection_position"]
    selected_quest_path: Path | None = None

    if selection_indices and current_selection_position >= len(selection_indices):
        st.toast("Больше квестов нет, спасибо за участие")
        st.session_state["prompt_context_text"] = ""
        st.session_state["generated_quest_text"] = ""
        st.session_state["quest_objective_text"] = ""
        st.session_state["quest_reward_text"] = ""
        st.session_state["quest_parts_resource_to_deliver_text"] = ""
        st.session_state["quest_explanation_resource_to_deliver_text"] = ""
        st.session_state["quest_parts_enemy_to_face_text"] = ""
        st.session_state["quest_explanation_enemy_to_face_text"] = ""
        st.session_state["quest_parts_destination_text"] = ""
        st.session_state["quest_explanation_destination_text"] = ""
        return


    if selection_indices and leaf_subfolders:
        selected_index = selection_indices[current_selection_position]
        selected_quest_path = Path(leaf_subfolders[selected_index]) / "content.yaml"
        prompt_text, generated_quest_text = read_prompt_and_generated_quest(selected_quest_path)
        quest_data = get_quest_section(selected_quest_path)

        last_logged_quest_path = st.session_state.get("last_logged_quest_path")
        if last_logged_quest_path != str(selected_quest_path):
            print(f"Reading {selected_quest_path}")
            st.session_state["last_logged_quest_path"] = str(selected_quest_path)
            st.session_state["prompt_context_text"] = prompt_text
            st.session_state["generated_quest_text"] = generated_quest_text
            st.session_state["quest_objective_text"] = str(quest_data.get("objective_description", ""))

            reward_data = quest_data.get("reward", {})
            st.session_state["quest_reward_text"] = str(reward_data.get("item_name", "")) if isinstance(reward_data, dict) else ""

            parts_data = quest_data.get("parts", {})
            explanation_data = quest_data.get("explanation", {})

            resource_to_deliver_parts = parts_data.get("resource_to_deliver", {}) if isinstance(parts_data, dict) else {}
            resource_to_deliver_explanation = explanation_data.get("resource_to_deliver", {}) if isinstance(explanation_data, dict) else {}
            enemy_to_face_parts = parts_data.get("enemy_to_face", {}) if isinstance(parts_data, dict) else {}
            enemy_to_face_explanation = explanation_data.get("enemy_to_face", {}) if isinstance(explanation_data, dict) else {}
            destination_parts = parts_data.get("destination", {}) if isinstance(parts_data, dict) else {}
            destination_explanation = explanation_data.get("destination", {}) if isinstance(explanation_data, dict) else {}

            st.session_state["quest_parts_resource_to_deliver_text"] = to_yaml_text(resource_to_deliver_parts)
            st.session_state["quest_explanation_resource_to_deliver_text"] = to_yaml_text(resource_to_deliver_explanation)
            st.session_state["quest_parts_enemy_to_face_text"] = to_yaml_text(enemy_to_face_parts)
            st.session_state["quest_explanation_enemy_to_face_text"] = to_yaml_text(enemy_to_face_explanation)
            st.session_state["quest_parts_destination_text"] = to_yaml_text(destination_parts)
            st.session_state["quest_explanation_destination_text"] = to_yaml_text(destination_explanation)


    st.markdown(
        """
        <style>
        .criterion-card {
            padding: 0.25rem 0 0.75rem 0;
            border-bottom: 1px solid rgba(250, 250, 250, 0.12);
            margin-bottom: 0.75rem;
        }
        .criterion-title {
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }
        .criterion-description {
            font-size: 0.92rem;
            opacity: 0.85;
            margin-bottom: 0.4rem;
            line-height: 1.35;
        }
        .criterion-scale {
            font-size: 0.85rem;
            opacity: 0.7;
            margin-bottom: 0.3rem;
            font-style: italic;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left_col, middle_col, right_col = st.columns([1.05, 1.05, 1.0], gap="small")

    with left_col:
        st.text_area(
            label="Цель квеста",
            value=st.session_state.get("quest_objective_text", ""),
            height=90,
            key="quest_objective_text",
        )
        st.text_area(
            label="Награда за квест",
            value=st.session_state.get("quest_reward_text", ""),
            height=90,
            key="quest_reward_text",
        )
        st.header("Промпт и контекст")
        st.text_area(
            label="Промпт и контекст",
            value=st.session_state.get("prompt_context_text", ""),
            height=2500,
            key="prompt_context_text",
            label_visibility="collapsed",
            placeholder="Здесь отображается промпт и контекст исследования...",
        )

    with middle_col:
        st.header("Диалоги сгенерированного квеста")
        
        st.markdown(
            """
            <div class="criterion-title">Получение задания на доставку</div>
            """,
            unsafe_allow_html=True
        )
        st.text_area(
            label="",
            value=st.session_state.get("quest_parts_resource_to_deliver_text", ""),
            height=650,
            key="quest_parts_resource_to_deliver_text",
        )

        st.markdown(
            """
            <div class="criterion-title">Встреча с противником</div>
            """,
            unsafe_allow_html=True
        )
        st.text_area(
            label="",
            value=st.session_state.get("quest_parts_enemy_to_face_text", ""),
            height=650,
            key="quest_parts_enemy_to_face_text",
        )

        st.markdown(
            """
            <div class="criterion-title">Доставка персонажу (завершение квеста)</div>
            """,
            unsafe_allow_html=True
        )
        st.text_area(
            label="",
            value=st.session_state.get("quest_parts_destination_text", ""),
            height=650,
            key="quest_parts_destination_text",
        )


    with right_col:
        st.header("Критерии оценки")

        if st.button("Далее", use_container_width=True, key="next_button_1"):
            if selected_quest_path is not None:
                handle_next_click(selected_quest_path)

        for idx, (title, description, scale) in enumerate(CRITERIA, start=1):
            st.markdown(
                f"""
                <div class="criterion-card">
                    <div class="criterion-title">{idx}. {title}</div>
                    <div class="criterion-description">{description}</div>
                    <div class="criterion-scale">({scale})</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.slider(
                label=title,
                min_value=1,
                max_value=10,
                value=5,
                key=f"criterion_{idx}",
                label_visibility="collapsed",
            )

        st.text_area(
            label="Свободный комментарий (опционально)",
            value=st.session_state.get("free_comment", ""),
            height=140,
            key="free_comment",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Далее", use_container_width=True, key="next_button_2"):
            if selected_quest_path is not None:
                handle_next_click(selected_quest_path)


