import openai
from dotenv import load_dotenv
import os
import streamlit as st

# environment vars
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# configs, to move to another file later
model = "gpt-3.5-turbo"

# prompts
PROMPT_PREFIX_INGREDIENT_RECO = """
You are a recipe recommendation engine. Your task is to give at most 5 recipes that involves one or more ingredient given by the user. Return the name of the recipe, type of cuisine if it exists, and a brief description of the dish. If the dish is from a particular cuisine, also include the original language name and english pronunciation of the name. If recipe is not from a specific cuisine, give back 'no specific cuisine' as cuisine type. For description, keep it concise and include things like type of dish, other main ingredients, short description of the dish, and how the dish is typically enjoyed. Give result back in the following format:
- <recipe title> (<original language title>, english pronunciation)
- cuisine type
- description

ingredients: 
"""

PROMPT_PREFIX_MOOD = """
You are a recipe recommendation engine. Your task is to give at most 5 recipes that is appropriate for user's input mood or occasion. Return the name of the recipe, type of cuisine if it exists, and a brief description of the dish. If the dish is from a particular cuisine, also include the original language name and english pronunciation of the name. If recipe is not from a specific cuisine, give back 'no specific cuisine' as cuisine type. For description, keep it concise and include things like type of dish, main ingredients, short description of the dish, why the dish is appropriate, and how the dish is typically enjoyed. Give result back in the following format:
- <recipe title> (<original language title>, english pronunciation)
- cuisine type
- description

user input: 
"""

PROMPT_PREFIX_PAIR = """
You are a recipe recommendation engine. Your task is to give at most 5 recipes that is often served with user's input recipe. Return the name of the recipe, type of cuisine if it exists, and a brief description of the dish. If the dish is from a particular cuisine, also include the original language name and english pronunciation of the name. If recipe is not from a specific cuisine, give back 'no specific cuisine' as cuisine type. For description, keep it concise and include things like type of dish, main ingredients, short description of the dish, and why it is served together. Give result back in the following format:
- <recipe title> (<original language title>, english pronunciation)
- cuisine type
- description

input recipe:
"""

temperature = 1.0 # later make it variable depending on user input


# generic function to get chat completion response
def get_chat_completion_response(user_input,
                                 prompt_prefix,
                                 temperature
                                 ):
    """
    function to return response from gpt's chat completion api given user input
    :param user_input:
    :param prompt_prefix:
    :param temperature:
    :return:
    """
    messages = [
        {"role": "user", "content": prompt_prefix+user_input}
    ]
    chat_completion_response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    response_text = chat_completion_response['choices'][0]['message']['content']
    return response_text


def main():
    """
    main function to run streamlit app
    """
    st.title("GPT powered recipe recommendation")

    reco_type = st.radio(label="select the type of recommendation",
                         options=('ingredient', 'mood', 'pairing')
                         )

    if reco_type == 'ingredient':
        user_input_text = st.text_input("List one or more ingredients (e.g. 'black olives') separated by comma: ")
        if user_input_text.strip() != '':
            gpt_response_text = get_chat_completion_response(
                user_input=user_input_text,
                prompt_prefix=PROMPT_PREFIX_INGREDIENT_RECO,
                temperature=temperature
            )
            st.write(gpt_response_text)
    elif reco_type == 'mood':
        user_input_text = st.text_input("Give a short description of what you feel like eating or the occasion (e.g. birthday party finger food): ")
        if user_input_text.strip() != '':
            gpt_response_text = get_chat_completion_response(
                user_input=user_input_text,
                prompt_prefix=PROMPT_PREFIX_MOOD,
                temperature=temperature
            )
            st.write(gpt_response_text)
    elif reco_type == 'pairing':
        user_input_text = st.text_input("Give a recipe that you want pairings for (e.g. caprese salad): ")
        if user_input_text.strip() != '':
            gpt_response_text = get_chat_completion_response(
                user_input=user_input_text,
                prompt_prefix=PROMPT_PREFIX_PAIR,
                temperature=temperature
            )
            st.write(gpt_response_text)
    else:
        st.write("Not ready yet!")


if __name__ == "__main__":
    main()
