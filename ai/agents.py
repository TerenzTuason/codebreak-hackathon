# agents.py
# CrewAI agents for healthcare customer support scenarios using Google Gemini API

import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Task
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# --- Gemini LLM for CrewAI (LangChain wrapper) ---
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GEMINI_API_KEY
)

# --- CrewAI Agents ---
ai_agent_0 = Agent(
    name="Tier0AI",
    role="Basic Info Retrieval",
    goal="Answer simple, factual healthcare questions using LLM.",
    backstory="An AI agent designed to quickly retrieve and provide basic healthcare information to patients and staff.",
    llm=llm
)
ai_agent_1 = Agent(
    name="Tier1AI",
    role="Routine Task Handler",
    goal="Handle routine healthcare support tasks using LLM.",
    backstory="An AI agent specialized in automating routine healthcare support tasks, such as appointment confirmations and reminders.",
    llm=llm
)
ai_agent_2 = Agent(
    name="Tier2AI",
    role="Complex Task Handler",
    goal="Handle complex but automatable healthcare tasks using LLM.",
    backstory="An advanced AI agent capable of managing complex healthcare workflows, including multi-step processes and data synthesis.",
    llm=llm
)
human_agent_3 = Agent(
    name="Tier3Human",
    role="Human Supervisor",
    goal="Review and approve AI suggestions for Tier 3 tasks.",
    backstory="A human supervisor who reviews, approves, or overrides AI-generated suggestions for sensitive or ambiguous healthcare support cases.",
    llm=llm
)
human_agent_4 = Agent(
    name="Tier4Human",
    role="Human Expert",
    goal="Handle escalated, critical healthcare cases.",
    backstory="A senior healthcare professional responsible for handling escalated or critical cases that require expert human judgment.",
    llm=llm
)

# --- CrewAI Tasks ---
def ai_task(agent, description, data):
    prompt = f"{description}\nDetails: {data}"
    return Task(agent=agent, description=description, input=data)

def human_task(agent, description, data):
    # Simulate human review/approval
    return Task(agent=agent, description=description, input=data, run=lambda d: f"[Simulated human review/approval for: {description} | Data: {data}]")

# --- CrewAI Crews for each Tier ---
def get_crew_for_tier(tier, data, scenario_desc):
    if tier == 0:
        crew = Crew(
            agents=[ai_agent_0],
            tasks=[ai_task(ai_agent_0, scenario_desc, data)]
        )
    elif tier == 1:
        crew = Crew(
            agents=[ai_agent_1],
            tasks=[ai_task(ai_agent_1, scenario_desc, data)]
        )
    elif tier == 2:
        crew = Crew(
            agents=[ai_agent_2],
            tasks=[ai_task(ai_agent_2, scenario_desc, data)]
        )
    elif tier == 3:
        crew = Crew(
            agents=[ai_agent_2, human_agent_3],
            tasks=[
                ai_task(ai_agent_2, scenario_desc, data),
                human_task(human_agent_3, "Review and approve AI output for Tier 3", data)
            ]
        )
    elif tier == 4:
        crew = Crew(
            agents=[ai_agent_2, human_agent_4],
            tasks=[
                ai_task(ai_agent_2, scenario_desc, data),
                human_task(human_agent_4, "Handle critical escalation for Tier 4", data)
            ]
        )
    else:
        return None
    return crew

# --- Scenario Descriptions ---
SCENARIO_DESCRIPTIONS = {
    "appointment": "Appointment scheduling or rescheduling for a patient.",
    "prescription": "Prescription refill assistance for a patient.",
    "lab_results": "Lab test results inquiry for a patient.",
    "insurance": "Insurance coverage inquiry for a patient.",
    "symptom_checker": "Symptom checker and triage for a patient.",
    "followup_reminder": "Follow-up appointment reminder for a patient.",
    "specialist_referral": "Specialist referral management for a patient.",
    "emergency": "Emergency contact routing for a patient.",
    "mental_health": "Mental health support for a patient.",
    "feedback": "Patient feedback collection after an appointment."
}

# --- Crew dispatcher for Flask integration ---
def crewai_agent(data):
    scenario = data.get('scenario')
    tier = int(data.get('tier', 0))
    scenario_desc = SCENARIO_DESCRIPTIONS.get(scenario, "General healthcare support task.")
    crew = get_crew_for_tier(tier, data, scenario_desc)
    if not crew:
        return {"error": f"Invalid tier: {tier}"}
    results = crew.kickoff()
    return {"crew_results": results}

# --- For backward compatibility, keep single-agent functions as wrappers ---
def appointment_agent(data):
    return crewai_agent({**data, "scenario": "appointment"})
def prescription_agent(data):
    return crewai_agent({**data, "scenario": "prescription"})
def lab_results_agent(data):
    return crewai_agent({**data, "scenario": "lab_results"})
def insurance_agent(data):
    return crewai_agent({**data, "scenario": "insurance"})
def symptom_checker_agent(data):
    return crewai_agent({**data, "scenario": "symptom_checker"})
def followup_reminder_agent(data):
    return crewai_agent({**data, "scenario": "followup_reminder"})
def specialist_referral_agent(data):
    return crewai_agent({**data, "scenario": "specialist_referral"})
def emergency_agent(data):
    return crewai_agent({**data, "scenario": "emergency"})
def mental_health_agent(data):
    return crewai_agent({**data, "scenario": "mental_health"})
def feedback_agent(data):
    return crewai_agent({**data, "scenario": "feedback"}) 