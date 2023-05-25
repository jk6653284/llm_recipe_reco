import openai
from dotenv import load_dotenv
import os
import streamlit as st

# environment vars
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# configs, to move to another file later
model = "gpt-3.5-turbo"
# user_input_prefix = "I want recipe recommendation that includes the following ingredients: "
# system instruction
user_input_prefix = """
You are a recipe recommendation engine. Your task is to give at most 5 recipes that involves one or more ingredient given by the user. Return the name of the recipe, type of cuisine if it exists, and a brief description of the dish. If the dish is from a particular cuisine, also include the original language name and english pronunciation of the name. If recipe is not from a specific cuisine, give back 'no specific cuisine' as cuisine type. Give result back in the following format:
- <recipe title> (<original language title>, english pronunciation)
- cuisine type
- description

ingredients: 
"""
temperature = 1.0 # later make it variable depending on user input


# generic function to get chat completion response
def get_chat_completion_response(user_input,
                                 user_input_prefix=user_input_prefix,
                                 #system_instruction=system_instruction,
                                 temperature=temperature
                                 ):
    """
    function to return response from gpt's chat completion api given user input
    :param user_input:
    :param user_input_prefix:
    :param system_instruction:
    :param temperature:
    :return:
    """
    messages = [
        {"role": "user", "content": user_input_prefix+user_input}
    ]
    chat_completion_response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature

    )
    response_text = chat_completion_response['choices'][0]['message']['content']
    return response_text


def test_st_input_text(txt):
    return f"You have listed: {txt}"


def main():
    """
    main function to run streamlit app
    """
    st.title("Test test testttttt")

    # user text input
    user_input_text = st.text_input("List one or more ingredients divided by comma: ")
    if user_input_text:
        s = get_chat_completion_response(user_input=user_input_text,
                                         user_input_prefix=user_input_prefix,
                                         #system_instruction=system_instruction,
                                         temperature=temperature)
        st.write(s)
    else:
        st.write("You have not given any input.")


if __name__ == "__main__":
    main()
