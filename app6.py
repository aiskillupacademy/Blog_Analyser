from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from langchain_groq import ChatGroq 
import streamlit as st
from langchain_core.runnables import RunnableLambda, RunnableParallel
import os
import time
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
class USP(BaseModel):
    problem: str
    solution: str
    competition: str
    industry_standard: str
    known_for: str
    usp: str

def generate_text(system_prompt:str, human_prompt, temp=0.2, model="gemini-1.5-flash", platform="google"):
    if type(human_prompt)== str:
        messages = [
            {"role": "system", "content": system_prompt },
            {"role": "human", "content": human_prompt }
    ]
        llm = ChatGroq(model="llama3-8b-8192", temperature= 0.2)
        # output = llm.with_config({"run_name": "FUNC> LLM"}).invoke(messages).content
        # return output
    elif type(human_prompt)== list:
        messages = [
            {"role": "system", "content": system_prompt }]
        messages += human_prompt
        llm =ChatGroq(model="llama3-8b-8192", temperature= 0.2)
    
    # verbose=[]
    output = llm.with_config({"run_name": "FUNC> LLM"}).invoke(messages).content
    return output


def standard_analysis(payload: dict):
    cb  = payload.get("company_brief")
    llm = ChatGroq(model="llama3-8b-8192", temperature= 0.2)
    strength = f"""
    You are an experienced business consultant. Based on the company brief provided below, generate a set of dynamic and insightful questions to identify the company's strengths. These questions should help uncover internal factors like successful processes, strong assets, customer satisfaction, competitive advantages, workforce skills, and brand perception.

    Company Brief:
    {cb}

    The questions should:
    1. Be specific to the company's context.
    2. Encourage detailed and actionable answers.
    3. Cover various aspects of the company, such as operations, team, customers, and competitive positioning.

    Examples:
    - What processes are successful?
    - What assets do you have in your team, and which is the strongest?
    - How secure is your customer base?
    - What gives you the edge over your competitors?
    - How skilled is your workforce?
    - What does your customer say about you?

    Now, generate 5 dynamic questions tailored to the company brief. Just give the questions. Never start with 'Here are your questions...'. Don't number the questions.
    """

    weak =f"""
    You are an experienced business consultant. Based on the company brief provided below, generate a set of dynamic and insightful questions to identify the company's weaknesses. These questions should help uncover internal and external factors that may hinder growth, including inefficiencies, resource gaps, and competitive disadvantages.

    Company Brief:
    {cb}

    The questions should:
    1. Be specific to the company's context.
    2. Encourage detailed and actionable responses.
    3. Cover aspects such as production, workforce skills, financial stability, customer base, and competitive position.

    Examples:
    - What hinders your production process?
    - In what areas does your competitor have an advantage over you?
    - What knowledge does your workforce lack?
    - Is the level of workforce skill lower than industry standards?
    - Do you have sufficient funding or budget for your goals?
    - Is your customer base too small for sustainable growth?
    - Is your business generating consistent profits?
    - Are you falling behind your competitors in key areas?

    Now, generate 5 dynamic and tailored questions based on the provided company brief. Just give the questions. Never start with 'Here are your questions...'. Don't number the questions.
    """
    opportunities = f"""
    You are an experienced business consultant. Based on the company brief provided below, generate a set of dynamic and insightful questions to identify opportunities for growth. These questions should help uncover external factors, trends, and potential collaborations that the company can leverage to expand its reach, customer base, and overall market presence.

    Company Brief:
    {cb}

    The questions should:
    1. Be specific to the company's context.
    2. Encourage detailed and actionable responses.
    3. Cover aspects such as market trends, partnerships, events, emerging technologies, and new customer segments.

    Examples:
    - What actions should you take now that have not been done before?
    - What are the current trends that you can leverage to your advantage?
    - How is the field changing, and how can you capitalize on these changes?
    - Which businesses could support you, and what can you offer them in return?
    - Are there upcoming events that the company can participate in to grow your customer base or presence?

    Now, generate 5 dynamic and tailored questions based on the provided company brief. Just give the questions. Never start with 'Here are your questions...'. Don't number the questions.
    """
    threats = f"""
    You are an experienced business consultant. Based on the company brief provided below, generate a set of dynamic and insightful questions to identify potential threats to the company. These questions should help uncover external risks, challenges, and uncertainties that could negatively impact the business's operations, market position, and growth.

    Company Brief:
    {cb}

    The questions should:
    1. Be specific to the company's context.
    2. Encourage detailed and actionable responses.
    3. Cover aspects such as competition, supply chain vulnerabilities, technological changes, unforeseen events, and market trends.

    Examples:
    - Who are your current and emerging competitors?
    - If you have suppliers, are they capable of supplying the materials you need at a given period and price?
    - What future technological changes could impact your business?
    - Is your business prepared for unforeseen situations such as a global pandemic, financial instability, or natural calamity?
    - What trends could pose significant threats to your business in the near future?

    Now, generate 5 dynamic and tailored questions based on the provided company brief. Just give the questions. Never start with 'Here are your questions...'. Don't number the questions.
    """


    swot_q_chain = RunnableParallel(s = RunnableLambda(lambda x: llm.invoke(strength)), w = RunnableLambda(lambda x: llm.invoke(weak)), o = RunnableLambda(lambda x: llm.invoke(opportunities)), t = RunnableLambda(lambda x: llm.invoke(threats)))
    
    swot_ques = swot_q_chain.invoke("run")
    s = swot_ques['s'].content
    w = swot_ques['w'].content
    o = swot_ques['o'].content
    t = swot_ques['t'].content

    swot_system_prompt = "You are an highly analytical associate for a marketing division. The user will provide you with a brief about their company. Using that answer the following questions DO not return anything else:\n"

    # llm = get_llm()
    swot_chain = RunnableParallel(stg = RunnableLambda(lambda x: generate_text(swot_system_prompt + s, cb)), wea = RunnableLambda(lambda x: generate_text(swot_system_prompt + w, cb)), opp = RunnableLambda(lambda x: generate_text(swot_system_prompt + o, cb)), thr = RunnableLambda(lambda x: generate_text(swot_system_prompt + t, cb)))

    swot_chain_result = swot_chain.invoke("run")
    swot_postproc_system_prompt = """
    You are an highly analytical associate for a marketing division. Given an input of a list of QA about a company, perform a SWOT analysis on only the {quality} of the company as a list. Output as a list of 10 words one-liners. Only output  5 most important points. Do not output anything else. No additional headers or footers.
    Output Format:
    - <Point 1> 
    - <Point 2>
    .
    .
    """

    # swot_postproc_system_prompt_template = PromptTemplate.from_template(swot_postproc_system_prompt)

    swot_postproc_chain = RunnableParallel(stg = RunnableLambda(lambda x: generate_text(swot_postproc_system_prompt.format(quality = "strengths"), swot_chain_result['stg'])),wea= RunnableLambda(lambda x: generate_text(swot_postproc_system_prompt.format(quality = "weaknesses"), swot_chain_result['wea'])),opp= RunnableLambda(lambda x: generate_text(swot_postproc_system_prompt.format(quality = "opportunities"), swot_chain_result['opp'])),thr= RunnableLambda(lambda x: generate_text(swot_postproc_system_prompt.format(quality = "threats"), swot_chain_result['thr'])), )

    swot_postproc_chain_output = swot_postproc_chain.invoke("run")
    print("swot done")
    time.sleep(5)
    P = """
    What are the current political stability and government policies in the market?
    How do government regulations and policies affect the industry?
    Are there any trade restrictions, tariffs, or quotas that could impact operations?
    What is the government’s stance on taxes, subsidies, and grants?
    What is the government's approach to foreign direct investment (FDI)?
    How do election cycles or political changes influence business decisions?
    What role do political parties play in shaping economic or business policies?
    Are there any international agreements or treaties affecting business operations?"""

    E = """
    What is the current economic growth rate in the region or country?
    What are the current interest rates and how do they impact business financing?
    How is the unemployment rate affecting consumer spending and labor availability?
    What is the state of the local and global economy and how does it affect the industry?
    What is the level of disposable income among consumers?
    What is the availability and cost of raw materials and resources in the market?
    """
    S ="""
    What are the current demographics and population trends in the region (age, gender, income levels)?
    How does cultural diversity or social attitudes influence consumer behavior?
    Are there shifts in societal values or attitudes toward certain products or services?
    What is the level of education and skill development in the workforce?
    How do health and wellness trends influence market demand?
    What is the level of social mobility and inequality in the region?
    """
    T = """
    Are there emerging technologies that could disrupt the market or create new opportunities for this organization?
    How does technology influence the cost and efficiency of production or operations?
    What are the technological barriers to entry in the market?
    How does research and development (R&D) impact industry growth and product evolution?
    Are there any technological infrastructure challenges (e.g., internet connectivity, energy)?
    What is the level of automation and digitization in the industry or market?
    How do new technologies influence customer expectations and satisfaction?
    How are cybersecurity risks and data protection regulations relevant to the this  business's operation?
    """
    EE = """
    What are the environmental regulations and policies impacting the industry?
    How does the business address sustainability and environmental responsibility?
    Are there any changes in climate or natural resource availability affecting the industry?
    How are waste management, recycling, and environmental conservation practices evolving?
    What is the impact of pollution or environmental degradation on business operations?
    How do consumers’ environmental concerns influence product demand and purchasing decisions?
    Are there any risks related to natural disasters that could disrupt business activities?
    What is the impact of government incentives or penalties for eco-friendly business practices?
    How does the industry manage carbon footprint, energy use, and sustainability goals?
    """
    L = """
    What are the current laws and regulations affecting the industry?
    How does intellectual property law affect product innovation and branding?
    What labor laws impact hiring, wages, and employee benefits?
    How do health and safety regulations affect operations and product design?
    Are there any antitrust laws or competition regulations that restrict or encourage business practices?
    How do consumer protection laws impact business transactions and marketing?
    What are the legal implications of data privacy and cybersecurity laws for the business?
    Are there changes in taxation laws that could affect profitability and business strategy?
    What are the legal risks related to contracts, liability, and disputes?
    """
    pestel_system_prompt = "You are an highly analytical associate for a marketing division. The user will provide you with a brief about their company. Using that information, answer the following questions in an organized manner as Question-Annser Pairs in specifically for this company if possible, not about the industry in general. if the question does not pertain to the functioning for the user's company, completely ignore the question and dont mention it in the answer. DO not return anything else:\n"

    # llm = get_llm()
    pestel_chain = RunnableParallel(pol = RunnableLambda(lambda x: generate_text(pestel_system_prompt + P, cb)), eco = RunnableLambda(lambda x: generate_text(pestel_system_prompt + E, cb)), soc = RunnableLambda(lambda x: generate_text(pestel_system_prompt + S, cb)), tec = RunnableLambda(lambda x: generate_text(pestel_system_prompt + T, cb)),env = RunnableLambda(lambda x: generate_text(pestel_system_prompt + EE, cb)), leg = RunnableLambda(lambda x: generate_text(pestel_system_prompt + L, cb)) )

    pestel_chain_result = pestel_chain.invoke("run")
    pestel_postproc_system_prompt = """
    You are an highly analytical associate for a marketing division. Given an input of a list of QA about a company, perform a PESTEL analysis on only the {quality} factors IN BRIEF that are likely to impact the company, as gathered from its size, industry and other parameters. Output as a list of small one-liners on potential factors. with an attached score on how important the factor is. Score can be low, medium and high.  Provide a maximum of 5 points. Do not output anything else. No additional headers or footers.
    Output Format:
    - <Factor 1> - <Score value>
    - <Factor 2> - <Score value>
    .
    .
    .
    """
    llm = ChatGroq(model="llama3-8b-8192", temperature= 0.2)

    # pestel_postproc_system_prompt_template = PromptTemplate.from_template(pestel_postproc_system_prompt)

    pestel_postproc_chain = RunnableParallel(pol = RunnableLambda(lambda x: generate_text(pestel_postproc_system_prompt.format(quality = "Political"), pestel_chain_result['pol'])),eco= RunnableLambda(lambda x: generate_text(pestel_postproc_system_prompt.format(quality = "Economical"), pestel_chain_result['eco'])),soc= RunnableLambda(lambda x: generate_text(pestel_postproc_system_prompt.format(quality = "Social"), pestel_chain_result['soc'])),tec= RunnableLambda(lambda x: generate_text(pestel_postproc_system_prompt.format(quality = "Technological"), pestel_chain_result['tec'])),env= RunnableLambda(lambda x: generate_text(pestel_postproc_system_prompt.format(quality = "Environmental"), pestel_chain_result['env'])),leg= RunnableLambda(lambda x: generate_text(pestel_postproc_system_prompt.format(quality = "Legal"), pestel_chain_result['leg'])) )

    pestel_postproc_chain_output = pestel_postproc_chain.invoke("run")
    print("pestel done")
    time.sleep(5)
