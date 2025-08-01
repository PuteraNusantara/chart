from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
import datetime
import json
import os

app = Flask(__name__)
CORS(app)

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

@app.route("/api/saham/<kode>", methods=["GET"])
def cek_saham(kode):
    try:
        kode = kode.upper()
        ticker = yf.Ticker(f"{kode}.JK")
        hist = ticker.history(period="1d")

        if hist.empty:
            return jsonify({"error": f"Data saham {kode} tidak ditemukan."}), 404

        harga = hist['Close'][-1]
        open_ = hist['Open'][-1]
        volume = hist['Volume'][-1]
        close_sebelumnya = hist['Close'][-2] if len(hist) > 1 else None

        hasil = {
            "kode": f"{kode}.JK",
            "harga": float(harga),
            "volume": int(volume),
            "open": float(open_),
            "close": float(close_sebelumnya) if close_sebelumnya else None,
            "waktu": datetime.datetime.now().isoformat()
        }

        simpan_riwayat(hasil)
        return jsonify(hasil)

    except Exception as e:
        return jsonify({"error": f"Gagal ambil data saham: {str(e)}"}), 500

@app.route("/api/history", methods=["GET"])
def get_history():
    return jsonify(riwayat[::-1])  # urutan terbaru dulu
@app.route("/")
def index():
    return "API Saham Jalan!"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

