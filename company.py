import streamlit as st
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from langchain_groq import ChatGroq
import os
import sys
import requests

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
st.set_page_config(
    page_title="Company brief Paragraph",
    page_icon="🖋️"
)
st.title("Company brief paragraph📝")

# Accepting text input from the user
with st.form(key='my_form'):
    link = st.text_input("Company website", placeholder="Enter company website", key='input')
    default_text="""You are an expert at quickly extracting key details about a business from a large block of text and using those details to generate an in-depth, compelling business summary. 
        Extract sentences from the scraped webpage text that describe the following details about the company, elaborating on each section with supporting details and explanations.   
        Cover each and every point mentioned below. Don't leave any point blank.

        Output format:

        ### Company Overview:
            - Company Name: Name of the company
            - Industry:
            - Brief description of the business: Provide company overview along with the nitty-gritty details of the business.  Include also what makes this company unique. If there is a mission statement or purpose of the company, include this in this overview.

        Customer Personas: For each target audience, create ideal customer personas representing a certain demographics and psychographics etc. Give me a name to the persona and a short description too.
            1. Customer Persona 1
            2. Customer Persona 2
            3. Customer Persona 3
            ...
            n. Customer Persona n

        Problem Statement:

            Problem the product/service solves
                1. Problem 1
                2. Problem 2
                3. Problem 3
                ...
                n. Problem n

            Pain points for customer
                1. Pain point 1
                2. Pain point 2
                3. Pain point 3
                ...
                n. Pain point n

        Solution: Describe the product and service and how it solves the target audience’s pain points.

            How the product/service addresses the problem:
                1.
                2.
                3.
                ...
                n. Customer Persona n

            Key features and benefits
                1. Feature 1
                2. Feature 2
                3. Feature 3
                ...
                n. Feature n
                """
    system_text = st.text_area("System prompt", value=default_text, key='system_pro', height=200)
    #cta = st.text_input("CTA", placeholder="What do you want the customer to do after reading your post?", key='ctainp')
    submit_button = st.form_submit_button(label='Generate company brief ➤')

if submit_button and link:
    llm = ChatGroq(model='llama3-8b-8192', temperature=0.3)
    data = requests.get(f"https://r.jina.ai/{link}")
    data = data.text
    data = data.split("Markdown")[-1]
    with st.spinner("Generating company brief..."):
        with st.expander(label="Scraped data"):
            st.write(data)
        system_template = system_text
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

        human_template="{question}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt= ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
        
        chain = chat_prompt | llm 

        res = chain.invoke({"question": f"""Website scrap: {data}         

        From the above information, extract the brief description of the business and problems in the product."""}).content
        st.write(res)
                