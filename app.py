# mini-gen-search/frontend-service-search/app.py (Modified to single form for RAG)
from flask import Flask, request, render_template_string, redirect, url_for
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Use TEXTGEN_HOST env var if provided (set by docker-compose/k8s), otherwise default to localhost.
TEXTGEN_HOST = os.environ.get("TEXTGEN_HOST", "http://localhost:5001")

HTML_PAGE = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>mini-gen — RAG Search Frontend</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 40px; max-width: 800px; }
      textarea { width: 100%; height: 120px; }
      .result { margin-top: 20px; padding: 12px; border: 1px solid #ddd; background: #f9f9f9; }
      button { padding: 8px 16px; font-size: 16px; }
      label { font-weight: bold; }
    </style>
  </head>
  <body>
    <h1>mini-gen — Electoral List RAG Search</h1>
    <form method="post" action="/">
      <label for="prompt">Search the Electoral List (PDF):</label><br/>
      <textarea id="prompt" name="prompt" placeholder="Search for a name, address, or specific detail in the electoral roll...">{{ prompt if prompt is not None else '' }}</textarea><br/><br/>
      <button type="submit">Search Document</button>
    </form>

    {% if result %}
      <div class="result">
        <h3>RAG Search Result:</h3>
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
            return render_template_string(HTML_PAGE, prompt=prompt, result=None, error="Prompt cannot be empty.")
        
        # --- CRITICAL MODIFICATION: Target the new RAG endpoint /ask ---
        backend_url = f"{TEXTGEN_HOST}/ask" 
        
        try:
            # Send the user's prompt to the TextGen RAG backend service
            resp = requests.post(
                backend_url, 
                json={"prompt": prompt}, 
                timeout=30
            )
        except requests.RequestException as e:
            return render_template_string(HTML_PAGE, prompt=prompt, result=None, error=str(e))

        if resp.status_code != 200:
            return render_template_string(HTML_PAGE, prompt=prompt, result=None,
                                          error=f"TextGen RAG service error: {resp.status_code} - {resp.text}")
        
        data = resp.json()
        result = data.get("generated", "An unexpected error occurred during search.")
        return render_template_string(HTML_PAGE, prompt=prompt, result=result, error=None)
    else:
        return render_template_string(HTML_PAGE, prompt="", result=None, error=None)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)