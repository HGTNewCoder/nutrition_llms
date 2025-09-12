from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain_google_vertexai import VertexAI

import os
from dotenv import load_dotenv
load_dotenv()

# Initialize LLM model
my_llm_model = VertexAI(
    model=os.getenv("MODEL"),
    project=os.getenv("PROJECT"),
    location=os.getenv("LOCATION")
)

# Template for nutrition and exercise
template_nutrition_excercise = """
You are a medical nutrition expert.

ONLY return a clean and concise list of 5-10 specific nutrition items in 5 main nutrients (only the exact names of foods) and 5-10 exercises as bullet points for each disease listed.
No explanations, no paragraphs, no notes, no disclaimers.If there is more than 1 disease combine it together to

Format exactly as follows:

**Disease Name 1**
Exercise:
- 
- 
Food:
- 
-
-
-
-

**Disease Name 2**
Exercise:
- 
-
-
-
-
Food:
- 
-
-
-
-

Diseases and weight: {question}

Answer:
"""

prompt_nutrition = PromptTemplate(
    input_variables=["question"],
    template=template_nutrition_excercise,
)

nutrition_chain = LLMChain(llm=my_llm_model, prompt=prompt_nutrition)

# Template for daily routine
template_routine = """
You are a medical nutrition expert.

Can you help me to create the routine based on {list_of_food_and_exercise} from 5-6 am to 10-11 pm? Make a table
"""
prompt_routine = PromptTemplate(
    input_variables=["list_of_food_and_exercise"],
    template=template_routine,
)

routine_chain = LLMChain(llm=my_llm_model, prompt=prompt_routine)

# Combine both chains
chain = SimpleSequentialChain(chains=[nutrition_chain, routine_chain])

# ---- Reusable function ----
def generate_routine(diseases: list, weight: float):
    """
    Input:
        diseases: list of disease names (strings)
        weight: user's weight in kg (float)
    Output:
        str: LLM-generated routine text
    """
    # Build input string
    question_str = f"Diseases: {', '.join(diseases)}; Weight: {weight}kg"
    answer = chain.run(question_str)
    return answer