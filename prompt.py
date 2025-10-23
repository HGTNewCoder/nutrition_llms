from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain_google_vertexai import VertexAI
from flask import request
import os
from dotenv import load_dotenv
load_dotenv()

# Initialize LLM model
my_llm_model = VertexAI(
    model=os.getenv("MODEL"),
    project=os.getenv("PROJECT"),
    location=os.getenv("LOCATION")
)

# Template for nutrition and exrcise
template_nutrition_food_exercise = """
You are a medical nutrition expert.

ONLY return a clean and concise list of 5-10 specific nutrition items in 5 main nutrients (only the exact names of foods) and the exercise which is suitable for that person
No explanations, no paragraphs, no notes, no disclaimers.If there is more than 1 disease combine it together to

Format exactly as follows:

**Disease Name 1**
Food:               Exercise:
    -                       -
    -                       -
    -                       -
    -                       -
    -                       -

The characterlistic of person : {information}

"""

prompt_nutrition_food_exercise = PromptTemplate(
    input_variables=["information"],
    template=template_nutrition_food_exercise,
)

nutrition_food_exercise_chain = LLMChain(llm=my_llm_model, prompt=prompt_nutrition_food_exercise)


template_routine = """
You are a medical nutrition expert.

Can you help me to create the routine based on {list_of_food_and_exercise} from 5-6 am to 10-11 pm? Make a table

Please do not give me the important and recommendation, just only the table of the routine
"""
prompt_routine = PromptTemplate(
    input_variables=["list_of_food_and_exercise"],
    template=template_routine,
)

routine_chain = LLMChain(llm=my_llm_model, prompt=prompt_routine)

# Combine both chains
chain = SimpleSequentialChain(chains=[nutrition_food_exercise_chain, routine_chain])


# Template of the important thing
template_nutrition_important ="""
You are a medical nutrition expert.

The characterlistic of person : {question}

Exmaple form:" - what you should do to protect yourself of diesease ?
               - what the things you have always carry with when you get the diesease ?
               - Any way to support that person
               
             "
Help me list the essential thing that you have to notice when you get that disease with the (Example form)

Follow the formant:
Important:
    -
    -
    -
    -
"""

prompt_nuitrion_important= PromptTemplate(
    input_variables=["information"],
    template=template_nutrition_important,
)

important_chain= LLMChain(llm=my_llm_model, prompt=prompt_nuitrion_important)


def generate_routine():
    """
    Input:
        diseases: list of disease names (strings)
        weight: user's weight in kg (float)
    Output:
        str: LLM-generated routine text
    """
    # Build input string
    name = request.form.get("name")
    age = request.form.get("age")
    weight = float(request.form.get("weight"))
    height = request.form.get('height')
    sex = request.form.get('sex')
    race = request.form.get('race')
    selected_diseases = request.form.getlist("disease")
    question_str = f"Diseases: {', '.join(selected_diseases)}; Weight: {weight}kg ; Age:{age} ; Height: {height}cm ; Sex: {sex} ; Race: {race}"
    answer = chain.run(question_str)
    return answer

def generate_food_exercise():
    # build input string
    name = request.form.get("name")
    age = request.form.get("age")
    weight = float(request.form.get("weight"))
    height = request.form.get('height')
    sex = request.form.get('sex')
    race = request.form.get('race')
    selected_diseases = request.form.getlist("disease")
    question_str = f"Diseases: {', '.join(selected_diseases)}; Weight: {weight}kg ; Age:{age} ; Height: {height}cm ; Sex: {sex} ; Race: {race}"
    answer = nutrition_food_exercise_chain.run(question_str)
    return answer

def generate_important():
    # build input string
    name = request.form.get("name")
    age = request.form.get("age")
    weight = float(request.form.get("weight"))
    height = request.form.get('height')
    sex = request.form.get('sex')
    race = request.form.get('race')
    selected_diseases = request.form.getlist("disease")
    question_str = f"Diseases: {', '.join(selected_diseases)}; Weight: {weight}kg ; Age:{age} ; Height: {height}cm ; Sex: {sex} ; Race: {race}"
    answer = important_chain.run(question_str)
    return answer