import os
import uuid
import time
from flask import Flask, render_template, request, jsonify
import pandas as pd
from utils.cleaner import clean_data
from utils.fd_checker import FunctionalDependencyChecker
from utils.first_nf_checker import to_first_nf
from utils.second_nf_checker import SecondNFChecker
from utils.third_nf_checker import Semantic3NFPrefixDecomposer
from utils.er_generator import generate_er_diagram
from tabulate import tabulate

app = Flask(__name__)
app.secret_key = "secret"
UPLOAD_FOLDER = 'uploads'
ER_FOLDER = os.path.join('static', 'er_diagrams')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ER_FOLDER, exist_ok=True)

def step_order(step):
    """Defines the ETL hierarchy order (lower is earlier)."""
    order = {
        "clean": 0,
        "fd": 1,
        "1nf": 2,
        "2nf": 3,
        "3nf": 4,
        "er": 5
    }
    return order.get(step, -1)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    file = request.files.get('csv')
    if file and file.filename.endswith('.csv'):
        abspath = save_temp_file(file)
        df = pd.read_csv(abspath)
        html = f"<h4>Uploaded: {file.filename}</h4><pre>Rows: {df.shape[0]}, Columns: {df.shape[1]}</pre>"
        return jsonify({"csv_path": abspath, "html": html})
    else:
        return jsonify({"error": "Please upload a valid CSV file."}), 400

def save_temp_file(file):
    tempname = f"{uuid.uuid4().hex}_{file.filename}"
    path = os.path.join(UPLOAD_FOLDER, tempname)
    file.save(path)
    return os.path.abspath(path)

@app.route("/run_etl", methods=["POST"])
def run_etl():
    data = request.json
    csv_path = data.get("csv_path")
    steps = data.get("steps", [])
    if not csv_path or not steps:
        return jsonify({"error": "Missing CSV or steps"}), 400

    # ETL hierarchy
    canonical = ["clean", "fd", "1nf", "2nf", "3nf", "er"]

    # Always require clean to be first
    if steps[0] != "clean":
        msg = "Without cleaning it will generate irrelevant ER Diagram. So follow the process: Clean → FD → 1NF → 2NF → 3NF → ER."
        return jsonify({"error": msg, "blocked_step": steps[0]})

    # If ER is requested, ensure 3NF is present before it
    if "er" in steps:
        er_idx = steps.index("er")
        if "3nf" not in steps[:er_idx]:
            msg = "Complete 3NF before generating an ER Diagram."
            return jsonify({"error": msg, "blocked_step": "er"})

    # Check for "going down" the hierarchy after a higher order step
    # Find the highest order step selected so far
    max_order = max([step_order(step) for step in steps])
    for idx, step in enumerate(steps):
        # If any step is less than the highest order (i.e., user went back down), block
        if step_order(step) < max_order and idx == len(steps) - 1:
            msg = f"You have already selected a higher ETL step. Please follow the order: Clean → FD → 1NF → 2NF → 3NF → ER."
            return jsonify({"error": msg, "blocked_step": step})

    df = pd.read_csv(csv_path)
    result = {}
    current_df = df.copy()
    fds = []
    tables = None
    latest_csv = csv_path

    for step in steps:
        if step == "clean":
            current_df, info = clean_data(current_df)
            result["clean"] = {
                "html": tabulate(current_df, headers="keys", tablefmt="html", showindex=False),
                "info": str(info)
            }
            latest_csv = csv_path.replace(".csv", f"_clean_{uuid.uuid4().hex[:6]}.csv")
            current_df.to_csv(latest_csv, index=False)
        elif step == "fd":
            checker = FunctionalDependencyChecker(current_df)
            fds = checker.find_all_fds(max_lhs_size=2)
            fd_table = [[" ,".join(lhs), " ,".join(rhs)] for lhs, rhs in fds]
            fd_html = tabulate(fd_table, headers=["LHS", "RHS"], tablefmt='html')
            result["fd"] = {"html": fd_html, "fds": fds}
        elif step == "1nf":
            current_df, summary = to_first_nf(current_df)
            table_html = tabulate(current_df, headers='keys', tablefmt='html', showindex=False)
            result["1nf"] = {
                "html": f"<h4>Table in 1NF</h4>{table_html}" +
                        (f"<div class='nf-status'><b>Info: </b>{summary}</div>" if summary else "")
            }
            latest_csv = csv_path.replace(".csv", f"_1nf_{uuid.uuid4().hex[:6]}.csv")
            current_df.to_csv(latest_csv, index=False)
        elif step == "2nf":
            pk = [current_df.columns[0]]
            if not fds:
                checker = FunctionalDependencyChecker(current_df)
                fds = checker.find_all_fds(max_lhs_size=2)
            checker2 = SecondNFChecker(current_df, pk, fds)
            violations = checker2.get_violations()
            is_2nf = checker2.is_2nf()
            table_html = tabulate(current_df, headers='keys', tablefmt='html', showindex=False)
            status_msg = "<b>Table is in 2NF.</b>" if is_2nf else "<b>Table violates 2NF.</b>"
            violations_msg = ""
            if violations:
                violations_msg = "<ul>" + "".join(
                    f"<li>{', '.join(v['lhs'])} &rarr; {', '.join(v['rhs'])}</li>" for v in violations
                ) + "</ul>"
            result["2nf"] = {
                "html": f"<h4>Table for 2NF Check</h4>{table_html}"
                        + f"<div class='nf-status'>{status_msg}</div>"
                        + (f"<div><b>Violations:</b>{violations_msg}</div>" if violations_msg else "")
                        + f"<div><b>Primary Key:</b> {', '.join(pk)}</div>"
            }
        elif step == "3nf":
            decomposer = Semantic3NFPrefixDecomposer(current_df)
            decomposer.decompose_3nf()
            tables = decomposer.tables
            tables_html = decomposer.get_tables_tabular_html()
            result["3nf"] = {
                "html": f"<h4>3NF Decomposition</h4>{tables_html}"
            }
        elif step == "er":
            decomposer = Semantic3NFPrefixDecomposer(current_df)
            decomposer.decompose_3nf()
            tables = decomposer.tables
            safe_basename = os.path.splitext(os.path.basename(csv_path))[0]
            timestamp = int(time.time())
            er_filename = f"er_diagram_{safe_basename}_{timestamp}"
            er_image_fullpath = generate_er_diagram(
                tables,
                output_folder=ER_FOLDER,
                filename=er_filename
            )
            er_image_path = f"er_diagrams/{er_filename}.png"
            result["er"] = {
                "html": f"<img src='/static/{er_image_path}' class='er-diagram'><br><a href='/static/{er_image_path}' download>Download ER Diagram</a>"
            }
    result["latest_csv"] = latest_csv
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True,port=5002)  
