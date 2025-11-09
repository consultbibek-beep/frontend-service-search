# mini-gen/frontend-service/app.py
from flask import Flask, request, render_template_string, redirect, url_for
import os
import requests
from dotenv import load_dotenv

load_dotenv()  # load .env when running locally (docker-compose uses env_file for textgen)

app = Flask(__name__)

# Use TEXTGEN_HOST env var if provided (set by docker-compose), otherwise default to localhost for local dev.
TEXTGEN_HOST = os.environ.get("TEXTGEN_HOST", "http://localhost:5001")

HTML_PAGE = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>mini-gen — Frontend</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 40px; max-width: 800px; }
      textarea { width: 100%; height: 120px; }
      .result { margin-top: 20px; padding: 12px; border: 1px solid #ddd; background: #f9f9f9; }
      button { padding: 8px 16px; font-size: 16px; }
      label { font-weight: bold; }
    </style>
  </head>
  <body>
    <h1>mini-gen — Frontend</h1>
    <form method="post" action="/">
      <label for="prompt">Provide an input here!:</label><br/>
      <textarea id="prompt" name="prompt" placeholder="Write your prompt here...">{{ prompt }}</textarea><br/><br/>
      <button type="submit">Generate</button>
    </form>

    {% if result %}
      <div class="result">
        <h3>Generated Cooked up by AI—spicy, weird, and slightly underdone!(20-word limit):</h3>
        <p>{{ result }}</p>
      </div>
    {% endif %}

    {% if error %}
      <div class="result" style="border-color: #f99; background: #fff0f0;">
        <h3>Error</h3>
        <pre>{{ error }}</pre>
      </div>
    {% endif %}
  </body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        if not prompt:
            return render_template_string(HTML_PAGE, prompt=prompt, result=None, error="Prompt cannot be empty. Say something!")
        try:
            resp = requests.post(
                f"{TEXTGEN_HOST}/generate",
                json={"prompt": prompt},
                timeout=30
            )
        except requests.RequestException as e:
            return render_template_string(HTML_PAGE, prompt=prompt, result=None, error=str(e))
        if resp.status_code != 200:
            return render_template_string(HTML_PAGE, prompt=prompt, result=None,
                                          error=f"TextGen service error: {resp.status_code} - {resp.text}")
        data = resp.json()
        result = data.get("generated", "")
        return render_template_string(HTML_PAGE, prompt=prompt, result=result, error=None)
    else:
        return render_template_string(HTML_PAGE, prompt="", result=None, error=None)

if __name__ == "__main__":
    # Useful for local development: runs on 0.0.0.0:5000 so docker container maps correctly
    app.run(host="0.0.0.0", port=5000)
