# CREWAI experiments

------ 

For my experiments with CrewAI, I decided to try 3 different projects, starting from the easiest to the most complex. The aim of the experiments was to have a team of AI agents do following work for me:
1. Examine my Startup idea
2. Build AI newsletter with Google SERP
3. Build AI newsletter with Reddit Scraper 
4. Email classifier [WIP]
5. **AI Events Newsletter Generator** (app.py) - Streamlit app with OpenAI integration

## For my experiements I've tried following LLMs:
---

### Available through API calls:

1. OpenAI -> GPT-4 
2. Gemini Pro 

### Local Models through Ollama + rating of how they performed:

1. **Mistral 7B** 
- Nice, coherent results
- Didn't understand that it should use scraping tool for the output
- Result is a bunch of generic text from training data
2. **Mistral 7B instruct** 
- Nice, coherent results, a lot of emojis
- Didn't use any scraping tool for the output
- Result is a bunch of generic text from training data.
3. **Open Chat 3.5 7B** 
- The best and most "newsletter-y" results
- But again, didn't use any tool, so generic content
4. **Nous Hermes 7B**  
- Ok results
- didn't use any tool
- generic content
5. **Open Hermes 2.5 7B** 
- The tone and style of writing is great
- but generic content
- didn't understand that it needs to use tools
6. **Starling 7B** 
- Ok results
- didn't use any tool
- generic content
7. **Llama 2 13B** 
- The only model that "understood" what the task is
- but the text wasn't coherent enough, didn's sound like a newsletter
8. **Llama 2 13B chat**  
- Didn't understand the task or produce any output
9. **Llama 2 13B text** 
- Didn't understand the task or produce any output
10. **Llama 2 7B** 
- not coherent
- didn't use any tool
- no output
11. **Llama 2 7B text** 
- No actual output
- didn't use any tool
- generic content
12. **Llama 2 7B chat** 
- Didn't use any tool
- generic content
13. **Phi-2**  
- The smallest model ran into biggest problems
- Lost track of what it's suppose to do, no output

## AI Events Newsletter Generator (app.py)

A Streamlit web application that generates AI event newsletters using CrewAI agents and OpenAI integration.

### Features:
- **Web Interface**: Clean Streamlit UI for generating AI event newsletters
- **AI-Powered Search**: Uses OpenAI GPT-4 Turbo instead of traditional web scraping
- **Document Upload**: Optional document processing for event extraction
- **Multi-Agent System**: 4 specialized CrewAI agents working together:
  - **Senior Researcher**: Finds AI events using OpenAI chat completion
  - **Document Loader**: Extracts events from uploaded documents  
  - **Technical Writer**: Creates formatted newsletter content
  - **Writing Critic**: Reviews and refines the final output

### Key Improvements:
- Replaced Google search scraping with OpenAI chat completion API
- Enhanced date awareness - explicitly passes current date to AI models
- Searches major AI event platforms: Meetup, Eventbrite, Lu.ma, Y Combinator, etc.
- Generates HTML-formatted newsletters with event details
- Focuses on Bay Area/Silicon Valley AI community events

### Usage:
1. Set `OPENAI_API_KEY` in Streamlit secrets
2. Run: `streamlit run app.py`
3. Choose web search and/or document upload options
4. Generate comprehensive AI events newsletter

### Event Sources Covered:
- Meetup.com, Eventbrite, Lu.ma (especially GenAI SF)
- Y Combinator, 500 Startups, A16z events
- Stanford/Berkeley university events  
- LinkedIn Events, Silicon Valley Forum
- Galvanize, StrictlyVC, Bay Area Tech Events
- cerebralvalley.ai