# 🧩 ETL_Designer

**Author:** [Antor6910](https://github.com/Antor6910)

An interactive **ETL (Extract–Transform–Load) process designer** that helps visualize and perform database normalization and data cleaning steps in a simple drag-and-drop interface.

---

## 🚀 Project Overview

**ETL_Designer** provides a visual workflow to simulate and execute ETL processes, including:
- **Data Cleaning**
- **Normalization (1NF → 2NF → 3NF)**
- **ER Diagram Generation and Export**

Users can dynamically **select steps from a dropdown menu**, **move process blocks**, and **view results instantly** below each step.  
The final **ER diagram** can be saved for further database design or documentation.

---

## 🧠 Project Mechanism

### 🔹 Step-by-Step Flow

1. **Choose an ETL Step**
   - Select a process (e.g., “Clean Data”, “1NF”, “2NF”, “3NF”, “ER Diagram”) from the dropdown box.

2. **Drag & Arrange**
   - Each selected step appears as a **movable block/button** on the canvas.
   - You can **reorder** or **reconnect** steps visually to adjust the workflow.

3. **View Results**
   - Each transformation step displays **results/output** dynamically beneath the dropdown box.

4. **Generate ER Diagram**
   - After normalization, the tool automatically generates an **Entity–Relationship Diagram**.
   - You can **save/export** the ER Diagram as an image file for documentation.

---

## 🧰 Key Features

✅ Interactive drag-and-drop interface  
✅ Real-time ETL visualization  
✅ Step-based normalization workflow  
✅ Dynamic result preview after each transformation  
✅ ER Diagram generation & export  
✅ Intuitive and beginner-friendly UI  

---

## 📸 Project Demonstration

You can showcase your project visually here 👇  

| Feature | Screenshot |
|----------|-------------|
| Home Interface | ![Home Screenshot](uploads/home_interface.png) |
| Data Cleaning Step | ![Clean Data Screenshot](uploads/clean_data.png) |
| Normalization Process | ![Normalization Screenshot](uploads/normalization_steps.png) |
| ER Diagram Result | ![ER Diagram Screenshot](uploads/er_diagram.png) |

> 🖼️ *Upload your screenshots to the `/uploads` folder and replace the above paths accordingly.*

---

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Antor6910/ETL_Designer.git
   ```

2. **Navigate to the project folder:**
   ```bash
   cd ETL_Designer
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the project:**
   ```bash
   python3 app.py
   ```

5. **Open in browser:**
   ```
   http://localhost:5002
   ```

---

## 🧑‍💻 Technologies Used

- **Frontend:** HTML, CSS, JavaScript  
- **Backend:** Python (Flask)  
- **Database:** MySQL  
- **Visualization:** Custom JS  

---

## 🧩 Folder Structure

```plaintext
ETL_Designer/
├── app/
│   └── app.py                 # Main Flask application and ETL logic
├── static/
│   ├── css/
│   │   └── style.css          # Custom styles for the UI
│   ├── js/
│   │   └── ETL_UI.js          # Interactive ETL pipeline designer logic
│   └── er_diagram/
│       └── er_demo.txt        # Example ER diagram output storage
├── templates/
│   └── index.html             # Main HTML template for the web UI
├── utils/
│   ├── 1NF_Checker.py         # Functions for First Normal Form (1NF) checks
│   ├── 2NF_Checker.py         # Functions for Second Normal Form (2NF) checks
│   ├── 3NF_Checker.py         # Functions for Third Normal Form (3NF) checks
│   ├── data_cleaning.py       # Data cleaning utilities
│   └── er_generator.py        # ER diagram generator logic
├── uploads/                   # Temporary uploaded CSV files (created at runtime)
└── README.md                  # Project documentation (you're reading it!)
```

**Highlights:**
- **app/**: Contains the main backend Flask application.
- **static/**: Static resources like CSS, JS, and generated ER diagrams.
- **templates/**: HTML templates for Flask rendering.
- **utils/**: Modular Python utilities for the ETL and database normalization workflow.
- **uploads/**: Stores user-uploaded CSV files temporarily during processing.

> This structure ensures clear separation of backend, frontend, and data processing logic, making the project easy to extend and maintain.

---

## 👥 Contributor

| Name | GitHub Profile |
|------|----------------|
| **Antor6910** | [https://github.com/Antor6910](https://github.com/Antor6910) |
| **MD. Anas**  | 
| **FTJ Tanju patawary**    |


---

## 🏁 Future Enhancements

- [x] Add multi-table ER diagram relationships  
- [ ] Enable CSV,Txt upload for sample data  
- [ ] Provide export in multiple formats (PNG, PDF, JSON)  
- [ ] Add undo/redo functionality for steps  
- [ ] Include data preview for each normalization stage  

---

## 📜 License

This project is open-source and available under the **MIT License**.  
Feel free to modify and use it for learning or development purposes.

---

⭐ **If you like this project, don't forget to star the repository!**
