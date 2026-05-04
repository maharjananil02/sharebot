from __future__ import annotations

import os

from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return (
        "NEPSE Trading Bot — minimal status endpoint.\n"
        "This file exists so Vercel detects a Python entrypoint."
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
