## Overview

Brief introduction about this small app (`assistant-agent.py`):
- Multi-agent role behavior
- Personas via system messages
- Conversation flow management
- Ollama as backend for AutoGen
- Teacher/student pedagogy
- Temperature control differences

## Requirements

This project requires Python 3.11:
```bash
brew install python@3.11
python3.11 --version
```

## Setup

Create a virtual environment named `venv`:
```bash
cd py-from-zero-to-hero-07
python3.11 -m venv venv
```

Activate it:
```bash
source venv/bin/activate
```

Confirm the environment is active (you should see the `(venv)` prefix):
```text
(venv) renatomatos@PT-D144 py-from-zero-to-hero-07
```

Install dependencies:
```bash
pip install -r ./requirements.txt
```

## Ollama

Run Docker Ollama (port 11435):
```bash
docker run -d --name ollama \
  -p 11435:11434 \
  --network=backend-bridge-network \
  -v ollama:/root/.ollama \
  ollama/ollama
```

Pull the `llama3.2` model:
```bash
docker exec -it ollama bash
ollama pull llama3.2
```

Confirm the model was pulled:
```bash
docker exec -it ollama bash
ollama list
```

You should see something like:
```text
NAME               ID              SIZE      MODIFIED
llama3.2:latest    a80c4f17acd5    2.0 GB    6 minutes ago
```

## Run

```bash
python3.11 src/assistant-agent.py
```

You should see a short chat between the student and teacher agents.

## Sample output

