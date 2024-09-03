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
    page_title="Content Pillars",
    page_icon="🗿"
)
st.title("Content Pillars🗿")
with st.form(key='my_form'):
    comp_url = st.text_input("Add company brief", placeholder="Enter a brief about your company", key='input')
    model = st.selectbox("Select model:", ["llama3-8b-8192", "gemini-1.5-pro", "llama3-70b-8192","gemma2-9b-it","llama-3.1-8b-instant", "llama-3.1-70b-versatile"])
    submit_button = st.form_submit_button(label='Enter ➤')
if submit_button:
    if model =="gemini-1.5-pro":
        llm = ChatGoogleGenerativeAI(model=model, temperature=0.3)
    else:
        llm = ChatGroq(model=model, temperature=0.3)
    with st.spinner("Loading content pillars: "):
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3)
        # llm = get_llm(platform='groq', model='llama3-8b-8192', temperature=0.3)
        template= """<COMPANY BRIEF>{blog}<COMPANY BRIEF>
        You are an experienced content strategist with deep expertise in crafting insightful content pillars that precisely address customer needs and drive engagement. Your objective is to enhance brand awareness and boost sales for the company. Your approach considers the company’s information, company's specific industry, emerging trends, consumer personas with their pain points and goals, keywords, as well as prevailing challenges within the industry. The focus is on the product’s unique benefits and value proposition. Avoid generic ideas; instead, generate thought-provoking, attention-grabbing content that immediately engages the target audience.
        Content Structure:

        [Content Pillar 1]: A core theme aligned with the industry context and consumer needs.
            [Sub Pillar 1]: A sub-theme that delves deeper into specific aspects of the core theme.
            [Sub Pillar 2]: Another sub-theme focusing on a different angle of the core theme.
                - [Topic Cluster 1]: Detailed topics or themes under Sub Pillar 1 that address key pain points, needs, or aspirations.\n\n
                - [Topic Cluster 2]: Additional topics or themes that cover other relevant aspects or opportunities.
        [Content Pillar 2]: Another core theme, distinct yet complementary to Pillar 1.
                [Sub Pillar 1]: A focused sub-theme related to the second core theme.
                [Sub Pillar 2]: Another sub-theme that provides a different perspective on the second core theme.
                    - [Topic Cluster 1]: Specific topics or themes under Sub Pillar 1 that target pain points, needs, or goals.\n\n
                    - [Topic Cluster 2]: Additional topics or themes to explore further opportunities or solutions.
        [Content Pillar 3]: Another core theme, distinct yet complementary to Pillar 1.
                [Sub Pillar 1]: A focused sub-theme related to the second core theme.
                [Sub Pillar 2]: Another sub-theme that provides a different perspective on the second core theme.
                    - [Topic Cluster 1]: Specific topics or themes under Sub Pillar 1 that target pain points, needs, or goals.\n\n
                    - [Topic Cluster 2]: Additional topics or themes to explore further opportunities or solutions.

        [Content Pillar 4]: Another core theme, distinct yet complementary to Pillar 1.
                [Sub Pillar 1]: A focused sub-theme related to the second core theme.
                [Sub Pillar 2]: Another sub-theme that provides a different perspective on the second core theme.
                    - [Topic Cluster 1]: Specific topics or themes under Sub Pillar 1 that target pain points, needs, or goals.\n\n
                    - [Topic Cluster 2]: Additional topics or themes to explore further opportunities or solutions.

        [Content Pillar 5]: Another core theme, distinct yet complementary to Pillar 1.
                [Sub Pillar 1]: A focused sub-theme related to the second core theme.
                [Sub Pillar 2]: Another sub-theme that provides a different perspective on the second core theme.
                    - [Topic Cluster 1]: Specific topics or themes under Sub Pillar 1 that target pain points, needs, or goals.\n\n
                    - [Topic Cluster 2]: Additional topics or themes to explore further opportunities or solutions.
        And so on...
        NEVER USE <br> tag. NEVER.
        Give output in a markdown table format. Don't give heater or footer. Just the table. Never use HTML tags like <h1>, <h2>, <br> etc. NEVER USE HTML TAGS.

        """
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm
        try:
            voice = chain.invoke({"blog": comp_url}).content
            st.write(voice)
        except Exception as e:
            st.error(e)