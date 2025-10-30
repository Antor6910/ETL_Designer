let csvPath = null;
let pipelineSteps = [];
const stepOrder = ["clean", "fd", "1nf", "2nf", "3nf", "er"];
const stepNames = {
    clean: "Clean",
    fd: "FD",
    "1nf": "1NF",
    "2nf": "2NF",
    "3nf": "3NF",
    er: "ER"
};
let stepPositions = {};
let dragFlags = {};
let csvUploaded = false;

// Helper: find the first red (reverse) arrow index
function findFirstRedArrowIndex(steps) {
    const canonicalOrder = stepOrder;
    for (let i = 0; i < steps.length - 1; i++) {
        let fromIdx = canonicalOrder.indexOf(steps[i]);
        let toIdx = canonicalOrder.indexOf(steps[i + 1]);
        if (toIdx < fromIdx) return i + 1;
    }
    return -1;
}

function setStepButtonsEnabled(enabled) {
    document.querySelectorAll('.etl-sidebar-btn').forEach(btn => {
        btn.disabled = !enabled;
        btn.style.opacity = enabled ? "1" : "0.5";
        btn.style.pointerEvents = enabled ? "auto" : "none";
    });
}

function clearPipelineCanvas() {
    document.getElementById("etl-pipeline-canvas").innerHTML = "";
    jsPlumb.reset();
}

function showMessage(msg, color = "red") {
    let resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `<div style="color:${color};margin:8px 0;font-weight:bold;">${msg}</div>` + resultsDiv.innerHTML;
}

function renderPipeline() {
    clearPipelineCanvas();
    const canvas = document.getElementById("etl-pipeline-canvas");
    // Set the canvas smaller
    canvas.style.width = "650px";
    canvas.style.height = "390px";
    canvas.style.minHeight = "250px";
    canvas.style.minWidth = "400px";
    let left = 30, top = 100;

    pipelineSteps.forEach((step, idx) => {
        const btn = document.createElement("div");
        btn.className = "etl-pipeline-step";
        btn.textContent = stepNames[step];
        btn.id = "pipeline-step-" + step;
        btn.style.position = "absolute";
        let pos = stepPositions[step];
        if (pos) {
            btn.style.left = pos.x + "px";
            btn.style.top = pos.y + "px";
        } else {
            btn.style.left = left + "px";
            btn.style.top = top + "px";
            stepPositions[step] = { x: left, y: top };
        }
        btn.dataset.step = step;
        dragFlags[step] = false;
        btn.onmousedown = () => { dragFlags[step] = false; };
        btn.onclick = (e) => {
            if (!dragFlags[step]) {
                fetchResultForStep(idx);
                document.querySelectorAll('.etl-pipeline-step').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
            }
        };
        canvas.appendChild(btn);
        left += 110;
    });

    // Make pipeline step nodes draggable
    interact('.etl-pipeline-step').draggable({
        modifiers: [
            interact.modifiers.restrictRect({
                restriction: 'parent'
            })
        ],
        inertia: true,
        listeners: {
            move(event) {
                const target = event.target;
                let step = target.dataset.step;
                let x = (parseFloat(target.style.left) || 0) + event.dx;
                let y = (parseFloat(target.style.top) || 0) + event.dy;
                target.style.left = x + "px";
                target.style.top = y + "px";
                stepPositions[step] = { x, y };
                dragFlags[step] = true;
                jsPlumb.repaintEverything();
            }
        }
    });

    // Draw arrows and handle flow break logic
    const canonicalOrder = stepOrder;
    let showSkipMessage = false;
    let showReverseMessage = false;
    let processBlocked = false;
    let blockedIdx = -1;
    let arrowColors = [];

    // Detect first red arrow and mark all after as blocked
    for (let i = 0; i < pipelineSteps.length - 1; ++i) {
        let fromStep = pipelineSteps[i];
        let toStep = pipelineSteps[i + 1];
        let fromIdx = canonicalOrder.indexOf(fromStep);
        let toIdx = canonicalOrder.indexOf(toStep);
        let color = "#228B22"; // green
        if (toIdx < fromIdx) {
            color = "red";
            showReverseMessage = true;
            processBlocked = true;
            blockedIdx = i + 1;
        } else if ((toIdx - fromIdx) > 1) {
            color = "#0070ad"; // professional blue
            showSkipMessage = true;
        }
        arrowColors.push(color);
    }

    setTimeout(() => {
        jsPlumb.ready(function () {
            jsPlumb.setContainer(canvas);
            for (let i = 0; i < pipelineSteps.length - 1; ++i) {
                let fromStep = pipelineSteps[i];
                let toStep = pipelineSteps[i + 1];
                let color = arrowColors[i];
                jsPlumb.connect({
                    source: "pipeline-step-" + fromStep,
                    target: "pipeline-step-" + toStep,
                    anchors: ["AutoDefault", "AutoDefault"],
                    endpoint: "Blank",
                    connector: ["Bezier", { curviness: 40 }],
                    paintStyle: { stroke: color, strokeWidth: 4 },
                    overlays: [
                        [
                            "Arrow",
                            {
                                width: 15,
                                length: 18,
                                location: 1,
                                foldback: 0.8,
                                paintStyle: { fill: color, stroke: color }
                            }
                        ]
                    ]
                });
            }
        });
        // Show skip/reverse message if necessary
        let resultsDiv = document.getElementById('results');
        if (showSkipMessage) {
            let msg = `<div style="color:#0070ad;margin:8px 0;font-weight:bold;">
                You skipped steps. Please follow the canonical order: Clean → FD → 1NF → 2NF → 3NF → ER.
            </div>`;
            if (!resultsDiv.innerHTML.includes('You skipped steps')) {
                resultsDiv.innerHTML = msg + resultsDiv.innerHTML;
            }
        }
        if (showReverseMessage) {
            let msg = `<div style="color:red;margin:8px 0;font-weight:bold;">
                You selected a lower-order ETL step after a higher one. Please proceed only upward in the ETL pipeline.
            </div>`;
            if (!resultsDiv.innerHTML.includes('You selected a lower-order ETL step')) {
                resultsDiv.innerHTML = msg + resultsDiv.innerHTML;
            }
        }
    }, 100);

    // Store processBlocked globally for fetchResultForStep
    renderPipeline.processBlocked = processBlocked;
    renderPipeline.blockedIdx = blockedIdx;
}