# these can really use the search agents, well see

    t_new_entry = """
    What barriers exist that would prevent new companies from entering {Company}'s market (e.g., capital, regulations, brand loyalty)?
    How easy is it for new competitors to enter and compete with {Company}?
    Are there significant switching costs for {Company}'s customers?
    """
    t_substitution = """
    Are there alternative products or services that could replace {Company}'s offerings?
    How easily can {Company}'s customers switch to substitutes?
    Are substitutes improving in quality or becoming more competitive?
    """
    supply_p = """
    How many suppliers does {Company} rely on, and how concentrated are they?
    Can suppliers easily increase their prices, or do they have power over {Company}?
    Are there alternative suppliers or materials that {Company} could use?
    """
    buyer_p = """
    How many suppliers does {Company} rely on, and how concentrated are they?
    Can suppliers easily increase their prices, or do they have power over {Company}?
    Are there alternative suppliers or materials that {Company} could use?
    """
    comp_rival = """
    How many direct competitors does {Company} have, and how intense is the competition?
    How much differentiation exists between {Company}’s products and its competitors'?
    Is the market {Company} operates in growing, or is it saturated with competition?
    """

    pff_system_prompt = "You are an highly analytical associate for a marketing division. The user will provide you with a brief about their company. Using that answer the following questions DO not return anything else:\n"

    # llm = get_llm()
    pff_chain = RunnableParallel(t_new = RunnableLambda(lambda x: generate_text(pff_system_prompt + t_new_entry, cb)), t_sub =RunnableLambda(lambda x: generate_text(pff_system_prompt + t_substitution, cb)) , s_pow=RunnableLambda(lambda x: generate_text(pff_system_prompt + supply_p, cb)), b_pow= RunnableLambda(lambda x: generate_text(pff_system_prompt + buyer_p, cb)), comp=RunnableLambda(lambda x: generate_text(pff_system_prompt + comp_rival, cb)))

    pff_chain_result = pff_chain.invoke("run")

    pff_postproc_system_prompt = """
    You are an highly analytical associate for a marketing division. You are proficient at using Porter's Five Forces model to make good analysis. 
    Porter’s Five Forces Model is a widely recognized strategic tool that helps businesses assess the factors influencing industry profitability. This framework analyzes five key forces that shape competition within an industry, allowing companies to make informed strategic decisions for long-term sustainability. 
    - Threat of New Entrants: This force analyzes the ease with which new companies can enter an industry. Factors like high initial investment, government regulations, brand loyalty, and economies of scale can deter new entrants, making the industry more attractive. Conversely, low barriers to entry allow new competitors to easily disrupt the market, reducing profitability. 
    - Bargaining Power of Suppliers: This force assesses the influence suppliers have on the industry. Factors like the number of suppliers, availability of substitutes for their products, and switching costs for companies can affect their bargaining power. When a few powerful suppliers control essential resources, they can dictate prices and terms, squeezing profits for companies in the industry. 
    Bargaining Power of Buyers: This force analyzes the influence buyers have on the industry. Factors such as buyer concentration, buyer volume, and the availability of substitutes for the product or service affect their bargaining power. When buyers are concentrated and have a high volume of purchases, they can pressure companies to lower prices and increase their demands, impacting profitability. 
    - Threat of Substitutes: This force analyzes the existence of products or services that can replace the industry’s offerings. Factors like price, performance, and switching costs determine the threat level. The presence of close substitutes can limit pricing power and profitability for companies within the industry. 
    - Competitive Rivalry: This force analyzes the intensity of competition among existing players within the industry. Factors like market share, product differentiation, and switching costs influence the level of rivalry. High competition can lead to price wars, marketing battles, and product innovation, ultimately reducing profitability for all companies involved.
    **Instructions**
    Given an input of a list of QA about a company, perform a Porter's Five Forces analysis on the effects of {quality} on the company as a list on less that 10 words one-liners. Provide a maximum of 5 points. Do not output anything else. No additional headers or footers.
    - <Point 1> 
    - <Point 2>
    .
    .
    """
    llm = ChatGroq(model="llama3-8b-8192", temperature= 0.2)

    # pff_postproc_system_prompt_template = PromptTemplate.from_template(pff_postproc_system_prompt)

    pff_postproc_chain = RunnableParallel(t_new = RunnableLambda(lambda x: generate_text(pff_postproc_system_prompt.format(quality = "Threats of New Entry"), pff_chain_result['t_new'])), t_sub= RunnableLambda(lambda x: generate_text(pff_postproc_system_prompt.format(quality = "Threats of Substitution"), pff_chain_result['t_sub'])), s_pow=RunnableLambda(lambda x: generate_text(pff_postproc_system_prompt.format(quality = "Seller's Bargaining Power"), pff_chain_result['s_pow'])), b_pow=RunnableLambda(lambda x: generate_text(pff_postproc_system_prompt.format(quality = "Buyer's Bargaining Power"), pff_chain_result['b_pow'])), comp=RunnableLambda(lambda x: generate_text(pff_postproc_system_prompt.format(quality = "Competitors and rivals"), pff_chain_result['comp'])))

    pff_postproc_chain_output = pff_postproc_chain.invoke("run")
    print("pff done")
    return {
        "status": 200,
        "data": {
            "swot": swot_postproc_chain_output,
            "pestel": pestel_postproc_chain_output,
            "pff": pff_postproc_chain_output
        }
    }

