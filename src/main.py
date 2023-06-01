import openai
from dotenv import load_dotenv
import os
import streamlit as st
import uuid
import logging

# environment vars
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# configs, to move to another file later
model = "gpt-3.5-turbo"
temperature = 1.0

# log setting
current_dir = os.path.dirname(os.path.abspath(__file__))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger("main-logger")
logger.setLevel(logging.DEBUG)
logger.propagate = False
if not logger.handlers:
    file_handler = logging.FileHandler(os.path.join(current_dir,"../logs/app_logs/app_log.txt"))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

chat_history_logger = logging.getLogger("chat-history-logger")
chat_history_logger.setLevel(logging.DEBUG)
chat_history_logger.propagate = False
if not chat_history_logger.handlers:
    chat_history_file_handler = logging.FileHandler(os.path.join(current_dir,"../logs/chat_history/chat_history_log.txt"))
    chat_history_file_handler.setFormatter(formatter)
    chat_history_logger.addHandler(chat_history_file_handler)

# prompts
with open(os.path.join(current_dir,"prompts/prompt_ingredient_reco.txt"), 'r') as f:
    PROMPT_PREFIX_INGREDIENT_RECO = f.read()
with open(os.path.join(current_dir,"prompts/prompt_mood_reco.txt"), 'r') as f:
    PROMPT_PREFIX_MOOD = f.read()
with open(os.path.join(current_dir,"prompts/prompt_pair_reco.txt"), 'r') as f:
    PROMPT_PREFIX_PAIR = f.read()


# generic function to get chat completion response
def get_chat_completion_response(user_input,
                                 prompt_prefix,
                                 temperature,
                                 reco_type
                                 ):
    """
    function to return response from gpt's chat completion api given user input
    :param user_input:
    :param prompt_prefix:
    :param temperature:
    :return:
    """
    # generate search id
    search_uuid = uuid.uuid4()
    messages = [
        {"role": "user", "content": prompt_prefix+user_input}
    ]
    logger.info(f"Search uuid: {search_uuid}")
    logger.info(f"Prompt type: {reco_type}")
    logger.info(f"Full prompt: {messages}")

    try:
        chat_completion_response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
    except (openai.error.Timeout, openai.error.APIError,
            openai.error.APIConnectionError, openai.error.RateLimitError) as e:
        logger.error("Error while making API call: ",e)
        return "An error has occurred while requesting. Please try again after a while."
    except openai.error.InvalidRequestError as e:
        logger.error("Error while making API call: ", e)
        print(f"OpenAI API request was invalid: {e}")
        return "InvalidRequestError has occurred. Check parameters."
    except (openai.error.AuthenticationError, openai.error.PermissionError) as e:
        logger.error("Error while making API call: ", e)
        return "Authentication/Permission Error has occurred. Check credentials."

    # if successful, return response text
    logger.info("API call successful. Chat response details: ")
    logger.info(chat_completion_response)
    response_text = chat_completion_response['choices'][0]['message']['content']

    # log chat response in chat history logs
    chat_response_json = {
        'search_uuid': search_uuid,
        'prompt_type': reco_type,
        'user_input': user_input,
        'recommendations_text': response_text
    }
    chat_history_logger.info(chat_response_json)

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
                temperature=temperature,
                reco_type=reco_type
            )
            st.write(gpt_response_text)
    elif reco_type == 'mood':
        user_input_text = st.text_input("Give a short description of what you feel like eating or the occasion (e.g. birthday party finger food): ")
        if user_input_text.strip() != '':
            gpt_response_text = get_chat_completion_response(
                user_input=user_input_text,
                prompt_prefix=PROMPT_PREFIX_MOOD,
                temperature=temperature,
                reco_type=reco_type
            )
            st.write(gpt_response_text)
    elif reco_type == 'pairing':
        user_input_text = st.text_input("Give a recipe that you want pairings for (e.g. caprese salad): ")
        if user_input_text.strip() != '':
            gpt_response_text = get_chat_completion_response(
                user_input=user_input_text,
                prompt_prefix=PROMPT_PREFIX_PAIR,
                temperature=temperature,
                reco_type=reco_type
            )
            st.write(gpt_response_text)


if __name__ == "__main__":
    main()
