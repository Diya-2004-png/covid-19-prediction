from flask import Flask, request, jsonify, render_template_string
import numpy as np
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)

# ======================
# ML MODEL
# ======================
X = np.array([
    [1,1,1,0,101,92,45,1],
    [1,1,1,1,102,88,60,1],
    [0,1,0,0,98,97,25,0],
    [1,0,1,1,100,90,50,1],
    [0,0,0,0,97,99,20,0],
    [1,1,0,1,101,89,55,1]
])
y = np.array([1,1,0,1,0,1])

model = RandomForestClassifier()
model.fit(X, y)

# ======================
# FRONTEND
# ======================
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>AI Health Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body{
    margin:0;
    font-family:'Segoe UI';
    background:linear-gradient(135deg,#141e30,#243b55);
    color:white;
}

/* Layout */
.container{
    display:flex;
    height:100vh;
}

/* LEFT PANEL */
.left{
    width:300px;
    padding:25px;
    background:rgba(255,255,255,0.05);
    backdrop-filter:blur(10px);
}/* LOGO CONTAINER */
.logo-container{
    text-align:center;
    margin-bottom:20px;
}

/* LOGO IMAGE */
.logo{
    width:130px;
    border-radius:12px;
    animation: pulseGlow 2s infinite;
}

/* TAGLINE */
.tagline{
    font-size:12px;
    color:#bbb;
}

/* 🔥 PULSE + GLOW ANIMATION */
@keyframes pulseGlow{
    0%{
        transform: scale(1);
        box-shadow: 0 0 10px #00f7ff;
    }
    50%{
        transform: scale(1.08);
        box-shadow: 0 0 25px #00f7ff, 0 0 40px #00c3ff;
    }
    100%{
        transform: scale(1);
        box-shadow: 0 0 10px #00f7ff;
    }
}

/* RIGHT PANEL */
.right{
    flex:1;
    padding:25px;
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:20px;
}

/* CARD */
.card{
    background:rgba(255,255,255,0.08);
    padding:15px;
    border-radius:15px;
    box-shadow:0 10px 30px rgba(0,0,0,0.3);
    animation:fadeIn 1s ease;
}

/* INPUT */
input{
    width:100%;
    padding:10px;
    margin:6px 0;
    border:none;
    border-radius:8px;
}

/* BUTTON */
button{
    width:100%;
    padding:12px;
    margin-top:10px;
    background:#00f7ff;
    border:none;
    border-radius:8px;
    cursor:pointer;
    transition:0.3s;
}
button:hover{
    transform:scale(1.05);
}

/* GAUGE TEXT */
.gauge-container{
    position:relative;
}
#riskValue{
    position:absolute;
    top:50%;
    left:50%;
    transform:translate(-50%,-50%);
    font-size:24px;
    font-weight:bold;
}

/* NEEDLE */
.needle{
    width:3px;
    height:80px;
    background:red;
    position:absolute;
    left:50%;
    bottom:0;
    transform-origin:bottom;
    transition:1s;
}

/* CHAT BUTTON */
#chatBtn{
    position:fixed;
    bottom:20px;
    right:20px;
    width:80px;
    height:80px;
    background:linear-gradient(45deg,#00f7ff,#00c3ff);
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:40px;
    cursor:pointer;
    box-shadow:0 5px 20px rgba(0,0,0,0.4);
    transition:0.3s;
}
#chatBtn:hover{
    transform:scale(1.25);
}

/* CHAT BOX */
#chatBox{
    position:fixed;
    bottom:90px;
    right:20px;
    width:300px;
    background:white;
    color:black;
    border-radius:15px;
    display:none;
    flex-direction:column;
    overflow:hidden;
    animation:fadeIn 0.4s ease;
}

#chatMessages{
    height:250px;
    overflow-y:auto;
    padding:10px;
    font-size:14px;
}

/* Chat bubbles */
.user{
    text-align:right;
    margin:5px;
}
.bot{
    text-align:left;
    margin:5px;
}

/* Input */
.chat-input{
    display:flex;
}
.chat-input input{
    flex:1;
    border:none;
    padding:10px;
}
.chat-input button{
    width:80px;
    border:none;
    background:#00c3ff;
}

/* Animation */
@keyframes fadeIn{
    from{opacity:0; transform:translateY(20px);}
    to{opacity:1; transform:translateY(0);}
}
</style>
</head>

<body>

<div class="container">

<div class="left">
<div class="logo-container">
    <img src="/static/logo.png" class="logo">
    <h2>SymtoScan AI</h2>
    <p class="tagline">AI-Powered Health Prediction & Insights</p>
