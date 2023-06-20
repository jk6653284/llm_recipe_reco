import os
import json
import streamlit as st
from recipe_recommendations import get_recipe_reco_in_json
from app_logger import logger

# configs, to move to another file later
current_dir = os.path.dirname(os.path.abspath(__file__))
model = "text-davinci-003"
recipe_reco_temperature = 1.0
recipe_parser_temperature=0.0
#openai_api_key = st.secrets["open_ai"]["api_key"]
import dotenv
dotenv.load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# prompts
with open(os.path.join(current_dir, "prompts/prompt_recipe_json_format.txt"), 'r') as f:
    JSON_FORMAT_PROMPT = f.read()
with open(os.path.join(current_dir, "prompts/prompt_ingredient_reco.txt"), 'r') as f:
    PROMPT_PREFIX_INGREDIENT_RECO = f.read()
# with open(os.path.join(current_dir,"prompts/prompt_mood_reco.txt"), 'r') as f:
#     PROMPT_PREFIX_MOOD = f.read()
# with open(os.path.join(current_dir,"prompts/prompt_pair_reco.txt"), 'r') as f:
#     PROMPT_PREFIX_PAIR = f.read()


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
        st.write(result_json['description'], wrap=True)

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
                         options=('ingredient', 'mood', 'pairing')
                         )
    reco_response = ''

    if reco_type == 'ingredient':
        user_input_text = st.text_input("List one or more ingredients (e.g. 'black olives') separated by comma: ")
        if user_input_text.strip() != '':
            reco_response = get_recipe_reco_in_json(reco_type=reco_type,
                                                    recipe_reco_prompt_template=PROMPT_PREFIX_INGREDIENT_RECO,
                                                    json_parser_prompt_template=JSON_FORMAT_PROMPT,
                                                    user_input_text=user_input_text,
                                                    api_key=openai_api_key,
                                                    reco_temperature=recipe_reco_temperature,
                                                    parser_temperature=recipe_parser_temperature,
                                                    model_name=model)
    # elif reco_type == 'mood':
    #     user_input_text = st.text_input("Give a short description of what you feel like eating or the occasion (e.g. birthday party finger food): ")
    #     if user_input_text.strip() != '':
    #         gpt_response_text = get_recipe_recommendation(
    #             user_input=user_input_text,
    #             prompt_prefix=PROMPT_PREFIX_MOOD,
    #             temperature=recipe_reco_temperature,
    #             reco_type=reco_type,
    #             model=model
    #         )
    # elif reco_type == 'pairing':
    #     user_input_text = st.text_input("Give a recipe that you want pairings for (e.g. caprese salad): ")
    #     if user_input_text.strip() != '':
    #         gpt_response_text = get_recipe_recommendation(
    #             user_input=user_input_text,
    #             prompt_prefix=PROMPT_PREFIX_PAIR,
    #             temperature=recipe_reco_temperature,
    #             reco_type=reco_type,
    #             model=model
    #         )
    else:
        st.write("Not available")

    # convert results to json
    if reco_response != '' or reco_response is not None:
        reco_response_json = json.loads(reco_response)
        blocks = st.columns(len(reco_response_json))
        for block, response in zip(blocks, reco_response_json):
            format_results_in_blocks(block, response)
    else:
        st.write("Cannot parse response. Please try again or check the logs.")


if __name__ == "__main__":
    main()
