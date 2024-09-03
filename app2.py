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
    page_title="Blog Rewriter",
    page_icon="🔄"
)
st.title("Blog Rewriter🔄")
with st.form(key='my_form'):
    comp_url = st.text_input("Add URL", placeholder="Type or add URL of blog", key='input')
    model = st.selectbox("Select model:", ["gemini-1.5-pro","llama3-70b-8192", "llama3-8b-8192"])
    ins = st.text_input("Add instructions", placeholder="Type instructions for rewriting blog", key='ins')
    submit_button = st.form_submit_button(label='Enter ➤')
if submit_button:
    if model =="gemini-1.5-pro":
        llm = ChatGoogleGenerativeAI(model=model, temperature=0.3)
    else:
        llm = ChatGroq(model=model, temperature=0.3)
    llm1 = ChatGroq(model="llama3-8b-8192", temperature=0.3)
    with st.spinner("Loading blog structure: "):
        domain = urlparse(comp_url).netloc
        data = requests.get(f"https://r.jina.ai/{comp_url}")
        data = data.text
        data = data.replace("Markdown Content:", "")
        with st.expander("Data scraped"):
            st.write(data+"\n\n")
        parser1 = PydanticOutputParser(pydantic_object=Outlines)
        prompt1 = PromptTemplate(
            template="""Blog: {blog}\n\n
                    You are an Expert Blog Analyser. Analyse the blog given above list out all the main headings with their subheadings. Return numberings wherever necessary.
                    \n{format_instructions}\n""",
            input_variables=["blog"],
            partial_variables={"format_instructions": parser1.get_format_instructions()},
            )
        chain1 = prompt1 | llm | parser1

        parser2 = PydanticOutputParser(pydantic_object=SEO)
        prompt2 = PromptTemplate(
            template="""Blog: {blog}\n\n
                    You are an Expert Blog Analyser. Analyse the blog given above, and give a list of SEO keywords used.
                    \n{format_instructions}\n""",
            input_variables=["blog"],
            partial_variables={"format_instructions": parser2.get_format_instructions()},
            )
        chain2 = prompt2 | llm | parser2

        parser3 = PydanticOutputParser(pydantic_object=URLS)
        prompt3 = PromptTemplate(
            template="""Blog: {blog}\n\n
                    You are an Expert Blog Analyser. Analyse the blog given above, and give a list of hyperlinks used to write the blog. If there are no internal linked urls, return an empty list. Only give urls, no anchor text. Just urls.
                    \n{format_instructions}\n""",
            input_variables=["blog"],
            partial_variables={"format_instructions": parser3.get_format_instructions()},
            )
        chain3 = prompt3 | llm | parser3
        run1= RunnableParallel(res1=chain1, res2=chain2, res3=chain3)
        
        try:
            outrun = run1.invoke({"blog": data})
            
            sections=[]
            for i, (key, values) in enumerate(outrun['res1'].outline.items()):
                markdown_output = ""
                if i == 0:
                    markdown_output += f"# {key}\n"
                else:
                    markdown_output += f"### {key}\n"
                markdown_output += '\n'.join([f"- {value}" for value in values])
                sections.append(markdown_output)
            markdown_output = "\n\n".join(sections)
            with st.expander("Blog structure"):
                st.write(markdown_output)
            with st.expander("SEO keywords"):
                st.write('\n- '.join([''] + outrun['res2'].seo))
            with st.expander("Links used"):
                unique_urls = list(set(outrun['res3'].urls))
                st.write('\n- '.join([''] +unique_urls))

            for url in unique_urls:
                if domain not in url:
                    filtered_urls.append(url)
            template_org = """Blog outline: {outline}\n\n
            SEO keywords: {seo}\n\n
            You are an Expert Blog Rewriter. Write a blog using the above outline optimised to above SEO keywords. Never give an introduction or conclusion. Never use =====. If there are numbers in the outline, use numbering too. Rephrase the headings.\n\n
            {ins}\n\n
            Output everything in markdown.
            """
            prompt_org = ChatPromptTemplate.from_template(template_org)
            chain_org = prompt_org | llm
            st.header("Rewritten blog:")
            filtered_urls =[]
            for sec in sections:
                st.info(sec)
                if outrun['res3'].urls==[]:
                    st.write(chain_org.invoke({"outline":sec, "seo":', '.join(outrun['res2'].seo), "ins": f"Follow these instructions: {ins}"}).content)
                else:
                    
                    st.write(chain_org.invoke({"outline":sec, "seo":', '.join(outrun['res2'].seo), "ins": f"Follow these instructions: {ins}"+"\n\n"+f"Embed the following links within the blog wherever necessary (not more than once and don't use all links) with relevant anchor text in markdown: {', '.join(filtered_urls)}"}).content)
                    st.info(filtered_urls)
        except Exception as e:
            st.error(e)
