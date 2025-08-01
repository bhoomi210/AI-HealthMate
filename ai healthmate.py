import streamlit as st
import time
import datetime
import requests
from groq import Groq
from streamlit_option_menu import option_menu
from fpdf import FPDF

# === Configuration ===
st.set_page_config(page_title="AI HealthMate", layout="wide")

# === Insert Groq API key ===
groq_api_key = ""
client = Groq(api_key=groq_api_key)

# === Sidebar Navigation ===
with st.sidebar:
    st.image("https://i.imgur.com/4NZ6uLY.jpg", use_column_width=True)
    selected = option_menu(
        menu_title="Navigation",
        options=["Home", "Doctor Chat", "Symptom Checker", "Nutrition Planner", "Health Progress", "Mental Health Support", "Find Doctor", "About"],
        icons=["house", "chat-dots", "search", "utensils", "chart-line", "brain", "user-md", "info-circle"],
        menu_icon="list",
        default_index=0,
        styles={
            "container": {"padding": "5px"},
            "icon": {"font-size": "25px"},
            "nav-link": {"font-size": "16px", "--hover-color": "#ffc13b"},
            "nav-link-selected": {"background-color": "#ff6e40"},
        },
    )

# === CSS Styling ===
st.markdown('''
<style>
.tip-container {
    border: 2px solid #ff5733;
    padding: 15px;
    border-radius: 10px;
    color: white;
    background-color: #302b63;
    text-align: center;
    font-weight: bold;
}
</style>
''', unsafe_allow_html=True)

# === Helper Function ===
def get_ai_response(prompt, system_role):
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt},
            ],
            model="llama3-70b-8192",
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"AI Error: {str(e)}")
        return "Sorry, AI is currently unavailable."

# === Pages ===
def home():
    st.title("👨‍⚕️ AI HealthMate")
    st.write("Welcome to your AI-powered healthcare companion.")

    tips = [
        "🥗 Eat colorful fruits and vegetables every day.",
        "🏃‍♂️ Stay active — at least 30 minutes of exercise daily.",
        "💧 Drink 2-3 liters of water daily to stay hydrated.",
    ]
    for tip in tips:
        st.markdown(f'<div class="tip-container">{tip}</div>', unsafe_allow_html=True)
        time.sleep(2)

    st.markdown("### 🌟 Health Tip of the Day")
    tip = get_ai_response("Give one unique health tip for today.", "You are a health and wellness expert.")
    st.success(tip)

    st.markdown("### 🩺 Word of the Day")
    word = get_ai_response("Give a health-related word of the day with meaning and usage example.", "You're a health vocabulary expert.")
    st.info(word)

def doctor_chat():
    st.title("💬 Talk to the AI Doctor")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Describe your symptoms:")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        response = get_ai_response(prompt, "You are an AI doctor providing helpful advice.")
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

def symptom_checker():
    st.title("🔍 Symptom Checker")
    symptoms = st.text_area("Enter your symptoms:")
    if st.button("Check"):
        if symptoms:
            response = get_ai_response(f"Analyze the following symptoms: {symptoms}", "You are an AI symptom checker.")
            st.write(response)
        else:
            st.warning("Please enter your symptoms to analyze.")

def nutrition_planner():
    st.title("🥗 Nutrition Planner")
    st.write("Get personalized meal plans based on your dietary preferences and goals.")

    goal = st.selectbox("What is your primary goal?", ["Weight Loss", "Muscle Gain", "Balanced Diet", "Diabetes-Friendly", "Heart Health"])
    dietary_preference = st.selectbox("Dietary Preference:", ["Vegetarian", "Vegan", "Non-Vegetarian", "Pescatarian", "No Preference"])
    allergies = st.text_input("Any food allergies? (Optional)")
    additional_info = st.text_area("Any specific health conditions or requirements? (Optional)")

  
    if st.button("Generate Meal Plan"):
        prompt = f"Create a {goal.lower()} meal plan that is {dietary_preference.lower()}."
        if allergies:
            prompt += f" Avoid {allergies}."
        if additional_info:
            prompt += f" Consider the following condition: {additional_info}."

        response = get_ai_response(prompt, "You are a nutritionist generating healthy and personalized meal plans.")
        st.success("Here’s your personalized meal plan:")
        st.write(response)

