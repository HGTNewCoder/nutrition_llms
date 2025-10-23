from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import os
import csv
from prompt import generate_food_exercise, generate_important, generate_routine

app = Flask(__name__)
# ---- ROUTES ----
@app.route('/image/<path:filename>')
def image(filename):
    return send_from_directory('image', filename)

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
def save_user_data(name, age, weight,height, disease_list):
    file_exists = os.path.isfile("user_data.csv")
    with open("user_data.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Name", "Age", "Weight", "Height","Disease"])
        writer.writerow([name, age, weight, height, ";".join(disease_list)])


@app.route("/base", methods=["GET", "POST"])
def health_form():
    diseases = load_diseases()
    
    if request.method == "POST":
        # collect form data
        form_data = {
            "name": request.form.get("name"),
            "age": request.form.get("age"),
            "weight": request.form.get("weight"),
            "height": request.form.get("height"),
            "sex": request.form.get("sex"),
            "race": request.form.get("race"),
            "disease": request.form.getlist("disease")
        }

        # Save user data
        save_user_data(
            form_data["name"],
            form_data["age"],
            form_data["weight"],
            form_data["height"],
            form_data["disease"]
        )

        # Render answer page immediately with form data
        return render_template("answer.html", form_data=form_data)

    return render_template("base.html", diseases=diseases)




@app.route("/")
def home():
    return render_template("base.html", page="home")


@app.route("/ask")
def ask():
    diseases = load_diseases()
    return render_template("ask.html", page="ask", diseases=diseases)


@app.route("/answer")
def answer():
    return render_template("answer.html", page="answer")


@app.route("/about")
def about():
    return render_template("about.html", page="about")

@app.route("/get_content/<category>", methods=["POST"])
def get_content(category):
    if category == "food":
        return jsonify({"content": generate_food_exercise()})
    elif category == "routine":
        return jsonify({"content": generate_routine()})
    elif category == "important":
        return jsonify({"content": generate_important()})
    else:
        return jsonify({"content": "No content available."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port = port, debug=True)
