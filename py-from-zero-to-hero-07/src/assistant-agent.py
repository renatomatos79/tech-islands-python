import autogen
from autogen import AssistantAgent

# -----------------------------------------------------
# OLLAMA CONFIGURATION
# -----------------------------------------------------
# Since we're running Ollama locally, we treat the model as "free".
# AutoGen tries to estimate cost, so we silence related warnings by setting price to zero.
# We also set base_url to the local OpenAI-compatible API exposed by Ollama.
# -----------------------------------------------------
config_list = [
    {
        "model": "llama3.2",
        "base_url": "http://localhost:11435/v1",
        "api_key": "ollama",   # not really used, but must not be empty
        "price": [0, 0],       # prompt_price_per_1k, completion_price_per_1k
    },
]

# -----------------------------------------------------
# STUDENT AGENT
# -----------------------------------------------------
# This agent behaves like a beginner asking questions and learning.
#
# Key configuration notes:
#
# 1) temperature=0.9
#    - We give the student a slightly higher temperature than the teacher.
#    - Higher temperature encourages curiosity, follow-up questions, and
#      more expressive answers — which fits the persona of a learner.
#    - Values near 1.0 make the model less deterministic and more exploratory,
#      which results in a more natural "student-like" dialogue.
#
# 2) max_consecutive_auto_reply=2
#    - Just like the teacher, we enforce a limit to avoid infinite loops.
#    - Without this, the teacher and student might keep talking forever.
#    - Setting it to 2 allows the student to ask clarifying questions,
#      but ensures the script eventually returns control to the program.
#
# -----------------------------------------------------
student = AssistantAgent(
    name="studentAgent",
    system_message=(
        "You are a curious student. "
        "Ask questions when you don't understand something, "
        "and try to summarize what you learned."
    ),
    max_consecutive_auto_reply=2,
    llm_config={
        "config_list": config_list,
        "temperature": 0.9,
    },
)


# -----------------------------------------------------
# TEACHER AGENT
# -----------------------------------------------------
# This agent explains concepts in simple terms.
#
# We configure two important behavior parameters here:
#
# 1) temperature=0.7
#    - Temperature controls creativity vs. determinism in the model.
#    - Lower values (~0.2–0.5) = more factual + deterministic (good for coding/math).
#    - Higher values (~0.9–1.2) = more imaginative + chatty (good for brainstorming).
#    - 0.7 is a balanced value for “teaching” because we want clarity + some adaptability.
#
# 2) max_consecutive_auto_reply=2
#    - Since two agents (teacher ↔ student) can talk to each other,
#      we set a limit to avoid infinite ping-pong loops.
#    - 2 means the teacher can auto-reply twice before yielding control.
#      This keeps the dialogue guided but safe.
#
# -----------------------------------------------------
teacher = AssistantAgent(
    name="teacherAgent",
    system_message=(
        "You are a patient teacher. "
        "Explain concepts clearly, using examples when helpful. "
        "Ask the student if they understood."
    ),
    max_consecutive_auto_reply=2,
    llm_config={
        "config_list": config_list,
        "temperature": 0.7,
    },
)


# -----------------------------------------------------
# CONVERSATION STARTER
# -----------------------------------------------------
# The teacher initiates by asking what the student wants to learn.
# -----------------------------------------------------
response = teacher.initiate_chat(
    recipient=student,
    message="Hello! What would you like to learn today?"
)

print("\n----- Conversation Output -----\n")
print(response)
