<h1 align="center">✈️ Aircraft Engine RUL Prediction System</h1>

<p align="center">
AI-powered Predictive Maintenance using Transformer-GRU and Digital Twin Technology
</p>

---

## 📖 Overview

The **Aircraft Engine Remaining Useful Life (RUL) Prediction System** is an **AI-powered predictive maintenance platform** designed to estimate the remaining operational life of aircraft turbofan engines using **multivariate sensor data**.

The system combines **Transformer** and **GRU deep learning architectures** with **Digital Twin Technology** to provide:

- Accurate **RUL predictions**
- **Real-time engine health monitoring**
- **Maintenance planning support**

The project utilizes **NASA's C-MAPSS FD001 dataset** and provides an interactive **Streamlit dashboard** for engineers and administrators to monitor engine health, analyze degradation trends, and manage maintenance activities.

---

## 🚀 Features

### 🔐 User Authentication
- Secure login system
- Role-based access control
- Engineer and Admin dashboards

### 🤖 AI-Based RUL Prediction
- Transformer-GRU hybrid architecture
- Predicts Remaining Useful Life (RUL)
- Prediction confidence scores

### 🩺 Component Health Monitoring
Monitors critical engine parameters:

- **T2** – Total temperature at fan inlet
- **T24** – Total temperature at LPC outlet
- **T30** – Total temperature at HPC outlet
- **T50** – Total temperature at LPT outlet
- **P2** – Pressure at fan inlet
- **P15** – Pressure in bypass duct
- **P30** – Pressure at HPC outlet
- **Nf** – Physical fan speed

---

## 🧠 Deep Learning Architecture

- **Transformer Encoder**
  - Multi-Head Self Attention
  - Positional Encoding
  - Layer Normalization

- **GRU Layer**
  - Captures temporal dependencies
  - Learns engine degradation patterns

- **Regression Head**
  - Predicts Remaining Useful Life

---

## 📂 Dataset

**NASA C-MAPSS FD001 Dataset**

Files:
- `train_FD001.txt`
- `test_FD001.txt`
- `RUL_FD001.txt`

The dataset contains:

- Engine operational cycles
- Sensor measurements
- Degradation patterns
- Remaining Useful Life targets

---

## 📊 Performance

| Metric | Score |
|--------|--------|
| Validation R² | 0.91 |
| Last-Cycle Test R² | 0.89 |

---
## 📸 Screenshots

### Login Page
![Login](images/login.png)

### Main Dashboard
![Dashboard](images/dashboard.png)

### RUL Prediction
![Prediction](images/prediction.png)

### Multi-Engine Comparison
![Comparison](images/comparison.png)

### Degradation Forecast
![Forecast](images/forecast.png)

---

## ⚙️ Installation

```bash
git clone https://github.com/Bhoomi002/Aircraft_Engine_Predictive_Maintenance.git
cd Aircraft_Engine_Predictive_Maintenance
pip install -r requirements.txt
streamlit run app.py
```

---

## 👩‍💻 Author

**Bhoomika M**

MCA Student, JSS Academy of Technical Education, Bengaluru

📧 mbhoomika00@gmail.com
💼 LinkedIn: https://www.linkedin.com/in/bhoomika-m-80834a327/