</div>
<h2>🦠 Input</h2>

<label>Fever <input type="checkbox" id="fever"></label>
<label>Cough <input type="checkbox" id="cough"></label>
<label>Fatigue <input type="checkbox" id="fatigue"></label>
<label>Breathing <input type="checkbox" id="breathing"></label>
<label>Travel <input type="checkbox" id="travel"></label>

<input id="temp" placeholder="Temperature">
<input id="oxygen" placeholder="Oxygen">
<input id="age" placeholder="Age">

<button onclick="predict()">Analyze</button>
</div>

<div class="right">

<div class="card">
<h3>Risk Meter</h3>
<div class="gauge-container">
<canvas id="gaugeChart"></canvas>
<div id="riskValue">0%</div>
<div class="needle" id="needle"></div>
</div>
</div>

<div class="card">
<h3>Symptoms</h3>
<canvas id="barChart"></canvas>
</div>

<div class="card">
<h3>Trend</h3>
<canvas id="lineChart"></canvas>
</div>

</div>
</div>

<!-- CHAT -->
<div id="chatBtn" onclick="toggleChat()">💬</div>

<div id="chatBox">
<div id="chatMessages"></div>

<div class="chat-input">
<input id="userInput" placeholder="Ask health question..." onkeypress="if(event.key==='Enter')sendMessage()">
<button onclick="sendMessage()">Send</button>
</div>
</div>

<script>

let barChart, lineChart, gaugeChart;
let history=[];

// ================== PREDICT ==================
function predict(){

let data={
fever:fever.checked?1:0,
cough:cough.checked?1:0,
fatigue:fatigue.checked?1:0,
breathing:breathing.checked?1:0,
temp:temp.value||98,
oxygen:oxygen.value||98,
age:age.value||25,
travel:travel.checked?1:0
};

fetch("/predict",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify(data)
})
.then(res=>res.json())
.then(res=>{

let risk = Number(res.probability)*100;

// TEXT
riskValue.innerText = risk.toFixed(1)+"%";

// NEEDLE
let angle=(risk/100)*180-90;
needle.style.transform="rotate("+angle+"deg)";

// BAR
if(barChart) barChart.destroy();
barChart = new Chart(document.getElementById("barChart"),{
type:'bar',
data:{
labels:["Fever","Cough","Fatigue","Breathing"],
datasets:[{data:[data.fever,data.cough,data.fatigue,data.breathing]}]
}
});

// LINE
history.push(risk);
if(lineChart) lineChart.destroy();
lineChart = new Chart(document.getElementById("lineChart"),{
type:'line',
data:{
labels:history.map((_,i)=>i+1),
datasets:[{data:history}]
}
});

// GAUGE
if(gaugeChart) gaugeChart.destroy();
gaugeChart = new Chart(document.getElementById("gaugeChart"),{
type:'doughnut',
data:{
datasets:[{data:[risk,100-risk]}]
},
options:{
circumference:180,
rotation:270,
cutout:"70%"
}
});

});
}

// ================== CHATBOT ==================
function getReply(msg){
msg = msg.toLowerCase();

if(msg.includes("fever"))
return "Fever indicates infection. Monitor regularly.";

if(msg.includes("cough"))
return "Persistent cough should not be ignored.";

if(msg.includes("oxygen"))
return "Oxygen must stay above 95%.";

if(msg.includes("covid"))
return "COVID spreads via air droplets. Stay protected.";

if(msg.includes("hello") || msg.includes("hi"))
return "Hello 👋 I'm your AI health assistant.";

return "Ask about symptoms, precautions or COVID 😊";
}

function toggleChat(){
chatBox.style.display = chatBox.style.display==="none"?"flex":"none";
}

function sendMessage(){
let msg = userInput.value.trim();
if(!msg) return;

chatMessages.innerHTML += `<div class="user"><b>You:</b> ${msg}</div>`;

let reply = getReply(msg);

setTimeout(()=>{
chatMessages.innerHTML += `<div class="bot"><b>Doctor:</b> ${reply}</div>`;
chatMessages.scrollTop = chatMessages.scrollHeight;
},500);

userInput.value="";
}

</script>

</body>
</html>
"""

# ======================
# API
# ======================
@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    features = np.array([[
        data["fever"],
        data["cough"],
        data["fatigue"],
        data["breathing"],
        float(data["temp"]),
        float(data["oxygen"]),
        float(data["age"]),
        data["travel"]
    ]])

    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0][1]

    return jsonify({
        "prediction": int(prediction),
        "probability": float(probability)
    })

if __name__ == "__main__":
    app.run(debug=True)