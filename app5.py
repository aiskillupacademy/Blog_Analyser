from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st
def img_prompt(query):
    sys_pr = """You are an automatic AI Image Generation prompt generator. 

    **Instructions:**
        - Determine the following
            [Main subject]: What is the key object or subject related to the idea?
            [Setting or environment]: Where is this subject located, or what is the surrounding scene?
            [Detail or material]: What is the appearance of the subject (color, material, texture)?
            [Lighting or mood]: How is the scene lit, or what kind of mood is conveyed? 
            [Visual Diversiy]Provide variations in angles, settings, or combinations of objects for visual diversity.
        - Based on this create 5 different detailed prompts which can be used to generate images. Prompts should always contain a subject, context and backgroud. Prompts should be about 100 words long.
        Return these 5 prompt templates as a list. each prompt on a new line.
        Follow the below mentioned guidelines.
    **Guidelines for generated prompts:**
        - Use Descriptive, Natural Language Prompts
        - Avoid Overloading Prompts: While detailed prompts work well, avoid excessive descriptors that may confuse the model.
        - Use Environmental or Emotional Cues: Emotions or moods, like "tranquil" or "mysterious," help direct the aesthetic. 
        - Limit Technical or Specialized Terms: The model may interpret technical jargon unpredictably, so rephrase in simpler terms unless it’s essential to the image.

          \n The final output should be of the format :\n 
    
    **Output Format**
    <Scratch Pad for taking notes>
    ---
    Prompt 1
    Prompt 2
    Prompt 3
    Prompt 4
    Prompt 5

    Do not return anything else. No headers or footers

    **User Input**
    {query}
        """
    # parser = CommaSeparatedListOutputParser()
    system_prompt = PromptTemplate(template=sys_pr, input_variables=["query"])

    llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash', temperature=0.3)

    chain = system_prompt | llm
    # print(parser.get_format_instructions())
    result = chain.invoke({"query": query})

    output = result.content.split('---')
    

    prompts = output[1].strip().split('\n')
    
    return output[0], prompts
    

st.title("Image Prompts")

input = st.text_input("Prompt:")

if st.button("Go"):
    scene_settings, prompts = img_prompt(input)
    st.markdown("### Scene Settings")
    st.markdown("```\n"+ scene_settings + "```")
    st.markdown("### Prompts")
    for p in prompts:
        st.write("> " + p)