```text
(venv) renatomatos@PT-D144L6PXF0 src % python3.11 assistant-agent.py
teacherAgent (to studentAgent):

Hello! What would you like to learn today?

--------------------------------------------------------------------------------
studentAgent (to teacherAgent):

That's great that I get to start fresh every day!

Hmm... I'm not really sure where to begin. Is there a new topic or subject we could explore together? Or maybe I could try to learn something through conversation?

Can you give me some suggestions? What are some interesting topics or questions that I could ask you about?

Oh, and also... is this a kind of "teaching" session where I get to be the student, or can we have a more free-form conversation?

--------------------------------------------------------------------------------
teacherAgent (to studentAgent):

I'm glad you're excited to start fresh!

We can definitely do a combination of both - structured learning and conversational exploration. I'd like to propose some topics that might interest you, but feel free to steer us in any direction you'd like.

Here are a few options:

1. **Learning a new language**: We could explore the basics of a specific language, such as grammar rules, vocabulary, and conversation techniques.
2. **Science and technology**: If you're interested in STEM topics, we could delve into subjects like physics, chemistry, computer science, or data analysis.
3. **Critical thinking and problem-solving**: We could work on developing your critical thinking skills through exercises, puzzles, and brain teasers.
4. **Creative writing or art**: We could explore writing techniques, storytelling methods, or discuss various art forms.
5. **Just for fun**: We could play a game, such as "What if...?", explore hypothetical scenarios, or discuss a current event.

Which of these options sounds appealing to you? Or do you have something else in mind?

(By the way, I'll make sure to check in with you regularly to ensure you understand the concepts and adjust our pace accordingly.)

--------------------------------------------------------------------------------
studentAgent (to teacherAgent):

Wow, all those options are fascinating!

After considering each one, I think I'd like to start with... **Learning a new language**! I've always been curious about languages other than my own, and I'd love to explore the basics of grammar rules, vocabulary, and conversation techniques.

However, before we dive in, can you tell me more about how language learning will work here? Will it be through interactive conversations, quizzes, or perhaps just by reading and writing examples?

Also, which language would you recommend starting with? I'm open to suggestions!

(And don't worry, I'll definitely let you know if I need more clarification on any of the concepts - after all, that's what this "learning" part is all about!)

--------------------------------------------------------------------------------
teacherAgent (to studentAgent):

I'm thrilled you chose learning a new language as our first topic.

**Language Learning Process**: We can use a combination of methods to learn a new language. Here's an overview of how we'll work together:

* **Interactive Conversations**: We'll have regular conversations in the target language, where I'll ask questions, provide prompts, and engage in discussions on various topics.
* **Vocabulary Building**: We'll focus on learning new words and phrases through context clues, word associations, and exercises like matching and filling in the blanks.
* **Grammar Explanation**: I'll break down grammar rules and explain concepts using analogies, examples, and visual aids to help you understand.
* **Reading and Writing**: We'll practice reading and writing in the target language, starting with simple texts and gradually moving on to more complex materials.

**Language Recommendation**: Considering your curiosity about languages other than your own, I recommend starting with a relatively easy-to-learn language that's also a popular choice for beginners. Let me suggest **Spanish**, **French**, or **Italian** as our first target language!

All three languages share similarities with English and have many cognates (words that are similar in both languages), making them more accessible to learners.

Which one of these three languages resonates with you, or would you like me to recommend another language based on your interests?

(And don't worry; we'll adjust the difficulty level as needed. If you find a particular concept challenging, we can slow down and revisit it together.)

--------------------------------------------------------------------------------

>>>>>>>> TERMINATING RUN (3fbc95b6-b2d3-4746-b947-f1df4adbf09a): Maximum number of consecutive auto-replies reached

----- Conversation Output -----

ChatResult(chat_id=307019191727651587477976195993899110976, chat_history=[{'content': 'Hello! What would you like to learn today?', 'role': 'assistant', 'name': 'teacherAgent'}, {'content': 'That\\'s great that I get to start fresh every day!\\n\\nHmm... I\\'m not really sure where to begin. Is there a new topic or subject we could explore together? Or maybe I could try to learn something through conversation?\\n\\nCan you give me some suggestions? What are some interesting topics or questions that I could ask you about?\\n\\nOh, and also... is this a kind of "teaching" session where I get to be the student, or can we have a more free-form conversation?', 'role': 'user', 'name': 'studentAgent'}, {'content': 'I\\'m glad you\\'re excited to start fresh!\\n\\nWe can definitely do a combination of both - structured learning and conversational exploration. I\\'d like to propose some topics that might interest you, but feel free to steer us in any direction you\\'d like.\\n\\nHere are a few options:\\n\\n1. **Learning a new language**: We could explore the basics of a specific language, such as grammar rules, vocabulary, and conversation techniques.\\n2. **Science and technology**: If you\\'re interested in STEM topics, we could delve into subjects like physics, chemistry, computer science, or data analysis.\\n3. **Critical thinking and problem-solving**: We could work on developing your critical thinking skills through exercises, puzzles, and brain teasers.\\n4. **Creative writing or art**: If you enjoy creative pursuits, we could explore writing techniques, storytelling methods, or even discuss various art forms.\\n5. **Just for fun**: We could play a game, such as "What if...?", explore hypothetical scenarios, or engage in a thought-provoking discussion on a current event.\\n\\nWhich of these options sounds appealing to you? Or do you have something else in mind?\\n\\n(By the way, I\\'ll make sure to check in with you regularly to ensure you understand the concepts and adjust our pace accordingly.)', 'role': 'assistant', 'name': 'teacherAgent'}, {'content': 'Wow, all those options are fascinating!\\n\\nAfter considering each one, I think I\\'d like to start with... **Learning a new language**! I\\'ve always been curious about languages other than my own, and I\\'d love to explore the basics of grammar rules, vocabulary, and conversation techniques.\\n\\nHowever, before we dive in, can you tell me more about how language learning will work here? Will it be through interactive conversations, quizzes, or perhaps just by reading and writing examples?\\n\\nAlso, which language would you recommend starting with? I\\'m open to suggestions!\\n\\n(And don\\'t worry, I\\'ll definitely let you know if I need more clarification on any of the concepts - after all, that\\'s what this "learning" part is all about!)', 'role': 'user', 'name': 'studentAgent'}, {'content': "I\\'m thrilled you chose learning a new language as our first topic.\\n\\n**Language Learning Process**: We can use a combination of methods to learn a new language. Here\\'s an overview of how we\\'ll work together:\\n\\n* **Interactive Conversations**: We\\'ll have regular conversations in the target language, where I\\'ll ask questions, provide prompts, and engage in discussions on various topics.\\n* **Vocabulary Building**: We\\'ll focus on learning new words and phrases through context clues, word associations, and exercises like matching and filling in the blanks.\\n* **Grammar Explanation**: I\\'ll break down grammar rules and explain concepts using analogies, examples, and visual aids to help you understand.\\n* **Reading and Writing**: We\\'ll practice reading and writing in the target language, starting with simple texts and gradually moving on to more complex materials.\\n\\n**Language Recommendation**: Considering your curiosity about languages other than your own, I recommend starting with a relatively easy-to-learn language that's also a popular choice for beginners. Let me suggest **Spanish**, **French**, or **Italian** as our first target language!\\n\\nAll three languages share similarities with English and have many cognates (words that are similar in both languages), making them more accessible to learners.\\n\\nWhich one of these three languages resonates with you, or would you like me to recommend another language based on your interests?\\n\\n(And don't worry; we'll adjust the difficulty level as needed. If you find a particular concept challenging, we can slow down and revisit it together.)", 'role': 'assistant', 'name': 'teacherAgent'}])
```
