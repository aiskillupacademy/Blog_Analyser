import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import os
import requests
import re
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
st.set_page_config(
    page_title="Blog structure builder",
    page_icon="🖋️"
)
st.title("Blog Structure builder")

def average_sentence_length(text):
    # Split the text into sentences
    sentences = re.split(r'[.!?]', text)
    
    # Filter out any empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Calculate the total number of words in all sentences
    total_words = sum(len(sentence.split()) for sentence in sentences)
    
    # Calculate the average sentence length
    avg_length = total_words / len(sentences) if sentences else 0
    
    return avg_length
# Form to input the URL
with st.form(key='my_form'):
    comp_url = st.text_input("Add URL", placeholder="Type or add URL of blog", key='input')
    model = st.selectbox("Select model:", ["llama3-8b-8192", "llama3-70b-8192","gemma2-9b-it","llama-3.1-8b-instant", "llama-3.1-70b-versatile"])
    submit_button = st.form_submit_button(label='Enter ➤')
if submit_button:
    llm = ChatGroq(model=model, temperature=0.3)
    with st.spinner("Loading blog structure: "):
        data = requests.get(f"https://r.jina.ai/{comp_url}")
        data = data.text
        data = data.replace("Markdown Content:", "")
        with st.expander("Data scraped"):
            st.write(data+"\n\n")
        template_org = """Blog: {blog}\n\n
        You are an Expert Blog Analyser. Analyse the blog given above, and talk about its organisation and following points:
        - Blog title
        - Blog summary
        - Date published
        - Average sentence length (in words)
        - List of main headings (actual headings)
        - Number of main headings (an integer)
        - Number of paragraphs per main heading (an integer)
        - Use of numbered/bulleted lists       
        - Subsections within main content areas
        - List of quotes used
        - Brand voice used in blog
        - Target Audience
        - Give a list of SEO keywords used
        - Links referred (show with anchor text in markdown format)

        Output everything in markdown. Bullets will be rendered by using -.
        """
        prompt_org = ChatPromptTemplate.from_template(template_org)
        chain_org = prompt_org | llm
        template_table = """<Text>\n\n{text}\n\n<Text>\n\nRender the text between <Text> delimiters in a markdown table. No header or footer required. Only the table. Render the markdown links with proper anchor text.
        """
        prompt_table = ChatPromptTemplate.from_template(template_table)
        chain_table = prompt_table | llm
        try:
            with st.expander("Analysis"):
                res_org = chain_org.invoke({"blog":data})
                st.write(f"# Blog format:\n\n{res_org.content}")
            res_table = chain_table.invoke({"text": res_org.content})
            st.write(f"# Tabular analysis:\n\n{res_table.content}")
        except:
            st.error("Rate limit of groq exceeded. Please try after a minute")
        