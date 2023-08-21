"""
order of logic:
- user chooses either of 3 types of reco (text input)
- get recipe reco (gpt api call)
- process recipe reco (gpt api call)
- return list of processed recommendations
"""
# imports
import streamlit as st
import openai
import uuid
from app_logger import logger

from langchain.llms import OpenAI
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.prompts import PromptTemplate

def create_chain(prompt_template,input_variables,temperature,model_name,api_key,max_tokens=1000):
    """
    :param parser_prompt_template:
    :param input_variables: list of string
    :param temperature:
    :param model_name:
    :param max_tokens:
    :param api_key:
    :return:
    """
    llm = OpenAI(api_key=api_key,model_name=model_name,max_tokens=max_tokens,temperature=temperature)
    prompt_template = PromptTemplate(template=prompt_template,
                                     input_variables=input_variables)
    return LLMChain(llm=llm,prompt=prompt_template)


def get_recipe_reco_in_json(reco_type,
                            recipe_reco_prompt_template,
                            json_parser_prompt_template,
                            user_input_text,
                            api_key,
                            reco_temperature=1.0,parser_temperature=0.0,
                            model_name='text-davinci-003'):
    # generate search id
    search_uuid = uuid.uuid4()
    logger.info(f"Search uuid: {search_uuid}")
    logger.info(f"Prompt type: {reco_type}")

    reco_chain = create_chain(prompt_template=recipe_reco_prompt_template,
                              input_variables=['user_input'],
                              temperature=reco_temperature,
                              model_name=model_name,
                              api_key=api_key)
    json_parser_chain = create_chain(prompt_template=json_parser_prompt_template,
                                     input_variables=['recipe_list'],
                                     temperature=parser_temperature,
                                     model_name=model_name,
                                     api_key=api_key)
    reco_output_chain = SimpleSequentialChain(chains=[reco_chain,json_parser_chain])

    try:
        recipe_response_json = reco_output_chain.run(user_input_text)
        return recipe_response_json
    except (openai.error.Timeout, openai.error.APIError,
            openai.error.APIConnectionError, openai.error.RateLimitError) as e:
        logger.error("Error while making API call: ", e)
        st.write("An error has occurred while requesting. Please try again after a while.")
        return None
    except openai.error.InvalidRequestError as e:
        logger.error("Error while making API call: ", e)
        st.write("An error has occurred while requesting. Please try again after a while.")
        return None
    except (openai.error.AuthenticationError, openai.error.PermissionError) as e:
        logger.error("Error while making API call: ", e)
        st.write("An error has occurred while requesting. Please try again after a while.")
        return None

