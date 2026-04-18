"""
-----------------------------------------------------------------------------
FILE     : OS_Scheduler_Pro_v6.py
BUILD    : 6.6.6 [Stable Release]
AUTHOR   : Nosrat Jahan
ACADEMIC : BSc in Computer Science & Engineering
-----------------------------------------------------------------------------
"""

import threading
import webbrowser
from flask import Flask, render_template_string

app = Flask(__name__)

# Enhanced UI with AJAX-style Clear Functionality
LAYOUT_V6 = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OS Scheduler - Nosrat Jahan</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --panel-color: #1e293b;
            --text-primary: #f8fafc;
            --neon-accent: #10b981;
            --btn-blue: #2563eb;
            --btn-purple: #7c3aed;
            --btn-reset: #eb4d4b;
        }

        .light-gray-theme {
            --bg-color: #f1f5f9;
            --panel-color: #ffffff;
            --text-primary: #1e293b;
            --neon-accent: #059669;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-primary);
            font-family: 'Inter', 'Segoe UI', sans-serif;
            margin: 0;
            transition: all 0.4s ease;
        }

        header {
            background: var(--panel-color);
            padding: 40px 20px;
            text-align: center;
            border-bottom: 3px solid var(--neon-accent);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        }

        .dashboard-container {
            max-width: 1100px;
            margin: 40px auto;
            padding: 0 20px;
        }

        .input-hub {
            background: var(--panel-color);
            padding: 35px;
            border-radius: 16px;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            justify-content: center;
            align-items: center;
        }

        input {
            padding: 14px;
            border-radius: 10px;
            border: 1px solid #475569;
            background: var(--bg-color);
            color: var(--text-primary);
            width: 200px;
            outline: none;
            text-align: center;
        }

        button {
            padding: 14px 24px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 700;
            text-transform: uppercase;
            transition: 0.2s;
        }

        .fcfs-trigger { background: var(--btn-blue); color: #fff; }
        .rr-trigger { background: var(--btn-purple); color: #fff; }
        .reset-trigger { background: var(--btn-reset); color: #fff; }
        .theme-trigger { background: #64748b; color: #fff; }

        button:hover { filter: brightness(1.2); transform: translateY(-2px); }

        .chart-viewport {
            margin: 50px 0;
            display: flex;
            height: 90px;
            border-radius: 12px;
            overflow: hidden;
            border: 2px solid var(--neon-accent);
            background: rgba(0,0,0,0.2);
        }

        .block-unit {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background: linear-gradient(to bottom right, var(--btn-blue), #1e40af);
            color: white;
            font-weight: 800;
            border-right: 1px solid rgba(255,255,255,0.1);
        }

        .time-step { font-size: 0.7rem; font-weight: 400; margin-top: 5px; opacity: 0.8; }

        table {
            width: 100%;
            border-collapse: collapse;
            background: var(--panel-color);
            border-radius: 14px;
            overflow: hidden;
            margin-top: 30px;
        }

        th { background: #334155; padding: 20px; color: #fff; }
        td { padding: 18px; border-bottom: 1px solid rgba(0,0,0,0.05); text-align: center; }

        footer {
            margin-top: 100px;
            padding: 30px;
            text-align: center;
            background: var(--panel-color);
            border-top: 3px solid var(--neon-accent);
            font-size: 0.85rem;
            color: #94a3b8;
        }
    </style>
</head>
<body onkeydown="handleGlobalEnter(event)">

    <header>
        <div style="font-size: 2.5rem; font-weight: 900; color: var(--neon-accent);">PROCESS SCHEDULER ENGINE</div>
        <div style="font-size: 1rem; opacity: 0.6; margin-top: 8px;">Academic Simulation Tool v6.6.6</div>
    </header>

    <div class="dashboard-container">
        <div class="input-hub">
            <input type="text" id="burst-list" placeholder="Burst Times (e.g. 5, 8, 2)">
            
            <input type="number" id="quantum-val" value="0" 
                   onfocus="if(this.value==='0')this.value='';" 
                   onblur="if(this.value==='')this.value='0';">
            
            <div class="btn-stack" style="display:flex; gap:10px;">
                <button class="fcfs-trigger" onclick="runSimulation('FCFS')">FCFS</button>
                <button class="rr-trigger" onclick="runSimulation('RR')">Round Robin</button>
                <button class="reset-trigger" onclick="smartReset()">RESET</button>
                <button class="theme-trigger" onclick="document.body.classList.toggle('light-gray-theme')">Theme</button>
            </div>
        </div>

        <h2 id="view-label" style="text-align: center; margin-top: 40px;"></h2>
        <div id="visual-output"></div>

        <table id="data-table" style="display: none;">
            <thead>
                <tr>
                    <th>Process ID</th>
                    <th>Burst Time</th>
                    <th>Waiting Time</th>
                    <th>Turnaround Time</th>
                </tr>
            </thead>
            <tbody id="table-entries"></tbody>
        </table>
    </div>

    <footer>
        v6.6.6 | Engineered by Nosrat Jahan | BSc in CSE | 2026
    </footer>

    <script>
        // Smart Reset Function to clear data without reloading
        function smartReset() {
            document.getElementById('burst-list').value = '';
            document.getElementById('quantum-val').value = '0';
            document.getElementById('view-label').innerText = '';
            document.getElementById('visual-output').innerHTML = '';
            document.getElementById('data-table').style.display = 'none';
            document.getElementById('table-entries').innerHTML = '';
            console.log("System Metrics Reset Successfully.");
        }

        function handleGlobalEnter(e) {
            if(e.key === 'Enter') {
                const isRR = document.activeElement.id === 'quantum-val';
                runSimulation(isRR ? 'RR' : 'FCFS');
            }
        }

        function runSimulation(algo) {
            const raw = document.getElementById('burst-list').value;
            const tq = parseInt(document.getElementById('quantum-val').value) || 0;
            
            if(!raw) { alert("Core Alert: Burst times required!"); return; }
            if(algo === 'RR' && tq <= 0) { alert("Quantum must be greater than 0 for Round Robin!"); return; }
            
            const burstData = raw.split(',').map(n => parseInt(n.trim())).filter(n => !isNaN(n));
            const jobs = burstData.map((b, i) => ({ id: `P${i+1}`, burst: b }));
            
            let timeline = [];
            let metrics = [];
            let clock = 0;

            if(algo === 'FCFS') {
                jobs.forEach(j => {
                    timeline.push({ id: j.id, start: clock, end: clock + j.burst });
                    metrics.push({ id: j.id, burst: j.burst, wait: clock, tat: clock + j.burst });
                    clock += j.burst;
                });
            } else {
                let rem = jobs.map(j => ({ ...j }));
                metrics = jobs.map(j => ({ ...j, wait: 0, tat: 0 }));
                let activeCount = jobs.length;

                while(activeCount > 0) {
                    rem.forEach((j, idx) => {
                        if(j.burst > 0) {
                            let slice = Math.min(j.burst, tq);
                            timeline.push({ id: j.id, start: clock, end: clock + slice });
                            clock += slice;
                            j.burst -= slice;
                            if(j.burst === 0) {
                                activeCount--;
                                metrics[idx].tat = clock;
                                metrics[idx].wait = clock - metrics[idx].burst;
                            }
                        }
                    });
                }
            }
            renderUI(algo, timeline, metrics);
        }

        function renderUI(algo, timeline, metrics) {
            document.getElementById('view-label').innerText = algo + " Analysis Complete";
            document.getElementById('data-table').style.display = 'table';
            const output = document.getElementById('visual-output');
            output.innerHTML = '<div class="chart-viewport" id="flow-container"></div>';
            const flow = document.getElementById('flow-container');

            timeline.forEach(step => {
                const node = document.createElement('div');
                node.className = 'block-unit';
                node.style.flex = step.end - step.start;
                node.style.minWidth = "45px";
                node.innerHTML = `<span>${step.id}</span><span class="time-step">${step.start}-${step.end}</span>`;
                flow.appendChild(node);
            });

            const body = document.getElementById('table-entries');
            body.innerHTML = '';
            metrics.forEach(m => {
                body.innerHTML += `<tr><td>${m.id}</td><td>${m.burst}</td><td>${m.wait}</td><td>${m.tat}</td></tr>`;
            });
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(LAYOUT_V6)

def start_browser():
    target_addr = "127.0.0.1"
    target_port = 6060
    print(f"\\n{'='*60}\\n  OS SCHEDULER ENGINE [v6.6.6]\\n  STATUS: ACTIVE\\n  LINK: http://{target_addr}:{target_port}\\n{'='*60}\\n")
    webbrowser.open(f"http://{target_addr}:{target_port}")

if __name__ == "__main__":
    threading.Timer(1.2, start_browser).start()
    app.run(host="127.0.0.1", port=6060, debug=False)
