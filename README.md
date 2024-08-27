# Blog Structure Builder 🖋️

**Blog Structure Builder** is a Streamlit application designed to analyze the structure of a blog from a provided URL. It leverages the power of the `langchain_groq` library and the `ChatGroq` model to provide insights into the organization of the blog, focusing on aspects like the use of lists, subsections, quotes, SEO keywords, and referred links.

## Features

- **Input URL**: Easily input the URL of the blog you wish to analyze.
- **Analyze Blog Structure**: The app extracts the content and provides a detailed analysis of the blog's structure.
- **Focus Areas**: The analysis includes the use of numbered/bulleted lists, subsections, quotes, SEO keywords, and referred links.

## Installation

To run this application locally, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/blog-structure-builder.git
   cd blog-structure-builder
   ```

2. **Install the required dependencies:**

   Ensure you have Python installed. Then install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment:**

   Add your GROQ API key to the `secrets` of your Streamlit app:

   ```bash
   st.secrets["GROQ_API_KEY"] = "your_groq_api_key_here"
   ```

4. **Run the app:**

   Start the Streamlit application:

   ```bash
   streamlit run app.py
   ```

## Usage

1. **Enter the Blog URL**: On the app interface, input the URL of the blog you want to analyze.
2. **Analyze**: Click on the "Enter ➤" button to start the analysis.
3. **View Results**: The app will display the blog's structure, including insights on lists, subsections, quotes, SEO keywords, and links.

## Example

After entering a blog URL, you might see results like:

```markdown
# Blog format:

- **Numbered/Bulleted Lists**: The blog effectively uses bulleted lists to break down key points.
- **Subsections**: The content is well-organized with clear subsections under each main topic.
- **Quotes**: There are quotes that enhance the credibility of the content.
- **SEO Keywords**: The blog strategically uses SEO keywords to improve search engine visibility.
- **Links Referred**: Relevant links are included to provide additional resources.
```
