from flask_cors import CORS
from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load cleaned dataset
try:
    df = pd.read_csv("database.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=["Disease", "Symptoms", "Recommended Medicine", "Precaution"])

# Load Medicine Dataset
try:
    med_df = pd.read_csv("medicine_database.csv")
except FileNotFoundError:
    med_df = pd.DataFrame(columns=["Medicine", "Usage", "Precaution", "Side Effects"])

# General responses for non-medical questions
general_responses = {
    "who trained you": "I was built by Pratyum Jangid for the SynthQuest!",
    "what do you do": "I help users with medical guidance and medicine information!",
    "tell me a joke": "Why did the doctor carry a red pen? In case they needed to draw blood!",
    "how are you": "I'm just a chatbot, but I'm here to help you!",
    "who created you": "I was created by Pratyum Jangid!",
    "what is your name": "I'm your AI healthcare assistant!",
    "what is your purpose": "I assist users with medical advice, symptom checking, and medicine information.",
    "how can you help me": "I can provide information on symptoms, diseases, and medicine recommendations.",
    "i feel dizzy": "Dizziness can be caused by dehydration, low blood pressure, or an ear infection. Try drinking water and resting. If it persists, consult a doctor.",
    "i have a headache": "A headache can result from stress, dehydration, or migraines. Drink water and rest. If severe, consider taking a mild pain reliever.",
    "i have stomach pain": "Stomach pain can be caused by indigestion, gas, or food poisoning. Try drinking warm water and avoiding heavy meals.",
    "my joints hurt": "Joint pain may be due to arthritis, strain, or lack of movement. Applying heat and mild stretching may help.",
    "i have a fever": "A fever is usually a sign of infection. Stay hydrated and rest. If it exceeds 102°F, consult a doctor.",
    "my throat hurts": "A sore throat can be caused by an infection or allergies. Try warm tea with honey and rest.",
    "i feel nauseous": "Nausea can be caused by food poisoning, motion sickness, or stress. Sip ginger tea and rest.",
    "i feel weak": "Weakness can result from low blood sugar, dehydration, or illness. Eat a balanced meal and rest.",
    "i have a cold": "A cold is caused by a viral infection. Stay warm, hydrated, and rest.",
}

# Function to process user input
# Function to process user input
def get_response(user_input):
    user_input = user_input.lower().strip()

    # Check for general medical questions using keyword matching
    for key in general_responses:
        if key in user_input or any(word in user_input for word in key.split()):  # Flexible matching
            return {"response": general_responses[key]}

    # Check for direct disease name queries
    for _, row in df.iterrows():
        disease_name = str(row["Disease"]).lower().strip()
        if disease_name in user_input:
            return {
                "Possible Condition": row["Disease"],
                "Recommended Medicine": row["Recommended Medicine"],
                "Precaution": row["Precaution"],
                "Possible Symptoms": row["Symptoms"]
            }

    # Check for symptoms in the database
    best_match = None
    max_matched = 0

    for _, row in df.iterrows():
        symptoms_text = str(row["Symptoms"]).lower().strip()
        symptoms_list = [s.strip() for s in symptoms_text.split(",") if s.strip()]
        matched_symptoms = [symptom for symptom in symptoms_list if symptom in user_input]

        if len(matched_symptoms) > max_matched:
            max_matched = len(matched_symptoms)
            best_match = row

    if best_match:
        return {
            "Possible Condition": best_match["Disease"],
            "Matched Symptoms": ", ".join(best_match["Symptoms"].split(",")[:3]),
            "Recommended Medicine": best_match["Recommended Medicine"],
            "Precaution": best_match["Precaution"]
        }

    return {"response": "I'm sorry, I couldn't recognize the symptoms. Please consult a doctor."}

# Medicine Information API
@app.route("/medicine", methods=["POST"])
def medicine_info():
    try:
        data = request.get_json()
        if not data or "medicine" not in data:
            return jsonify({"error": "Invalid request. Send {'medicine': 'name'}"}), 400
        
        medicine_name = data["medicine"].strip().lower()

        # Search in the medicine dataset
        for _, row in med_df.iterrows():
            if str(row["Medicine"]).strip().lower() == medicine_name:
                return jsonify({
                    "Medicine": row["Medicine"],
                    "Usage": row.get("Usage", "Not available"),
                    "Precautions": row.get("Precaution", "Not available"),
                    "Side Effects": row.get("Side Effects", "Not available"),
                })

        return jsonify({"response": "Sorry, no information found for this medicine."})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Homepage route
@app.route("/", methods=["GET"])
def home():
    return "Chatbot API is running!"

# Chatbot API route
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Invalid request. Please send {'message': 'your query'}"}), 400
        
        user_message = data["message"]
        response = get_response(user_message)
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)
