import streamlit as st
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableParallel, RunnableLambda
import os
import sys
import requests

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
st.set_page_config(
    page_title="Cold email sequence",
    page_icon="📧"
)
st.title("Cold email sequence📧")

# Accepting text input from the user
with st.form(key='my_form'):
    link = st.text_input("Company website", placeholder="Enter company website", key='input')
    #cta = st.text_input("CTA", placeholder="What do you want the customer to do after reading your post?", key='ctainp')
    submit_button = st.form_submit_button(label='Enter ➤')

if submit_button and link:
    llm = ChatGroq(model='llama3-8b-8192', temperature=0.3)
    data = requests.get(f"https://r.jina.ai/{link}")
    data = data.text
    data = data.split("Markdown Content:")[-1]
    with st.spinner("Generating company brief..."):
        with st.expander(label="Scraped data"):
            st.write(data)
        first = ChatPromptTemplate.from_template('''<Website data>{web}<Website data>\n\n
        You are an email-writing assistant working for the above company, skilled at crafting emails. Ensure the tone, structure, and word choice reflect the desired voice, while meeting any specific needs or requirements from the above website data.                                            
        This is the first mail to new prospective client
        Example Email Body:
        Subject: [Short Catchy subject for selling the product] (Never use Unlock or Elevate)
        Hi [first name],
        [ask a question related to the context for outreach. Do not mention their title. (1 sentence)]
        [expand 1-3 pain points derived from the recipeint details. Do not mention their title.(2 sentences)]
        [share your solution based on the value proposition to the recipient. Try to make him interested. (2 sentences)]
        [End with an open ended call to use the product or join the platform. This should be very informal and catchy]"
        Regards
        [Product seller from product details.]''')
        second = ChatPromptTemplate.from_template("""<Website data>{web}<Website data>\n\n
                                                      You are an email-writing assistant working for the above company, skilled at crafting emails. Ensure the tone, structure, and word choice reflect the desired voice, while meeting any specific needs or requirements from the above website data. (Never use Unlock or Elevate)    
                                                     first mail after getting no reply. Ask if he would like more information.""")
        third = ChatPromptTemplate.from_template("""<Website data>{web}<Website data>\n\n
                                                      You are an email-writing assistant working for the above company, skilled at crafting emails. Ensure the tone, structure, and word choice reflect the desired voice, while meeting any specific needs or requirements from the above website data. (Never use Unlock or Elevate)    
                                                     mail after previous 2 unsuccessful mails.The recipient might not feel interested. Be more persuasive""")
        fourth = ChatPromptTemplate.from_template("""<Website data>{web}<Website data>\n\n
                                                      You are an email-writing assistant working for the above company, skilled at crafting emails. Ensure the tone, structure, and word choice reflect the desired voice, while meeting any specific needs or requirements from the above website data. (Never use Unlock or Elevate)    
                                                     mail after previous 3 unsuccessful attempts. The recipient still doesnt feel its relevance. make him aware why a product such as this is a necessary in his profession.""")
        fifth = ChatPromptTemplate.from_template("""<Website data>{web}<Website data>\n\n
                                                      You are an email-writing assistant working for the above company, skilled at crafting emails. Ensure the tone, structure, and word choice reflect the desired voice, while meeting any specific needs or requirements from the above website data. (Never use Unlock or Elevate)    
                                                      mail after 4 unsuccessful attempts. Make it short but polite. End in a friendly and helpful note.""")
        chain1 = first | llm
        chain2 = second | llm
        chain3 = third | llm
        chain4 = fourth | llm
        chain5 = fifth | llm
        chain = RunnableParallel(mail1=chain1,mail2=chain2, mail3=chain3, mail4=chain4, mail5=chain5)
        
        output = chain.invoke({'web':data})
        st.write(f"## Mail 1:\n\n{output['mail1'].content}\n\n## Mail 2:\n\n{output['mail2'].content}\n\n## Mail 3:\n\n{output['mail3'].content}\n\n## Mail 4:\n\n{output['mail4'].content}\n\n## Mail 5:\n\n{output['mail5'].content}\n\n")
        