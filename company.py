import streamlit as st
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from langchain_groq import ChatGroq
import os
import sys
import requests

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
st.set_page_config(
    page_title="Company brief Paragraph",
    page_icon="🖋️"
)
st.title("Company brief paragraph📝")

# Accepting text input from the user
with st.form(key='my_form'):
    link = st.text_input("Company website", placeholder="Enter company website", key='input')
    texts = st.text_input("Text", placeholder="Enter text", key='inputtext')
    default_text="""You are given web-scraped data containing information about a company. From this data, extract and summarize key details to create a complete company brief. The brief should include the following sections:

                Company Name: Identify and highlight the name of the company.
                Industry: Specify the industry or sector the company operates in.
                Mission Statement: Summarize the company’s mission or core values.
                Key Products/Services: Outline the main products or services offered by the company.
                Target Audience: Describe the company’s primary customer base or target market.
                Pricing plans: Give detailed price plan if present.
                Unique Selling Proposition (USP): Highlight what differentiates the company from competitors. Give detailed bullet points.
                Company Milestones: Include any notable achievements or major milestones.
                Leadership Team: List key leadership figures with their roles.
                Recent News: Summarize any recent news or developments about the company.
                SEO Keywords: Identify relevant SEO keywords related to the company.
                Ensure that each section is concise yet informative, and the overall tone is professional.
                """
    system_text = st.text_area("System prompt", value=default_text, key='system_pro', height=200)
    #cta = st.text_input("CTA", placeholder="What do you want the customer to do after reading your post?", key='ctainp')
    submit_button = st.form_submit_button(label='Generate company brief ➤')

if (submit_button and link) or (submit_button and texts):
    llm = ChatGroq(model='llama-3.1-70b-versatile', temperature=0.3)
    if link!="":
        data = requests.get(f"https://r.jina.ai/{link}")
        data = data.text
        data = data.split("Markdown")[-1]
    else:
        data=texts
    with st.spinner("Generating company brief..."):
        if link!="":
            with st.expander(label="Scraped data"):
                st.write(data)
        system_template = system_text
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

        human_template="{question}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt= ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
        
        chain = chat_prompt | llm 

        res = chain.invoke({"question": f"""Website scrap: {data}         

        From the above information, extract the detailed description of the business"""}).content
        st.write(res)
                