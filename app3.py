import streamlit as st
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_groq import ChatGroq
from outparsers import SEO, URLS, Outlines
from langchain_core.runnables import RunnableParallel
from langchain_google_genai import ChatGoogleGenerativeAI
from urllib.parse import urlparse
import os
import requests
from langchain.output_parsers import PydanticOutputParser
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
st.set_page_config(
    page_title="Blog Schema",
    page_icon="✍️"
)
st.title("Blog Schema✍️")
with st.form(key='my_form'):
    comp_url = st.text_input("Add URL", placeholder="Type or add URL of blog", key='input')
    submit_button = st.form_submit_button(label='Enter ➤')
if submit_button:
    with st.spinner("Loading blog structure: "):
        data = requests.get(f"https://r.jina.ai/{comp_url}")
        data = data.text
        data = data.replace("Markdown Content:", "")
        with st.expander("Data scraped"):
            st.write(data+"\n\n")
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3)
        # llm = get_llm(platform='groq', model='llama3-8b-8192', temperature=0.3)
        template= """<BLOG CONTENT>{blog}<BLOG CONTENT>
        You are an expert in blog structure analysis. You will analyze the provided markdown blog content and extract a detailed schema that includes:

        1. Headings & Subheadings:
        Display the structure like:
        Title (#):
            Main heading 1(##):
                Number of paragraphs
                - Subheading 1(###)
                Number of paragraphs
                - Subheading 2(###)
                Number of paragraphs
                ...
            Main heading 2(##):
                Number of paragraphs
                - Subheading 1(###)
                Number of paragraphs
                - Subheading 2(###)
                Number of paragraphs
                ...
        
        3. Bullets & Ordered Lists:
        - Count the number of bullet points and ordered lists, along with the average number of items in each list.

        4. Quotes:
        - Identify and count any blockquotes or quoted text.

        5. Voice & Tone:
        - Analyze the voice of the blog (e.g., formal, conversational, authoritative) and describe its tone.

        6. Sentence Structure:
        - Calculate the average sentence length and identify any prevalent sentence structures or patterns.

        Provide the schema in a clear, structured format. Put the actual heading names. Never output in a table. Give the exact number of headings and subheadings as a structure.
        """
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm
        try:
            voice = chain.invoke({"blog": data}).content
            st.write(voice)
        except:
            st.error("Gemini is down. Please try again after sometime.")