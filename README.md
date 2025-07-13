# Medium Article Analyzer

Following [this](https://medium.com/data-science-collective/the-complete-guide-to-building-your-first-ai-agent-its-easier-than-you-think-c87f376c84b2) tutorial

I'm improving the above idea, which is a basic AI Powered Text Analysis Agent into a Medium Article Analyzer using LangGraph

## Key Features

- 📊 Text Classification: Automatically categorizes text into News, Blog, Research, or Other
- 🏷️ Named Entity Recognition: Extracts people, organizations, and locations from text
- 📝 Text Summarization: Generates concise one-sentence summaries
- 🔄 Workflow Orchestration: Uses LangGraph's state management for coordinated multi-step processing
- ⚡ OpenAI Integration: Powered by GPT-4o-mini for reliable text analysis

## Tech Stack

- LangGraph - Agent workflow orchestration
- LangChain - LLM framework and prompt management
- OpenAI GPT-4o-mini - Language model for text processing
- Python - Core implementation language

## Use Cases

Perfect for analyzing Medium articles, blog posts, news content, or any text that needs automated classification, entity extraction, and summarization in a single workflow

### Create the virtual environment

```bash
python -m venv agent_env
```

#### Activate the virtual environment

```bash
agent_env\Scripts\activate
```

### Install the following dependencies

- langgraph
- langchain
- langchain-openai
- python-dotenv

#### Save the dependencies in a txt

```bash
pip freeze > requirements.txt
```

## Overview of LangGraph's Agent Architecture

![LangGraph Agent Architecture](agent-architecture.png)
