import os
from datetime import date
import streamlit as st
from crewai import Agent, Task, Process, Crew
from crewai.tools import tool

# Page config
st.set_page_config(
    page_title="AI Events Newsletter Generator",
    page_icon="🤖",
    layout="wide"
)

today = date.today().strftime("%A, %B %d, %Y")

@tool("OpenAI Search")
def search_tool(query: str) -> str:
    """AI-powered search using OpenAI chat completion"""
    try:
        from openai import OpenAI
        
        # Initialize OpenAI client
        api_key = st.secrets["OPENAI_API_KEY"]
        if not api_key:
            return "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
        
        client = OpenAI(api_key=api_key)
        today = date.today().strftime("%A, %B %d, %Y")
        
        # Create a focused prompt for AI events
        system_prompt = f"""
        Today's date is {today}. You are an AI events researcher helping find upcoming AI and machine learning events.
        
        IMPORTANT: The current date is {today}. When I ask for events "for the next 7 to 10 days", I mean events happening between {today} and 10 days from now.
        
        Based on your knowledge, provide information about upcoming AI and machine learning events that would typically be found on:
        - Meetup.com
        - Eventbrite.com 
        - Lu.ma (especially https://lu.ma/genai-sf?k=c)
        - Y Combinator events
        - 500 Startups
        - Andreessen Horowitz (a16z)
        - Stanford Events
        - Berkeley Events
        - LinkedIn Events
        - Silicon Valley Forum
        - Galvanize
        - StrictlyVC
        - Bay Area Tech Events
        - cerebralvalley.ai
        
        Include details like dates, locations, event types, and general information about AI/ML community events.
        Remember: Today is {today}."""
        
       
        user_prompt = f"""CURRENT DATE: {today}
        
        Query: {query}
        
        Find AI and machine learning events for the next 7-10 days starting from {today}.
        
        Search these sources and provide specific events:

        
        Please provide:
        - Specific event names and titles
        - Exact dates (starting from {today})
        - Event times
        - Locations (especially Bay Area/Silicon Valley)
        - Event descriptions
        - Registration/signup URLs
        
        Format your response as a structured list with bullet points.
        REMEMBER: Today is {today}. Only include events happening in the next 7-10 days from this date."""
        
        st.write(f"query: {query}")

        # Make API call to OpenAI
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=4096,
            temperature=0
        )
        
        result = response.choices[0].message.content
        st.write(result)
        return f"AI-powered search results for '{query}':\n\n{result}"
        
    except ImportError:
        return "OpenAI library not installed. Please install it with: pip install openai"
    except Exception as e:
        return f"OpenAI search failed for query '{query}': {str(e)}"

@tool("Load document")
def load_tool(document_type: str = "any") -> str:
    """Load a document using Streamlit file uploader and return its content as string"""
    if 'uploaded_content' in st.session_state and st.session_state.uploaded_content:
        return st.session_state.uploaded_content
    return "No file uploaded. Please upload a document to proceed."

# Define agents
@st.cache_resource
def create_agents():
    today_str = date.today().strftime("%A, %B %d, %Y")
    explorer = Agent(
        role="Senior Researcher",
        goal=f"Find and explore the most exciting events in the ai and machine learning space starting from {today_str}",
        backstory=f"""You are an Expert strategist that knows how to find events in AI, tech and machine learning. Today's date is {today_str}. Make sure to include the current date in every search query.
           Search the following sources for AI events for the next 7 to 10 days from {today_str}: Meetup.com, eventbrite.com, lu.ma (make sure to include https://lu.ma/genai-sf?k=c ), startupgrind, Y combinator, 500 startups, Andreessen Horowitz (a16z), Stanford Events, Berkeley Events, LinkedIn Events, Silicon Valley Forum, Galvanize, StrictlyVC, Bay Area Tech Events, cerebralvalley.ai,
           Please make sure to follow the link, and find out the date, the sign up URL and location""",
        verbose=True,
        allow_delegation=False,
        tools=[search_tool],
    )

    loader = Agent(
        role="Document Loader",
        goal="Read from the document and find the events",
        backstory="""Read the document and find the events""",
        verbose=True,
        allow_delegation=False,
        tools=[load_tool],
    )

    writer = Agent(
        role="Senior Technical Writer",
        goal=f"Write summary blog post about latest AI events using ordered by date for the next 7 to 10 days from {today_str}",
        backstory=f"""You are an Expert Writer on technical innovation, especially in the field of AI and machine learning. Today's date is {today_str}. You know how to write in 
        engaging, interesting but simple, straightforward and concise.""",
        verbose=True,
        allow_delegation=False,
    )

    critic = Agent(
        role="Expert Writing Critic",
        goal="Provide feedback and criticize blog post drafts. Make sure that the tone and writing style is compelling, simple and concise",
        backstory="""You are an Expert at providing feedback to the technical writers. You can tell when a blog text isn't concise,
        simple or engaging enough. You know how to provide helpful feedback that can improve any text. You know how to make sure that text 
        stays technical and insightful by using layman terms.""",
        verbose=True,
        allow_delegation=False,
    )
    
    return explorer, loader, writer, critic

