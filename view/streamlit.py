from datetime import datetime
from pathlib import Path
from uuid import uuid4

import streamlit as st


from view.classical_user_study.render import render_classical_study
from view.classical_user_study.suggest import get_leaf_subfolders, prepare_selection
from view.instructions import render_instructions
from view.read import zip_results_dir


st.set_page_config(page_title="User Study", layout="wide")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid4())

if "selection_indices" not in st.session_state:
    quests_root = Path(__file__).resolve().parent / "resources" / "quests"
    leaf_subfolders = get_leaf_subfolders(quests_root)
    st.session_state.selection_indices = prepare_selection(leaf_subfolders)


def main() -> None:
    instructions_tab, classical_tab, export_tab = st.tabs(['Инструкция', 'Исследование', 'Выгрузка'])

    with instructions_tab:
        render_instructions()

    with classical_tab:
        render_classical_study()

    with export_tab:
        timestamp = datetime.now().strftime('%d-%m-%Y-%H_%M_%S')
        st.download_button(
            label='Выгрузить результаты (ZIP)',
            data=zip_results_dir(),
            file_name=f'results_{timestamp}.zip',
            mime='application/zip',
        )

if __name__ == "__main__":
    main()


