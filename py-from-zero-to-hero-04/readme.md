# Quick Chat setup

# Let´s build our streamlit Chat  

### Add a new folder "py-from-zero-to-hero-04"
```
mkdir py-from-zero-to-hero-04
cd py-from-zero-to-hero-04
```

### So, then let´s build a dynamic environment named "chat"
```
python -m venv chat
```

### And activate our new dynamic env "chat" 
#### Windows
```
.\chat\Scripts\activate
```
#### Linux 
```
source ./chat/bin/activate
```

### Rather than installing packages one by one, let´s use our dependencies file :)
```
pip install -r .\requirements.txt
```

### Finally, we should confirm whether our packages were properly installed
```
pip list
```

# (1) Building a streamlit Chat

### (1.1) Env file

Use this file to specify the base LLM API URL.

- APP_BACKEND_URL=http://localhost:5000

### (1.2) Config file

This configuration file is only a reference for .env file

```
class Config:
    APP_BACKEND_URL = os.environ.get("APP_BACKEND_URL", "")
```

### (1.3) Basic Setup 

In the first code lines, after importing streamlit, we define:
- "title": Best Price 
- "subtitle": Customer Service for our client APP
- "logo": st.image("best-price-logo.png", caption="Best Price")

```
import streamlit as st

st.markdown("<h1 style='text-align: center;'>Best Price</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Customer Service</h3>", unsafe_allow_html=True)
left_co, cent_co,last_co = st.columns(3)
with cent_co:
    st.image("best-price-logo.png", caption="Best Price")
```

Since our backend endpoint needs a client_id to identify the client side request.
The code below searches for a client_id into the session state, otherwise, a GUID is going to be used

```
# generate a client_id to be used during the chat
if "client_id" not in st.session_state:
    st.session_state.client_id = str(uuid.uuid4())
```

So, then, we try to load some history content

```
# load messages
if "messages" not in st.session_state:
    st.session_state.messages = []
```


### (1.4) Let´s prepare que question method 

This method below is a callback for streamlit and it will be used to send user inputs to the backend api
```
def ask_question(question):
    url = config_class.APP_BACKEND_URL + "/info"
    payload = {
        "client_id": st.session_state.client_id,
        "question": question
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
       return response.json().get("answer", "Error trying to get the server answer.")
    if response.status_code in [400, 404]:
       return response.json().get("error", "Error trying to get the server answer.")
    return f"Erro: {response.status_code} - {response.text}"

```

### (1.5) Refresh chat with previous content

```
# load messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
```

### (1.6) Define roles: bot and user
User settings
```
st.session_state.messages.append({"role": "user", "content": prompt})
st.chat_message("user").markdown(prompt)
```

Bot assistant
```
st.session_state.messages.append({"role": "assistant", "content": answer})
with st.chat_message("assistant"):
  st.markdown(answer)
```

### (1.7) Running the app
```
python chat.py
```

### So, let's run a quick demo to showcase what we've accomplished so far.
<p align="center">
  <img src="https://github.com/renatomatos79/cgi-python-adventure/blob/main/images/chat-ok.gif" height="400px" width="100%" alt="LLM API Demo">
</p>
