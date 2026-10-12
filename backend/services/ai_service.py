import os
from collections.abc import Sequence
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph
from PIL import Image


def image_reasoning_tool(image_path: str) -> str:
    try:
        if not os.path.exists(image_path):
            return f"Error: Image not found at {image_path}"

        import google.generativeai as genai

        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        model = genai.GenerativeModel("gemini-2.5-flash")
        image = Image.open(image_path)

        prompt = (
            "You are a maintenance inspector. Analyze this image and provide a brief 2-3 sentence summary of any maintenance issues. "
            "Focus on: fans, lights, furniture, or electronics. "
            "If damaged: state the item and specific problem (e.g., 'Ceiling fan blade is severely bent and broken'). "
            "If no issues: respond with exactly 'No maintenance issues detected'. "
            "Keep your response concise and under 100 words."
        )

        response = model.generate_content([prompt, image])

        return response.text.strip() if response.text else "No visible issues detected."

    except Exception as exc:
        return f"Error occurred: {str(exc)}"


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    image_path: str
    issue_detected: str
    issue_type: str
    priority: str
    ticket_created: bool


def analyze_image_node(state: AgentState) -> AgentState:
    image_path = state["image_path"]
    analysis_result = image_reasoning_tool(image_path)

    state["issue_detected"] = analysis_result
    state["messages"] = list(state.get("messages", [])) + [
        AIMessage(content=f"Image Analysis Complete: {analysis_result}")
    ]

    return state


def classify_issue_node(state: AgentState) -> AgentState:
    issue_text = state["issue_detected"].lower()

    if "fan" in issue_text:
        issue_type = "Fan"
    elif "light" in issue_text or "bulb" in issue_text or "lamp" in issue_text:
        issue_type = "Light"
    elif "furniture" in issue_text or "chair" in issue_text or "table" in issue_text or "desk" in issue_text:
        issue_type = "Furniture"
    elif "electronics" in issue_text or "computer" in issue_text or "screen" in issue_text:
        issue_type = "Electronics"
    elif "electrical" in issue_text or "wire" in issue_text or "socket" in issue_text:
        issue_type = "Electrical"
    else:
        issue_type = "Other"

    critical_keywords = ["severely", "broken", "damaged", "fire", "sparking", "dangerous", "hazard", "catastrophic", "major", "shattered"]
    high_keywords = ["not working", "malfunctioning", "cracked", "bent", "loose", "leaking"]
    low_keywords = ["no maintenance issues", "no issues", "no visible issues", "minor", "slight"]

    if any(keyword in issue_text for keyword in low_keywords):
        priority = "low"
    elif any(keyword in issue_text for keyword in critical_keywords):
        priority = "high"
    elif any(keyword in issue_text for keyword in high_keywords):
        priority = "medium"
    else:
        priority = "low"

    state["issue_type"] = issue_type
    state["priority"] = priority
    state["messages"] = list(state.get("messages", [])) + [
        AIMessage(content=f"Issue classified as: {issue_type} (Priority: {priority})")
    ]

    return state


def create_ticket_node(state: AgentState) -> AgentState:
    state["ticket_created"] = True
    state["messages"] = list(state.get("messages", [])) + [
        AIMessage(content="Maintenance ticket ready to be created")
    ]

    return state


def build_workflow():
    workflow = StateGraph(AgentState)

    workflow.add_node("analyze_image", analyze_image_node)
    workflow.add_node("classify_issue", classify_issue_node)
    workflow.add_node("create_ticket", create_ticket_node)

    workflow.set_entry_point("analyze_image")
    workflow.add_edge("analyze_image", "classify_issue")
    workflow.add_edge("classify_issue", "create_ticket")
    workflow.add_edge("create_ticket", END)

    return workflow.compile()


agent_workflow = build_workflow()


def analyze_image_for_ticket(image_path: str, student_name: str, location: str) -> dict:
    initial_state: AgentState = {
        "messages": [HumanMessage(content=f"Analyzing image from {student_name} at {location}")],
        "image_path": image_path,
        "issue_detected": "",
        "issue_type": "",
        "priority": "",
        "ticket_created": False,
    }

    final_state = agent_workflow.invoke(initial_state)

    return {
        "issue_type": final_state["issue_type"],
        "description": final_state["issue_detected"],
        "priority": final_state["priority"],
    }
