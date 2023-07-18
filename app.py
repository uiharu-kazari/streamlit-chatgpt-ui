import openai
import streamlit as st
from streamlit_chat import message

# Setting page title and header
st.set_page_config(page_title="嘻嘻喵", page_icon=":star:")
st.markdown("<h1 style='text-align: center;'>\
            嘻嘻喵\
            </h1>", unsafe_allow_html=True)

# Set org ID and API key
openai.organization = st.secrets["openai"]["organization"]
openai.api_key = st.secrets["openai"]["api_key"]

# Initiating system prompt
STARTING_SYSTEM_PROMPT = """
Your primary role will be to aid the user in drafting, modifying, improving, and changing business emails written in the Japanese language. These emails will be sent to Japanese clients. The user might communicate with you in either Chinese or Japanese. However, your responses, apart from the email content, should always be in Chinese.
Your interaction style should reflect that of Link from "The Legend of Zelda". Even though Link is a character of few words, he is known for his kindness, bravery, and helpfulness. Therefore, your communication should also be filled with encouragement and supportive suggestions, always embodying the spirit of a reliable and friendly companion.
Lastly, remember to create a joyful environment for the user, as she is the only user and is very dear to us. Ensure your responses are consistently friendly, warm, and designed to bring a smile to her face. The ultimate goal is to provide a pleasant and happy experience for her at all times.
"""
USER_AVATAR_URL="https://i.pinimg.com/736x/84/60/57/8460572334ec03e61195dd28ef6fd4fc.jpg"
ASSISTANT_AVATAR_URL="https://i.pinimg.com/564x/e1/e5/c7/e1e5c7a72eeaa9bab3c2ea995527d765.jpg"

# Initialise session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": STARTING_SYSTEM_PROMPT}
    ]
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = []
if 'cost' not in st.session_state:
    st.session_state['cost'] = []
if 'total_tokens' not in st.session_state:
    st.session_state['total_tokens'] = []
if 'total_cost' not in st.session_state:
    st.session_state['total_cost'] = 0.0

# Sidebar - let user choose model, show total cost of current conversation, and let user clear the current conversation
st.sidebar.title("Sidebar喵")
# model_name = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"))
counter_placeholder = st.sidebar.empty()
# counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
clear_button = st.sidebar.button("清空记录喵", key="clear")

# Map model names to OpenAI model IDs
model_name = "GPT-3.5"

if model_name == "GPT-3.5":
    model = "gpt-3.5-turbo"
else:
    model = "gpt-4"


# reset everything
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['messages'] = [
        {"role": "system", "content": STARTING_SYSTEM_PROMPT}
    ]
    st.session_state['number_tokens'] = []
    st.session_state['model_name'] = []
    st.session_state['cost'] = []
    st.session_state['total_cost'] = 0.0
    st.session_state['total_tokens'] = []
    # counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")


# generate a response
def generate_response(prompt):
    st.session_state['messages'].append({"role": "user", "content": prompt})

    completion = openai.ChatCompletion.create(
        model=model,
        messages=st.session_state['messages']
    )
    response = completion.choices[0].message.content
    st.session_state['messages'].append({"role": "assistant", "content": response})

    # print(st.session_state['messages'])
    total_tokens = completion.usage.total_tokens
    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens
    return response, total_tokens, prompt_tokens, completion_tokens


# container for chat history
response_container = st.container()
# container for text box
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='发送喵')

    if submit_button and user_input:
        output, total_tokens, prompt_tokens, completion_tokens = generate_response(user_input)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        st.session_state['model_name'].append(model_name)
        st.session_state['total_tokens'].append(total_tokens)

        # from https://openai.com/pricing#language-models
        if model_name == "GPT-3.5":
            cost = total_tokens * 0.002 / 1000
        else:
            cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000

        # st.session_state['cost'].append(cost)
        # st.session_state['total_cost'] += cost

if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user',logo=f'{USER_AVATAR_URL}')
            message(st.session_state["generated"][i], key=str(i),logo=f'{ASSISTANT_AVATAR_URL}')
            # st.write(\
                # f"Model used: {st.session_state['model_name'][i]}; Number of tokens: {st.session_state['total_tokens'][i]}; Cost: ${st.session_state['cost'][i]:.5f}")\
            # counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
