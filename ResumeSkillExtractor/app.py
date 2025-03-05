from flask import Flask, render_template, request
from pyresparser import ResumeParser
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Skill Points System
skill_points = {
    "Python": 10,
    "Machine Learning": 15,
    "Data Science": 20,
    "Java": 10,
    "Communication": 5,
    "SQL": 8,
    "C++": 12,
    "Deep Learning": 18,
    "HTML": 5,
    "CSS": 5,
    "JavaScript": 10
}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Store Candidate Details
candidates = []

# Function to Calculate Rank Score
def calculate_rank(skills):
    total_score = 0
    for skill in skills:
        if skill in skill_points:
            total_score += skill_points[skill]
    return total_score

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "resume" not in request.files:
        return "No file uploaded", 400

    file = request.files["resume"]
    if file.filename == "":
        return "No selected file", 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    try:
        data = ResumeParser(file_path).get_extracted_data()
        skills = data.get("skills", [])
        rank = calculate_rank(skills)

        candidate = {
            "name": data.get("name", "Unknown"),
            "skills": skills,
            "rank": rank
        }

        candidates.append(candidate)
        # Sort candidates by rank (Descending Order)
        candidates.sort(key=lambda x: x["rank"], reverse=True)

        return render_template("index.html", skills=skills, rank=rank)

    except Exception as e:
        return f"Error processing file: {str(e)}", 500

@app.route("/ranking")
def ranking():
    return render_template("ranking.html", candidates=candidates)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/inputskill", methods=["GET", "POST"])
def input_skill():
    if request.method == "POST":
        selected_skills = [request.form.get("skill1"), request.form.get("skill2"), request.form.get("skill3")]
        selected_skills = [skill.lower() for skill in selected_skills if skill]  # Remove empty inputs

        filtered_candidates = []
        for candidate in candidates:
            candidate_skills = [s.lower() for s in candidate["skills"]]
            if all(skill in candidate_skills for skill in selected_skills):
                filtered_candidates.append(candidate)

        filtered_candidates.sort(key=lambda x: x["rank"], reverse=True)

        return render_template("ranking.html", candidates=filtered_candidates, selected_skills=selected_skills)

    return render_template("inputskill.html")

if __name__ == "__main__":
    app.run(debug=True)
