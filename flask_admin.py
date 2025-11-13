from __future__ import annotations

import os

from flask import Flask, abort, redirect, render_template_string, request, url_for

from bot.core.questions_store import add_question, get_categories, load_questions

ADMIN_PANEL_TOKEN = os.getenv("ADMIN_PANEL_TOKEN", "change-me")

app = Flask(__name__)

BASE_TEMPLATE = """
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>CultureG Admin</title>
</head>
<body>
  <h1>CultureG - Panel admin (Flask)</h1>
  <p>
    <a href="{{ url_for('index', token=request.args.get('token')) }}">Liste</a> |
    <a href="{{ url_for('add', token=request.args.get('token')) }}">Ajouter une question</a>
  </p>
  <hr>
  {% block content %}{% endblock %}
</body>
</html>
"""


@app.before_request
def check_auth():
    token = request.args.get("token") or request.headers.get("X-Admin-Token")
    if token != ADMIN_PANEL_TOKEN:
        abort(403)


@app.get("/")
def index():
    cats = get_categories()
    category = request.args.get("category") or ""
    if category:
        questions = load_questions(category)
    else:
        questions = load_questions()

    return render_template_string(
        BASE_TEMPLATE
        + """
        {% block content %}
        <h2>Questions ({{ questions|length }})</h2>
        <form method="get">
          <input type="hidden" name="token" value="{{ request.args.get('token') }}">
          <label>Catégorie :
            <select name="category">
              <option value="">(toutes)</option>
              {% for c in cats %}
                <option value="{{ c }}" {% if c == category %}selected{% endif %}>{{ c }}</option>
              {% endfor %}
            </select>
          </label>
          <button type="submit">Filtrer</button>
        </form>
        <ul>
          {% for q in questions %}
            <li>
              <strong>[{{ q.get('category', 'inconnue') }}]</strong>
              {{ q["q"] }}
            </li>
          {% endfor %}
        </ul>
        {% endblock %}
        """,
        questions=questions,
        cats=cats,
        category=category,
    )


@app.get("/add")
def add():
    cats = get_categories()
    return render_template_string(
        BASE_TEMPLATE
        + """
        {% block content %}
        <h2>Ajouter une question</h2>
        <form method="post" action="{{ url_for('add', token=request.args.get('token')) }}">
          <p>Question :<br>
            <textarea name="q" rows="3" cols="80"></textarea>
          </p>
          <p>Réponse A : <input name="a" size="60"></p>
          <p>Réponse B : <input name="b" size="60"></p>
          <p>Réponse C : <input name="c" size="60"></p>
          <p>Réponse D : <input name="d" size="60"></p>
          <p>Bonne réponse :
            <select name="good">
              <option value="0">A</option>
              <option value="1">B</option>
              <option value="2">C</option>
              <option value="3">D</option>
            </select>
          </p>
          <p>Catégorie :
            <select name="category">
              {% for c in cats %}
                <option value="{{ c }}">{{ c }}</option>
              {% endfor %}
            </select>
            ou nouvelle : <input name="new_category" size="20">
          </p>
          <p>Difficulté :
            <select name="difficulty">
              <option value="facile">facile</option>
              <option value="moyen">moyen</option>
              <option value="difficile">difficile</option>
            </select>
          </p>
          <button type="submit">Ajouter</button>
        </form>
        {% endblock %}
        """,
        cats=cats or [],
    )


@app.post("/add")
def add_post():
    q = (request.form.get("q") or "").strip()
    a = (request.form.get("a") or "").strip()
    b = (request.form.get("b") or "").strip()
    c = (request.form.get("c") or "").strip()
    d = (request.form.get("d") or "").strip()
    good_raw = request.form.get("good") or "0"
    category = (request.form.get("new_category") or "").strip() or (
        request.form.get("category") or ""
    ).strip()
    difficulty = (request.form.get("difficulty") or "facile").strip() or "facile"

    if not q or not all([a, b, c, d]):
        return "Tous les champs doivent être remplis.", 400
    if not category:
        return "Catégorie manquante.", 400

    try:
        good_index = int(good_raw)
    except ValueError:
        good_index = 0

    choices = [a, b, c, d]

    add_question(category, q, choices, good_index, difficulty=difficulty)

    return redirect(url_for("index", token=request.args.get("token")))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
