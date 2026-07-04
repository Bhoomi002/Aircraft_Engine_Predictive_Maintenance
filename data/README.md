# Dataset

This project uses the **NASA C-MAPSS (Commercial Modular Aero-Propulsion System Simulation) FD001 dataset** for aircraft engine Remaining Useful Life (RUL) prediction.

## Dataset Source
The dataset was downloaded from Kaggle:

🔗 https://www.kaggle.com/datasets/behrad3d/nasa-cmaps

## Files Used
- `train_FD001.txt` – Training run-to-failure trajectories.
- `test_FD001.txt` – Test trajectories truncated before failure.
- `RUL_FD001.txt` – Ground-truth Remaining Useful Life values for test engines.

## Dataset Description
The FD001 subset contains:
- Multiple engine operational cycles
- Multivariate sensor measurements
- Engine degradation patterns
- Remaining Useful Life (RUL) targets

## Note
The dataset files are **not included in this repository** to keep the repository lightweight. Please download the dataset from the link above and place the files inside the `data/` directory before running the project.

Expected structure:

```text
data/
├── train_FD001.txt
├── test_FD001.txt
└── RUL_FD001.txt
