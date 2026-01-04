from flask import Flask, request, render_template_string, send_from_directory
from datetime import datetime
import os
from math import radians, cos, sin, asin, sqrt

app = Flask(__name__)

# ---------------- CONFIG ----------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ITEM_KEYWORDS = [
    "wallet","phone","bag","earring","ring","watch",
    "keys","charger","helmet","id","card","bottle","book"
]

DATABASE = []

# ---------------- DISTANCE ----------------
def distance_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, map(float,[lat1,lon1,lat2,lon2]))
    dlat = lat2-lat1
    dlon = lon2-lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 6371 * (2*asin(sqrt(a)))

# ---------------- UI ----------------
HTML = """
<!doctype html>
<html>
<head>
<title>Smart Lost & Found</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap" rel="stylesheet">
<style>
body{
margin:0;font-family:'Poppins',sans-serif;
background:linear-gradient(135deg,#020617,#020617);
min-height:100vh;display:flex;justify-content:center;align-items:center;color:white
}
.container{
width:560px;padding:38px;border-radius:28px;
background:linear-gradient(135deg,#0f172a,#020617);
box-shadow:0 40px 90px rgba(0,0,0,.8)
}
h1{text-align:center;font-weight:800}
input,select,button{
width:100%;height:54px;padding:16px;
border-radius:16px;border:none;margin-top:14px;
font-size:16px;font-family:'Poppins',sans-serif;
box-sizing:border-box
}
input::placeholder{color:#9ca3af}
button{
font-weight:700;
background:linear-gradient(135deg,#38bdf8,#2563eb);
color:white;cursor:pointer
}
.card{
margin-top:30px;padding:24px;border-radius:22px;
background:white;color:#020617
}
.badge{
padding:6px 14px;border-radius:999px;
font-size:12px;font-weight:700;color:white
}
.lost{background:#f97316}
.found{background:#22c55e}
.preview{
margin:16px auto 0;display:block;
max-width:240px;width:100%;border-radius:14px
}
.map{margin-top:16px;border-radius:16px;overflow:hidden}
</style>
</head>

<body>
<div class="container">
<h1>🔍 Smart Lost & Found</h1>

<form method="POST" enctype="multipart/form-data">
<input name="description" placeholder="Lost black book near canteen" required>
<select name="type">
<option value="lost">Lost</option>
<option value="found">Found</option>
</select>
<input type="hidden" name="lat" id="lat">
<input type="hidden" name="lng" id="lng">
<input type="file" name="image" accept="image/*">
<button>Submit</button>
</form>

<script>
navigator.geolocation.getCurrentPosition(p=>{
lat.value=p.coords.latitude;
lng.value=p.coords.longitude;
});
</script>

{% if result %}
<div class="card">
<span class="badge {{ result.type }}">{{ result.type|upper }}</span>
<h3>{{ result.text }}</h3>
<p>📍 {{ result.location }}</p>
<p>🧠 AI Confidence: {{ result.confidence }}%</p>
<p><b>{{ result.status }}</b></p>

{% if result.image %}
<img src="{{ result.image }}" class="preview">
{% endif %}

<div class="map">
<iframe src="https://www.google.com/maps?q={{ result.location }}&output=embed"
width="100%" height="200" style="border:0"></iframe>
</div>
</div>
{% endif %}
</div>
</body>
</html>
"""

# ---------------- ROUTES ----------------
@app.route("/uploads/<filename>")
def uploaded(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/", methods=["GET","POST"])
def index():
    result = None

    if request.method == "POST":
        text = request.form["description"].lower()
        t = request.form["type"]   # lost / found
        lat = request.form.get("lat")
        lng = request.form.get("lng")
        location = f"{lat},{lng}" if lat and lng else "Unknown"

        image = request.files.get("image")
        img_url = None
        if image and image.filename:
            image.save(os.path.join(UPLOAD_FOLDER, image.filename))
            img_url = f"/uploads/{image.filename}"

        item = next((w for w in text.split() if w in ITEM_KEYWORDS), None)

        # ---------- CONFIDENCE ----------
        confidence = 40
        if item: confidence += 20
        if img_url: confidence += 20
        if lat: confidence += 20
        confidence = min(confidence, 95)

        # ---------- MATCH ----------
        for d in DATABASE:
            if item and item in d["text"] and d["type"] != t:
                if lat and d.get("lat"):
                    dist = distance_km(lat,lng,d["lat"],d["lng"])
                    if dist <= 0.5:
                        d["status"] = "🔥 Matched"
                        result = {
                            "type": t,                 # ✅ CURRENT TYPE
                            "text": text,
                            "location": location,
                            "lat": lat,
                            "lng": lng,
                            "image": img_url,
                            "confidence": confidence,
                            "status": f"🔥 Match found ({round(dist*1000)}m away)"
                        }
                        return render_template_string(HTML,result=result)

        # ---------- SAVE ----------
        result = {
            "type": t,
            "text": text,
            "location": location,
            "lat": lat,
            "lng": lng,
            "image": img_url,
            "confidence": confidence,
            "status": "Saved successfully ✅"
        }
        DATABASE.append(result)

    return render_template_string(HTML,result=result)

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    total=len(DATABASE)
    lost=len([d for d in DATABASE if d["type"]=="lost"])
    found=len([d for d in DATABASE if d["type"]=="found"])
    matched=len([d for d in DATABASE if "matched" in d["status"].lower()])

    return f"""
    <h1>Admin Dashboard</h1>
    <p>Total: {total}</p>
    <p>Lost: {lost}</p>
    <p>Found: {found}</p>
    <p>Matched: {matched}</p>
    """

if __name__=="__main__":
    app.run(debug=True)