def usp(payload: dict):
    cb  = payload.get("company_brief")
    company_type = payload.get("type")
    llm = ChatGroq(model="llama3-8b-8192", temperature= 0.2)
    
    company_details = cb[:100]
    # company_type = generate_text("Classify the company as `product` or   `service`. A product company has a product (which can be anything) approaches clients on its own. A service company specializes in something and are approached by clients to do it for them.", company_details)
    print(f"type {company_type}")
    exc_persona = f"""
    You are an executive for the company whose details are given below. You have been asked to collaborate with an rep from a company who is performing a business analysis for your company. You are currently in a conversation with them.
    Company Details
    {cb}
    Instructions:
    Your task is to answer questions proposed by the representative in a clear and simple language. If you do have any clarity on a topic which requires precise knowledge or if is the question is irrelevant , reply with a negation response. Do not make up important information based on unclear assumptions. Answer professionally and in detail.
    Answer the question in upto 100 words and nothing else. Do not return anything else. No headers or footers.
    """

    product_based_questions = [
        "What are the main features of the product listed in the company brief?",
        "Who is the product intended for, according to the company brief? Is there a specific demographic, industry, or consumer segment mentioned?",
        " What are the problems, challenges, or pain points the product is designed to address for this target audience?",
        "If applicable, Are there any specific customer desires or preferences mentioned in the brief that the product fulfills?",
        "Does the company brief mention any direct benefits or advantages the product offers its customers (e.g., saves time, improves efficiency, enhances comfort) Or are any emotional appeals or psychological benefits mentioned (e.g., status, peace of mind, self-improvement)?",
        "Does the company brief mention any third-party validation (e.g., awards, certifications, endorsements, testimonials)?",
        " Does the company brief mention any brand values (e.g., sustainability, innovation, customer service) that the product embodies?",
        "From the details in the company brief, what are the top 2-3 points that would make the product stand out to the target audience?summarized in a clear, concise, and compelling way that aligns with the company's messaging."

    ]
    service_based_questions = [
        "What are the core services offered by the company as outlined in the brief?",
        "Who is the target audience for these services? Does the brief specify any particular industries, businesses, or consumer segments?",
        "What specific problems, challenges, or pain points do the services address for the target audience?",
        "Are there any unique service features or aspects mentioned that differentiate it from competitors or alternatives?",
        "What specific customer needs or desires does the service fulfill? Are there any emotional or psychological benefits highlighted (e.g., peace of mind, increased productivity)?",
        "Does the company brief mention any successful case studies, testimonials, or customer experiences that validate the service’s value?",
        "Are there any service-level guarantees, such as performance standards, response times, or customizations, that stand out?",
        "Does the company brief emphasize any company values (e.g., reliability, innovation, customer care, flexibility) that are integral to delivering the service?",
        "From the details in the company brief, what are the top 2-3 differentiators or unique aspects of the service that would resonate with the target audience?"
    ]

    analyst_persona = """You are a business analyst hired by a company, whose detailed are mentioned below
    Client Company:
    {company_details}
    You are in a conversation with an executive from the company to get insight into the company. 
    Based on the following conversation ask 10 question,similar to those provided as suggestions to the executive pertaining to the company which will be useful in finding 'UNIQUE SELLING POINT' of the company. 
    Questions suggestions (Modify as required for the specific company)
    {questions_suggestions}.
    Return a list of 15 questions separated by newline. The questions should be informative and require a 80 words answer.
    Output Format:
    <Question 1>
    <Question 2>
    .
    .
    <Question 10>
    Never repeat a question.
    Do not return anything else. No headers or footers.

    """

    usp_system_prompt = """You are a analyst hired to conduct business analysis for a company. You will be provided a transcript of your previous conversation with an executive of the company. Your job is to perform the analysis demanded by the user based on information from the conversation.
    Conversation History:
    {conv_hist}
    """
    usp_human_prompt = """**Prompt:**
    Based on the following transcript, find out the following aspects of the company's business (in 1 line each):

    - problem: What specific pain point, challenge, or need is the company addressing for its target audience? How does this problem impact customers or businesses in the industry?
    - solution: What product or service does the company offer to resolve this problem? How does the solution specifically cater to the consumer’s needs?
    - competition: Who are the key competitors in the industry, and what are their strengths? How does the company's solution compare to these competitors in terms of features, pricing, or customer experience?
    - industry_standard: What are the typical methods, strategies, or solutions used by businesses in this space? How does the industry usually operate, and what are the standard approaches taken to solve the identified problem?
    - known_for: What key reputation or image does the company want to build within the market? What specific attribute, quality, or achievement does the company want to be recognized for?
    - usp:  summarize the company’s approach using the following format:
    **"We at [Business Name] help you [resolve the consumer’s need by/with only/without [unique benefit]."**
    Strictly return output in the following format
    Output Format Instructions:
    {instructions}"""


    analyst_persona = analyst_persona.format(company_details=company_details, questions_suggestions = "\n- ".join(product_based_questions) if 'product' in company_type else "\n- ".join(service_based_questions))

    # llm = get_llm(temperature=0.5)
    list_of_questions = llm.invoke(analyst_persona).content.strip().split('\n')
    print("questions ready")

    messages = [('system', f"{company_details}This is beginning of a conversation between the company's executive and a hired analyst."), 
                ('system', "{persona}")]


    for i in range(len(list_of_questions)):
        messages.append(('assistant', list_of_questions[i]))
        x = ChatPromptTemplate.from_messages(messages) |llm
        j = x.invoke(exc_persona)
        messages.append(('human', j.content))
    print("answers ready")
    transcript = ""
    for m in messages:
        transcript += f"{m[0]}:>\n {m[1]}\n"

    # parser = PydanticOutputParser(pydantic_object = USP)
    # usp_chain = ChatPromptTemplate([('system',usp_system_prompt), ('human',usp_human_prompt)]) | llm | parser
    # output = usp_chain.invoke({"instructions": parser.get_format_instructions, 'conv_hist': transcript})
    
    usp_chain = ChatPromptTemplate([('system',usp_system_prompt), ('human',usp_human_prompt)]) | llm
    output = usp_chain.invoke({"instructions": "Structured", 'conv_hist': transcript})
    print("usp done")
    return output, transcript






st.title("Business analysis")

company_brief = st.text_area("Enter company brief or equivalent")
option = st.selectbox(
    "Select type of company",
    ("product", "service")
)


tab1, tab2, tab3, tab4 = st.tabs(["SWOT", "PESTEL", "PFF", "USP"])
if st.button("Run"):
    output = standard_analysis({"company_brief": company_brief})
    with tab1:
        st.markdown("### SWOT ANALYSIS")
        for k in output["data"]["swot"].keys():
            st.write(f"##### {k}")
            st.write(f"{output['data']['swot'][k]}")
    with tab2:
        st.markdown("### PESTEL ANALYSIS")
        for k in output["data"]["pestel"].keys():
            st.write(f"##### {k}")
            st.write(f"{output['data']['pestel'][k]}")
    with tab3:
        st.markdown("### PFF ANALYSIS")
        for k in output["data"]["pff"].keys():
            st.write(f"##### {k}")
            st.write(f"{output['data']['pff'][k]}")
    with tab4:
        time.sleep(5)
        st.markdown("### USP ANALYSIS")
        usp_output, conv = usp({"company_brief": company_brief, "type": option})
        # with st.expander("Conversation"):
        #     st.markdown(f"```{conv}```")
        st.markdown(usp_output.content)

        
    