def create_tasks(explorer, loader, writer, critic):
    today_str = date.today().strftime("%A, %B %d, %Y")
    task_report = Task(
        description=f"""Use and summarize scraped data from the internet to make a detailed report on the latest AI events in the next 7 to 10 days from {today_str}. 
        Use ONLY scraped data to generate the report. Today's date is {today_str}.""",
        agent=explorer,
        expected_output="A detailed analysis report with bullet points listing AI events for the next 7-10 days, including dates, locations, and signup URLs."
    )

    task_loader = Task(
        description="""Load the content of the document and find the events.""",
        agent=loader,
        expected_output="All the events in the document, with the date, description, the sign up URL and the location"
    )

    task_blog = Task(
        description="""Write a short but impactful headline, and list all the events in the order of the date.
        Here is one example event:
        
        Monday, August 25 2025
            RAG to Riches Workshop
            Time: 7:00 PM PDT
            Location: SupportVectors AI Lab 
            Description: Two-day hands-on workshop diving deep into building smart AI systems using Retrieval-Augmented Generation (RAG)
            Sign Up: https://www.meetup.com/supportvectors/events/294244000/signup
        
        For your Outputs use the following html format:
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
        expected_output="A blog article in html format with compelling headline featuring AI events ordered by date with all required details."
    )

    task_critique = Task(
        description="""Review the blog post and ensure it follows the correct format and is well-written.
        Make sure all events are properly formatted with dates, times, locations, descriptions, and signup URLs.
        Ensure the writing is engaging and accessible.""",
        agent=critic,
        expected_output="A finalized, well-formatted blog article about upcoming AI events."
    )
    
    return [task_report, task_loader, task_blog, task_critique]

def main():
    st.title("🤖 AI Events Newsletter Generator")
    st.markdown("Generate a comprehensive newsletter about upcoming AI events using web search and document upload.")
    
    # Sidebar for options
    st.sidebar.header("Options")
    include_search = st.sidebar.checkbox("Include web search for events", value=True)
    include_document = st.sidebar.checkbox("Include document upload", value=False)
    
    # Document upload section
    uploaded_content = None
    if include_document:
        st.subheader("📄 Upload Document")
        uploaded_file = st.file_uploader(
            "Choose a file containing AI events",
            type=['txt', 'md', 'csv', 'json', 'py', 'js', 'html', 'xml', 'pdf', 'docx', 'doc']
        )
        
        if uploaded_file is not None:
            try:
                # Handle different file types
                file_extension = uploaded_file.name.lower().split('.')[-1]
                
                if file_extension in ['docx', 'doc']:
                    try:
                        from docx import Document
                        # Reset file pointer
                        uploaded_file.seek(0)
                        doc = Document(uploaded_file)
                        content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                    except ImportError:
                        st.error("python-docx library not installed. Install with: pip install python-docx")
                        return
                    except Exception as e:
                        st.error(f"Error reading docx file: {str(e)}")
                        return
                elif file_extension == 'pdf':
                    try:
                        import PyPDF2
                        # Reset file pointer
                        uploaded_file.seek(0)
                        pdf_reader = PyPDF2.PdfReader(uploaded_file)
                        content = ""
                        for page in pdf_reader.pages:
                            content += page.extract_text() + "\n"
                    except ImportError:
                        st.error("PyPDF2 library not installed. Install with: pip install PyPDF2")
                        return
                    except Exception as e:
                        st.error(f"Error reading PDF file: {str(e)}")
                        return
                else:
                    # Handle text-based files
                    content = uploaded_file.read().decode('utf-8')
                
                st.success(f"Successfully loaded {uploaded_file.name}")
                uploaded_content = f"File: {uploaded_file.name}\n\nContent:\n{content}"
                st.session_state.uploaded_content = uploaded_content
                
                with st.expander("Preview uploaded content"):
                    st.text_area("Document content:", content, height=200)
            except UnicodeDecodeError:
                try:
                    content = uploaded_file.read().decode('latin-1')
                    st.success(f"Successfully loaded {uploaded_file.name}")
                    uploaded_content = f"File: {uploaded_file.name}\n\nContent:\n{content}"
                    st.session_state.uploaded_content = uploaded_content
                    
                    with st.expander("Preview uploaded content"):
                        st.text_area("Document content:", content, height=200)
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
    
    # Generate button
    if st.button("🚀 Generate AI Events Newsletter", type="primary"):
        if not include_search and not include_document:
            st.error("Please select at least one option: web search or document upload.")
            return
            
        if include_document and not uploaded_content and 'uploaded_content' not in st.session_state:
            st.error("Please upload a document first.")
            return
        
        # Create agents and tasks
        explorer, loader, writer, critic = create_agents()
        
        # Determine which tasks to include
        tasks = []
        agents = []
        
        if include_search:
            tasks.append(Task(
                description="""Use and summarize scraped data from the internet to make a detailed report on the latest AI events in the next 7 to 10 days. 
                Use ONLY scraped data to generate the report.""",
                agent=explorer,
                expected_output="A detailed analysis report with bullet points listing AI events for the next 7-10 days, including dates, locations, and signup URLs."
            ))
            agents.append(explorer)
        
        if include_document and (uploaded_content or 'uploaded_content' in st.session_state):
            tasks.append(Task(
                description="""Load the content of the document and find the events.""",
                agent=loader,
                expected_output="All the events in the document, with the date, description, the sign up URL and the location"
            ))
            agents.append(loader)
        
        # Add writing and critique tasks
        tasks.extend([
            Task(
                description="""Write a short but impactful headline, and list all the events in the order of the date.
                
                For your Outputs use the following html format:
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
                expected_output="A blog article in html format with compelling headline featuring AI events ordered by date with all required details."
            ),
            Task(
                description="""Review the blog post and ensure it follows the correct format and is well-written.
                Make sure all events are properly formatted with dates, times, locations, descriptions, and signup URLs.
                Ensure the writing is engaging and accessible.""",
                agent=critic,
                expected_output="A finalized, well-formatted blog article about upcoming AI events."
            )
        ])
        agents.extend([writer, critic])
        
        # Create and run crew
        with st.spinner("🔍 Generating your AI events newsletter..."):
            crew = Crew(
                agents=agents,
                tasks=tasks,
                verbose=True,
                process=Process.sequential,
            )
            
            # Capture output
            try:
                result = crew.kickoff()
                
                st.success("✅ Newsletter generated successfully!")
                
                # Display result
                st.subheader("📰 Generated Newsletter")
                st.text_area("Newsletter", str(result), height=200)
                
                # Download button
                st.download_button(
                    label="📥 Download Newsletter",
                    data=str(result),
                    file_name="ai_events_newsletter.html",
                    mime="text/html"
                )
                
            except Exception as e:
                st.error(f"Error generating newsletter: {str(e)}")

    # Information section
    with st.expander("ℹ️ How it works"):
        st.markdown("""
        This app uses AI agents to generate a comprehensive newsletter about upcoming AI events:
        
        1. **Web Search Agent**: Searches various sources for AI events in the next 7-10 days
        2. **Document Loader Agent**: Extracts events from uploaded documents
        3. **Writer Agent**: Combines information and formats it into a readable newsletter
        4. **Critic Agent**: Reviews and refines the final output
        
        **Sources searched include:**
        - Meetup.com, Eventbrite.com, Lu.ma
        - Y Combinator, 500 Startups, A16z events
        - Stanford/Berkeley events
        - LinkedIn Events, Silicon Valley Forum
        - And more AI community sources
        """)

if __name__ == "__main__":
    main()