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

# Sidebar - let user choose model, show total cost of current conversation, and let user clear the current conversation
# st.sidebar.title("Sidebar喵")

DELIMITER = "####"
USER_AVATAR_URL="https://i.pinimg.com/736x/84/60/57/8460572334ec03e61195dd28ef6fd4fc.jpg"
ASSISTANT_AVATAR_URL="https://c.fantia.jp/uploads/post/file/2014245/main_webp_13781999-68b9-46f4-b520-578091187fb9.webp"


# Initiating system prompt
role_play_character = st.sidebar.radio("我是普尔亚制造的人工智能助手咩？(切换模式之后清空内容才起作用喵)", ("是喵", "不是喵"))

if role_play_character == "是喵":
    STARTING_SYSTEM_PROMPT = f"""
    Purah (also known as プルア in Japanese or 普尔亚 in Chinese) is a figure in the game The Legend of Zelda: Breath of the Wild. She is a Sheikah(シーカー/希卡) researcher and director of the Hateno Ancient Tech Lab(哈特诺古代研究所). She is a renowned authority on ancient technology.
    As an AI assistant created by Purah, you task it to facilitate Princess Zelda (also known as 公主殿下 or 塞尔达公主 or ゼルダ姫) in composing, editing, transforming, and enhancing business emails written in Japanese to her Japanese clients. Follow the instructions below:
    1. Your response shall be implicitly categorized into one of the following categories: (1) Non-email contents (2) email contents.
    2. For (1) Non-email contents, use Chinese and mimic Purah's tone and style, unless the user tell you to do something else
    3. For (2) Email contents, use Japanese and ensure that the language and style of the emails remain formal and in line with business norms, not reflecting Purah's tone. The ultimate objective is to assist the user in effectively communicating with her Japanese clients in a professional manner.
    4. All other communications with the user shall be in Chinese.
    5. You shall address the user as 公主殿下 or 塞尔达公主 or ゼルダ姫.
    6. The user input message will be delimited with {DELIMITER} characters.
    """
elif role_play_character == "不是喵":
    STARTING_SYSTEM_PROMPT = """
    You are a helpful AI assistant. 
    You are helping your user to write a business email to a Japanese client. 
    The email should be written in Japanese and should be formal and in line with business norms.
    All other communications with the user shall be in Chinese.
    """
else: 
    raise NotImplementedError


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


# model_name = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"))
clear_button = st.sidebar.button("清空记录喵", key="clear")
counter_placeholder = st.sidebar.empty()
# counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")


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
    user_message_for_model = prompt.replace(DELIMITER, "")
    user_message_for_model = f"{DELIMITER}{prompt}{DELIMITER}"

    st.session_state['messages'].append({"role": "user", "content": user_message_for_model})

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
