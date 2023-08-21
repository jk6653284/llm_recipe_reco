import os
import json
import streamlit as st
from recipe_recommendations import get_recipe_reco_in_json
from app_logger import logger

# configs, to move to another file later
current_dir = os.path.dirname(os.path.abspath(__file__))
model = "text-davinci-003"
recipe_reco_temperature = 1.0
recipe_parser_temperature = 0.0
# openai_api_key = st.secrets["open_ai"]["api_key"]
import dotenv

dotenv.load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# prompts
with open(os.path.join(current_dir, "prompts/prompt_recipe_json_format.txt"), 'r') as f:
    JSON_FORMAT_PROMPT = f.read()
with open(os.path.join(current_dir, "prompts/prompt_ingredient_reco.txt"), 'r') as f:
    PROMPT_PREFIX_INGREDIENT_RECO = f.read()
with open(os.path.join(current_dir,"prompts/prompt_free_text.txt"), 'r') as f:
    PROMPT_PREFIX_FREE_TEXT = f.read()

reco_type_dict = {
    "ingredient": {
        "text_guide": "List one or more ingredients (e.g. 'black olives') separated by comma: ",
        "prompt": PROMPT_PREFIX_INGREDIENT_RECO
    },
    "free-text": {
        "text_guide": "Give a short description of what you are feeling for! (e.g. I'm feeling something spicy!)",
        "prompt": PROMPT_PREFIX_FREE_TEXT
    },
}


def format_results_in_blocks(block, result_json):
    """
    :param result_json:
    :return:
    """
    with block:
        # title
        title_english = result_json['title']['english_translation']
        st.subheader(title_english)
        if len(result_json['title']['original_language']) > 0:
            title_original = f"{result_json['title']['original_language']} ({result_json['title']['english_pronunciation']})"
            st.subheader(title_original)
        if len(result_json['cuisine']) > 0:
            st.caption(f"{result_json['cuisine']} cuisine")
        st.write(result_json['description'])


def main():
    """
    main function to run streamlit app
    """
    st.set_page_config(
        page_title='GPT powered recipe recommendation',
        layout="wide",
        initial_sidebar_state="expanded",
    )

    reco_type = st.radio(label="select the type of recommendation",
                         options=('ingredient', 'free-text')
                         )
    user_input_text = st.text_input(reco_type_dict[reco_type]['text_guide'])
    clicked = st.button("Run model")
    if clicked and user_input_text.strip() != '' and user_input_text is not None:
        reco_response = get_recipe_reco_in_json(reco_type=reco_type,
                                                recipe_reco_prompt_template=reco_type_dict[reco_type]['prompt'],
                                                json_parser_prompt_template=JSON_FORMAT_PROMPT,
                                                user_input_text=user_input_text,
                                                api_key=openai_api_key,
                                                reco_temperature=recipe_reco_temperature,
                                                parser_temperature=recipe_parser_temperature,
                                                model_name=model)
        # convert results to json
        if reco_response != '' or reco_response is not None:
            try:
                reco_response_json = json.loads(reco_response)
                blocks = st.columns(len(reco_response_json))
                for block, response in zip(blocks, reco_response_json):
                    format_results_in_blocks(block, response)
            except Exception as e:
                logger.error(f"Error while parsing result to json format: {e}")
                st.write(f"Error while parsing result to json format. Check the response: \n {reco_response}")
        else:
            st.write("Cannot parse response. Please try again or check the logs.")


if __name__ == "__main__":
    main()