def generate_pdf(content, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)
    pdf.output(filename)

    if st.button("Download PDF"):
        filename = "nutrition_plan.pdf"
        generate_pdf(st.session_state.nutrition_plan, filename)
        with open(filename, "rb") as f:
            st.download_button("Download Nutrition Plan", f, file_name=filename)    

def health_progress_tracker():
    st.title("📊 Health Progress Tracker")
    if "weight_history" not in st.session_state:
        st.session_state.weight_history = []

    new_weight = st.number_input("Enter your current weight (kg):", min_value=30.0, max_value=300.0, value=70.0)

    if st.button("Log Weight"):
        st.session_state.weight_history.append(new_weight)
        st.success(f"Weight logged: {new_weight} kg")

    if st.session_state.weight_history:
        st.line_chart(st.session_state.weight_history)
    else:
        st.write("No data available.")

def mental_health_support():
    st.title("🧠 Mental Health Support")
    mental_health_prompt = st.text_area("How are you feeling today?")
    if st.button("Get Advice"):
        if mental_health_prompt:
            response = get_ai_response(f"Provide mental health advice for the following: {mental_health_prompt}", "You are a mental health AI assistant.")
            st.write(response)
        else:
            st.warning("Please describe your feelings.")

def doctor_finder():
    st.title("👩‍⚕️ Find a Doctor Near You")
    location = st.text_input("Enter your city or zip code:")
    
    if st.button("Find Doctors"):
        if location:
            st.success(f"Showing doctors near {location}:")

            doctors = [
                {"name": "Dr. Neha Sharma", "specialty": "Cardiologist", "contact": "9876543210"},
                {"name": "Dr. Anil Verma", "specialty": "General Physician", "contact": "9123456780"},
                {"name": "Dr. Fatima Khan", "specialty": "Dermatologist", "contact": "9988776655"},
                {"name": "Dr. Premal Pancholi", "specialty" : "Multispecialist", "contact" : "9876543210"},
                {"name" : "Dr. Nikesh Shah", "specialty" : "Orthopaedic", "contact": "9823456702"},
            ]

            for doc in doctors:
                st.markdown(f"""
                **👨‍⚕️ {doc['name']}**  
                *Specialty:* {doc['specialty']}  
                *Contact:* 📞 {doc['contact']}  
                """)
        else:
            st.warning("Please enter your location.")


def about():
    st.title("📘 About Us")
    st.write("We are a team passionate about using AI to enhance healthcare.")

    team = [
        {
            "name": "Dr. Alice",
            "role": "AI Healthcare Specialist",
            "image": "https://i.imgur.com/0XhF2KT.png",
            "linkedin": "https://linkedin.com",
            "github": "https://github.com"
        },
        {
            "name": "John Doe",
            "role": "Frontend Developer",
            "image": "https://i.imgur.com/QoE7TnN.png",
            "linkedin": "https://linkedin.com",
            "github": "https://github.com"
        },
    ]

    cols = st.columns(len(team))
    for idx, member in enumerate(team):
        with cols[idx]:
            st.image(member["image"], width=150)
            st.subheader(member["name"])
            st.caption(member["role"])
            st.markdown(f"[LinkedIn]({member['linkedin']}) | [GitHub]({member['github']})")

# === Page Routing ===
if selected == "Home":
    home()
elif selected == "Doctor Chat":
    doctor_chat()
elif selected == "Symptom Checker":
    symptom_checker()
elif selected == "Nutrition Planner":
    nutrition_planner()
elif selected == "Health Progress":
    health_progress_tracker()
elif selected == "Mental Health Support":
    mental_health_support()
elif selected == "Find Doctor":
    doctor_finder()
elif selected == "About":
    about()
