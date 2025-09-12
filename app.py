from flask import Flask, render_template, request, redirect, url_for
import csv
import os
from prompt import generate_routine  # Your existing LLM pipeline
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# ---- Load disease options ----
def load_diseases():
    diseases = []
    if os.path.exists("disease.csv"):
        with open("disease.csv", newline="") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                diseases.append(row[0].strip())
    return diseases

# ---- Save user data ----
def save_user_data(name, age, weight, disease_list):
    file_exists = os.path.isfile("user_data.csv")
    with open("user_data.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Name", "Age", "Weight", "Disease"])
        writer.writerow([name, age, weight, ";".join(disease_list)])

# ---- ROUTES ----
@app.route("/", methods=["GET", "POST"])
def health_form():
    diseases = load_diseases()
    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        weight = float(request.form.get("weight"))
        selected_diseases = request.form.getlist("disease")

        # Save data
        save_user_data(name, age, weight, selected_diseases)

        # Redirect to routine page with query params
        return redirect(url_for("daily_routine", weight=weight, disease=",".join(selected_diseases)))

    return render_template("index.html", diseases=diseases)

@app.route("/routine")
def daily_routine():
    disease_list = request.args.get("disease", "").split(",")
    weight = float(request.args.get("weight", 0))

    if not disease_list:
        return "No disease data found. Please submit the health form first."

    routine_text = generate_routine(disease_list, weight)
    # Parse LLM output into sections for template
    routine_sections = []
    sections = routine_text.split("**")
    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue
        try:
            disease_name, rest = sec.split("\n", 1)
        except ValueError:
            disease_name, rest = sec, ""
        exercises = []
        foods = []
        lines = rest.split("\n")
        current_section = None
        for line in lines:
            line = line.strip()
            if line.startswith("Exercise:"):
                current_section = "exercise"
                continue
            elif line.startswith("Food:"):
                current_section = "food"
                continue
            elif line.startswith("-"):
                item = line.replace("-", "").strip()
                if current_section == "exercise":
                    exercises.append(item)
                elif current_section == "food":
                    foods.append(item)
        routine_sections.append({
            "disease": disease_name,
            "exercises": exercises,
            "foods": foods
        })
    # Pass parsed routine_sections and raw routine_text to template
    return render_template("routine.html", routine_sections=routine_sections, routine_text=routine_text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port = port, debug=True)