function fetchResultForStep(idx) {
    // Block if trying to view results after red arrow
    if (typeof renderPipeline.processBlocked !== "undefined" &&
        renderPipeline.processBlocked &&
        typeof renderPipeline.blockedIdx !== "undefined" &&
        renderPipeline.blockedIdx !== -1 &&
        idx >= renderPipeline.blockedIdx) {
        // Don't show any result
        let resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = ""; // Clear results
        // The red message is already shown by renderPipeline
        return;
    }

    if (!csvPath || pipelineSteps.length === 0) return;
    let stepsToRun = pipelineSteps.slice(0, idx + 1);

    fetch('/run_etl', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            csv_path: csvPath,
            steps: stepsToRun
        })
    })
        .then(res => res.json())
        .then(data => {
            let resultsDiv = document.getElementById('results');
            if (data.error) {
                showMessage(data.error, "red");
                return;
            }
            if (data.latest_csv) {
                csvPath = data.latest_csv;
            }
            let step = stepsToRun[stepsToRun.length - 1];
            resultsDiv.innerHTML = "";
            if (data[step]) {
                let stepData = data[step];
                if (stepData.html) resultsDiv.innerHTML += stepData.html;
            } else {
                resultsDiv.innerHTML = "<em>No result for this step.</em>";
            }
            renderPipeline();
        });
}

document.querySelectorAll('.etl-sidebar-btn').forEach(btn => {
    btn.onclick = function () {
        if (!csvUploaded) return;
        let step = btn.dataset.step;
        // Add only if not already present
        if (pipelineSteps.indexOf(step) === -1) {
            pipelineSteps.push(step);
            renderPipeline();
        }
        // Always fetch result for the last step (including ER)
        fetchResultForStep(pipelineSteps.length - 1);
    };
});

document.getElementById('clear-pipeline').onclick = function () {
    pipelineSteps = [];
    stepPositions = {};
    dragFlags = {};
    renderPipeline();
    document.getElementById('results').innerHTML = "";
    document.querySelectorAll('.etl-pipeline-step').forEach(b => b.classList.remove('selected'));
    setStepButtonsEnabled(csvUploaded);
};

let fileInput = document.getElementById('csvUpload');
let fileNameSpan = document.getElementById('csvFileName');
document.querySelector('label[for="csvUpload"]').onclick = function () {
    fileInput.click();
}
fileInput.addEventListener('change', function () {
    let file = fileInput.files[0];
    if (file) {
        fileNameSpan.textContent = file.name;
        let formData = new FormData();
        formData.append('csv', file);
        setStepButtonsEnabled(false);
        fetch('/upload_csv', {
            method: 'POST',
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                csvPath = data.csv_path;
                pipelineSteps = [];
                stepPositions = {};
                dragFlags = {};
                csvUploaded = true;
                renderPipeline();
                document.getElementById('results').innerHTML = "";
                setStepButtonsEnabled(true);
            });
    }
});
setStepButtonsEnabled(false)
