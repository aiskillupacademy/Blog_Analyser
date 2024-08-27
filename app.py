import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import os
import requests
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
st.set_page_config(
    page_title="Blog structure builder",
    page_icon="🖋️"
)
st.title("Blog Structure builder")
llm = ChatGroq(model='llama3-70b-8192', temperature=0.3)
# Form to input the URL
with st.form(key='my_form'):
    comp_url = st.text_input("Add URL", placeholder="Type or add URL of blog", key='input')
    submit_button = st.form_submit_button(label='Enter ➤')
if submit_button:
    with st.spinner("Loading blog structure: "):
        data = requests.get(f"https://r.jina.ai/{comp_url}")
        data = data.text
        data = data.split("Markdown Content:")
        data = data[-1]
        template_org = """Blog: {blog}\n\n
        You are an Expert Blog Analyser. Analyse the blog given above, and talk about its organisation and following points:
        - Use of numbered/bulleted lists       
        - Subsections within main content areas
        - List of quotes used
        - Give a list of SEO keywords used
        - Links referred (show with anchor text in markdown format)
        """
        prompt_org = ChatPromptTemplate.from_template(template_org)
        chain_org = prompt_org | llm
        res_org = chain_org.invoke({"blog":data})
        st.write(f"# Blog format:\n\n{res_org.content}")