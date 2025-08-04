from flask import Flask, jsonify, render_template
from flask_cors import CORS
import requests
import datetime
import json
import os

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("TWELVE_API_KEY", "57ffc9d4ef854dc282b3ed44a8d48144")  # Ganti di Railway nanti
HISTORY_FILE = "history.json"

# Muat riwayat lama jika ada
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        try:
            riwayat = json.load(f)
        except json.JSONDecodeError:
            riwayat = []
else:
    riwayat = []

def simpan_riwayat(entry):
    riwayat.append(entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(riwayat, f, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/saham/<kode>")
def cek_saham(kode):
    try:
        kode = kode.upper()
        url = f"https://api.twelvedata.com/time_series?symbol={kode}.JK&interval=1day&apikey={API_KEY}&outputsize=2"
        res = requests.get(url)
        data = res.json()

        if "values" not in data:
            return jsonify({"error": data.get("message", "Data tidak ditemukan")}), 404

        values = data["values"]
        harga = float(values[0]["close"])
        open_ = float(values[0]["open"])
        volume = int(values[0]["volume"])
        close_sebelumnya = float(values[1]["close"]) if len(values) > 1 else None

        hasil = {
            "kode": f"{kode}.JK",
            "harga": harga,
            "volume": volume,
            "open": open_,
            "close": close_sebelumnya,
            "waktu": datetime.datetime.now().isoformat()
        }

        simpan_riwayat(hasil)
        return jsonify(hasil)

    except Exception as e:
        return jsonify({"error": f"Gagal ambil data: {str(e)}"}), 500

@app.route("/api/history")
def get_history():
    return jsonify(riwayat[::-1])  # urutan terbaru dulu

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
