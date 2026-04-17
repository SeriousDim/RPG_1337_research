from __future__ import annotations

import os
import random
from collections import defaultdict
from pathlib import Path
from typing import Sequence


def get_leaf_subfolders(root_dir: str | Path) -> list[str]:
    """Return all leaf subdirectories under *root_dir*.

    A leaf directory is a directory that does not contain any subdirectories.
    For example, if the tree contains:

        /some/dir1/quest1
        /some/dir1/quest2
        /some/dir2/quest1

    and we scan from /some, this function returns the leaf paths only:
        /some/dir1/quest1
        /some/dir1/quest2
        /some/dir2/quest1

    not /some/dir1 or /some/dir2.
    """
    root = Path(root_dir).resolve()
    if not root.exists() or not root.is_dir():
        return []

    leaf_dirs: list[str] = []

    for current_dir, subdirs, _files in os.walk(root):
        current_path = Path(current_dir).resolve()

        if current_path == root:
            continue

        if not subdirs:
            leaf_dirs.append(str(current_path))

    return sorted(leaf_dirs)


def prepare_selection(subfolders: Sequence[str | Path]) -> list[int]:
    """Prepare a randomized index selection grouped by model.

    The input is expected to be a list of quest leaf folders such as:
        /view/resources/quests/model1/quest1

    Here, ``model1`` is treated as the model and ``quest1`` as the quest.

    The output is a flat list of indices into ``subfolders``. The indices are
    arranged in rounds:
    - in each round, each model contributes at most one quest;
    - no model repeats within the same round;
    - quests for each model are chosen randomly;
    - when some models run out of quests, later rounds continue only with the
      remaining models.
    """
    if not subfolders:
        return []

    model_to_indices: dict[str, list[int]] = defaultdict(list)

    for index, folder in enumerate(subfolders):
        folder_path = Path(folder).resolve()
        model_key = str(folder_path.parent)
        model_to_indices[model_key].append(index)

    for indices in model_to_indices.values():
        random.shuffle(indices)

    result: list[int] = []

    while True:
        active_models = [model for model, indices in model_to_indices.items() if indices]
        if not active_models:
            break

        random.shuffle(active_models)

        for model in active_models:
            result.append(model_to_indices[model].pop())

    return result
