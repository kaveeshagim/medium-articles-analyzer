import os
from dotenv import load_dotenv
import requests
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from bs4 import BeautifulSoup

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

llm =  ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0)

class MediumAnalysisState(TypedDict, total=False):
    url: str  # URL of the Medium article
    text: str  # Full text of the article
    title: str  # Title of the article
    author: str  # Author of the article
    publication_date: str  # Publication date of the article
    reading_time: str
    claps: int  # Number of claps the article has received
    classification: str  # Classification of the article
    entities: List[str]  # Extracted named entities
    technologies: List[str]  # Technologies mentioned in the article
    sentiment: str  # Sentiment analysis result
    tone: str  # Tone of the article
    seo_score: float  # SEO score of the article
    structure: dict  # Structure of the article (headings, paragraphs, etc.)
    summary: str  # Summary of the article

# Classification Node
def classification_node(state: MediumAnalysisState):
    """
    Classify the text into one of predefined categories.

    Parameters:
    state(State): The current state doctionary containing the text to classify

    Returns:
    dict: A dictionary with the "classification" key containing the category result

    Categories:
    - News: Factual reporting of current events
    - Blog: Personal or informal web writing
    - Research: Academic or scientific content
    - Other Content that doesn't fit the above categories
    """

    # Define a prompt template that asks the mode to classfy the given text
    prompt = PromptTemplate(
        input_variables=["text"],
        template="""Classify this Medium article into one of the following categories:
    Technical/Programming, Data Science/AI, Business/Entrepreneurship, Personal Development, Design/UX, Marketing, Opinion/Editorial.

    Text: {text}

    Category:"""
    )


    # Format the prompt with the input text from the state
    message = HumanMessage(content=prompt.format(text=state["text"]))

    # Invoke the language model to classify the text based on the prompt
    classification = llm.invoke([message]).content.strip()

    # Return the classification result in a dictionary
    return {"classification": classification}

# Entity Extraction Node
def entity_extraction_node(state: MediumAnalysisState):
    # Function to identify and extract named entities from the text
    # Organized by category (Person, Organization, Location)

    # Create template for entity extraction prompt
    # Specifies what entities to look for and format (comma-separated)
    prompt = PromptTemplate(
        input_variables=["text"],
        template="Extract all the entities (Person, Organization, Location) from the following text. Provide the result as a comma-separated list.\n\nText: {text}\n\nEntities:"
    )

    # Format the prompt with text from state and wrap in HumanMessage
    message = HumanMessage(content=prompt.format(text=state["text"]))

    # Send to language model, get response, clean whitespace, split into list
    entities = llm.invoke([message]).content.strip().split(", ")

    # Return dictionary with entities list to be merged into agent state
    return {"entities": entities}

# Summarization Node
def summarize_node(state: MediumAnalysisState):
    # Create a template for the summarization prompt
    # This tells the model to summarize the input text in one sentence
    summarization_prompt = PromptTemplate.from_template(
        """Summarize the following text in one short sentence.
        
        Text: {text}

        Summary:"""
    )

    # Create a chain by connecting the prompt template to the language model
    # The "|" operator pipes the output of the prompt into the model
    chain = summarization_prompt | llm

    # Execute the chain with the input text from the state dictionary
    # This passes the text to be summarized to the model
    response = chain.invoke({"text": state["text"]})

    # Return a dictionary with the summary extracted from the model's response
    # This will be merged into the agent's state
    return {"summary": response.content}

# Fetch Article Node
def fetch_article_node(state: MediumAnalysisState):
    url = state["url"]
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.title.string
    paragraphs = [p.get_text() for p in soup.find_all("p")]
    text = "\n".join(paragraphs)

    # Optional: parse meta tags for author, reading time, etc.
    return {
        "text": text,
        "title": title,
        "author": soup.find("meta", {"name": "author"})["content"] if soup.find("meta", {"name": "author"}) else "Unknown"
    }

# Sentiment Analysis Node
def sentiment_tone_node(state: MediumAnalysisState):
    prompt = PromptTemplate.from_template(
        """Analyze the tone and sentiment of the following article.

Text: {text}

Respond in this format:
Sentiment: <Positive/Neutral/Negative>
Tone: <Informative/Critical/Emotional/etc.>"""
    )
    response = llm.invoke([HumanMessage(content=prompt.format(text=state["text"]))]).content
    lines = response.split("\n")
    return {
        "sentiment": lines[0].replace("Sentiment:", "").strip(),
        "tone": lines[1].replace("Tone:", "").strip(),
    }

# Structural and SEO Analysis Node
def structure_seo_node(state: MediumAnalysisState):
    prompt = PromptTemplate.from_template(
        """Analyze the article structure and SEO aspects.

Text: {text}

Return:
- Heading Count
- Has Clear Introduction and Conclusion (Yes/No)
- Title SEO Score (0 to 100)
- Formatting Quality (Good/Poor)
"""
    )
    response = llm.invoke([HumanMessage(content=prompt.format(text=state["text"]))]).content
    return {"structure": response}

# Engagement Score Node
def engagement_score_node(state: MediumAnalysisState):
    prompt = PromptTemplate.from_template(
        """Evaluate the following article's quality and engagement potential on Medium.

Title: {title}
Text: {text}

Respond with:
- Clarity Score (0-10)
- Engagement Prediction (High/Medium/Low)
- Readability: <Easy/Medium/Hard>
"""
    )
    response = llm.invoke([HumanMessage(content=prompt.format(text=state["text"], title=state["title"]))]).content
    return {"engagement_analysis": response}


# Defining the coordianted workflow
workflow = StateGraph(MediumAnalysisState)

# Add nodes to the graph
workflow.add_node("fetch_article_node", fetch_article_node)
workflow.add_node("classification_node", classification_node)
workflow.add_node("entity_extraction", entity_extraction_node)
workflow.add_node("summarization", summarize_node)
workflow.add_node("sentiment_tone_node", sentiment_tone_node)
workflow.add_node("structure_seo_node", structure_seo_node)
workflow.add_node("engagement_score_node", engagement_score_node)

# Add edges to the graph
workflow.set_entry_point("fetch_article_node") # Set the entry point of the graph
workflow.add_edge("fetch_article_node", "classification_node") # Connect fetch article to classification
workflow.add_edge("classification_node", "entity_extraction") # Connect classification to entity extraction
workflow.add_edge("entity_extraction", "summarization") # Connect entity extraction to summarization
workflow.add_edge("summarization", "sentiment_tone_node") # Connect summarization to sentiment and tone analysis
workflow.add_edge("sentiment_tone_node", "structure_seo_node") # Connect sentiment tone to structure and SEO analysis
workflow.add_edge("structure_seo_node", "engagement_score_node") # Connect structure seo to engagement score analysis
workflow.add_edge("engagement_score_node", END) # Connect engagement score analysis to the end of the graph

# Compile the graph
app = workflow.compile()

if __name__ == "__main__":
    result = app.invoke({
        "url": "https://medium.com/@ryanblakes/10-full-stack-project-ideas-will-actually-get-you-hired-a62294823512"  # Replace with a real Medium article
    })

    print("\n--- Medium Article Analysis Result ---")
    print("Title:", result.get("title"))
    print("Author:", result.get("author"))
    print("Classification:", result.get("classification"))
    print("Entities:", result.get("entities"))
    print("Summary:", result.get("summary"))
    print("Sentiment:", result.get("sentiment"))
    print("Tone:", result.get("tone"))
    print("Structure/SEO:", result.get("structure"))
    print("Engagement Score:", result.get("engagement_analysis"))
