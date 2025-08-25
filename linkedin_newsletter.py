import os

from langchain_community.agent_toolkits.load_tools import load_tools
from crewai import Agent, Task, Process, Crew
from crewai.tools import tool
from langchain_community.utilities import GoogleSerperAPIWrapper
import streamlit as st

#os.environ["SERPER_API_KEY"] = "serp-api-here"
search = GoogleSerperAPIWrapper(serper_api_key=st.secrets["SERPER_API_KEY"])
#api = os.environ.get("OPENAI_API_KEY")

@tool("Scrape google searches")
def search_tool(query: str) -> str:
    """Useful for when you need to ask the agent to search the internet"""
    return search.run(query)

# Loading Human Tools
human_tools = load_tools(["human"])


"""
- define agents that are going to research latest AI tools and write a blog about it 
- explorer will use access to internet to get all the latest news
- writer will write drafts 
- critique will provide feedback and make sure that the blog text is engaging and easy to understand
"""
explorer = Agent(
    role="Senior Researcher",
    goal="Find and explore the most exciting events in the ai and machine learning space",
    backstory="""You are and Expert strategist that knows how to find events in AI, tech and machine learning. 
       Searching the following sources for AI events for the next 7 to 10 days: Meetup.com, evetnbrite.com, lu.ma (make sure to include https://lu.ma/genai-sf?k=c ) , startupgrind, Y combinator, 500 startups, Andreessen Horowitz (a16z), Stanford Events, Berkeley Events , LinkedIn Events, Silicon Valley Forum,Galvanize, StrictlyVC, Bay Area Tech Events, cerebralvalley.ai,
       Please make sure to follow the link, and find out the date,  the sign up URL and location    """,
    verbose=True,
    allow_delegation=False,
    tools=[search_tool],
)

writer = Agent(
    role="Senior Technical Writer",
    goal="Write summary blog post about latest AI events using ordered by date for the next 7 to 10 days",
    backstory="""You are an Expert Writer on technical innovation, especially in the field of AI and machine learning. You know how to write in 
    engaging, interesting but simple, straightforward and concise. """,
    verbose=True,
    allow_delegation=False,
)
critic = Agent(
    role="Expert Writing Critic",
    goal="Provide feedback and criticize blog post drafts. Make sure that the tone and writing style is compelling, simple and concise",
    backstory="""You are an Expert at providing feedback to the technical writers. You can tell when a blog text isn't concise,
    simple or engaging enough. You know how to provide helpful feedback that can improve any text. You know how to make sure that text 
    stays technical and insightful by using layman terms.
    """,
    verbose=True,
    allow_delegation=False,
)

task_report = Task(
    description="""Use and summarize scraped data from the internet to make a detailed report on the latest rising projects in AI. Use ONLY 
    scraped data to generate the report. Your final answer MUST be a full analysis report, text only, ignore any code or anything that 
    isn't text. The report has to have bullet points and with 5-10 exciting new AI projects and tools. Write names of every tool and project. 
    Each bullet point MUST contain 3 sentences that refer to one specific ai company, product, model or anything you found on the internet.  
    """,
    agent=explorer,
    expected_output="A detailed analysis report with bullet points listing 5-10 exciting AI projects and tools, with each bullet containing 3 sentences about a specific AI company, product, or model."
)

task_blog = Task(
    description="""Write a short but impactful headline, and list all the events in the order of the date.
    Here is one example event:
    
    Monday, August 25
        RAG to Riches Workshop
        Time: 7:00 PM PDT
        Location: SupportVectors AI Lab 
        Description: Two-day hands-on workshop diving deep into building smart AI systems using Retrieval-Augmented Generation (RAG)
        Sign Up: https://www.meetup.com/supportvectors/events/294244000/signup
    
    For your Outputs use the following markdown format:
    ```
    ## [Day of the week], Date
    - Event Title
    - Time of the event
    - Location of the event (if available)
    - Description
    - Sign Up URL 
    ```
    """,
    agent=writer,
    expected_output="A blog article in markdown format with compelling headline and at least 10 paragraphs, featuring specific AI projects with links and formatted according to the specified template."
)

task_critique = Task(
    description="""The Output MUST have the following markdown format:
    ```
    ## [Title of post](link to project)
    - Interesting facts
    - Own thoughts on how it connects to the overall theme of the newsletter
    ## [Title of second post](link to project)
    - Interesting facts
    - Own thoughts on how it connects to the overall theme of the newsletter
    ```
    Make sure that it does and if it doesn't, rewrite it accordingly.
    """,
    agent=critic,
    expected_output="A finalized blog article that strictly follows the specified markdown format with proper project titles, links, interesting facts, and thoughts on newsletter theme connections."
)

# instantiate crew of agents
crew = Crew(
    agents=[explorer, writer, critic],
    tasks=[task_report, task_blog, task_critique],
    verbose=True,
    process=Process.sequential,  # Sequential process will have tasks executed one after the other and the outcome of the previous one is passed as extra content into this next.
)

# Get your crew to work!
result = crew.kickoff()

print("######################")
print(result)
