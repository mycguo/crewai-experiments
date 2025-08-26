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

@tool("Web Search")
def search_tool(query: str) -> str:
    """Real web search using SerpAPI or similar service"""
    try:
        return perform_deep_research(query)
        
    except Exception as e:
        return f"Search failed for query '{query}': {str(e)}"

def perform_deep_research(query: str) -> str:
    """Perform deep research using web scraping and analysis"""
    try:
        import requests
        from bs4 import BeautifulSoup
        import re
        from datetime import datetime, timedelta
        
        results = []
        today = datetime.now()
        next_week = today + timedelta(days=10)
        
        # Research multiple sources
        query_encoded = query.replace(' ', '+')
        query_dash = query.replace(' ', '-')
        
        sources = [
            # Event platforms
            f"https://www.meetup.com/find/?keywords={query_encoded}&source=EVENTS",
            f"https://www.eventbrite.com/d/ca--san-francisco/{query_dash}/",
            "https://lu.ma/genai-sf?k=c",
            f"https://lu.ma/discover?q={query_encoded}",
            
            # Startup/VC events  
            f"https://www.ycombinator.com/events?q={query_encoded}",
            f"https://500.co/events/",
            f"https://a16z.com/events/",
            
            # Universities
            f"https://events.stanford.edu/search?search={query_encoded}",
            f"https://events.berkeley.edu/search?search_api_fulltext={query_encoded}",
            
            # Professional networks
            f"https://www.linkedin.com/events/search?keywords={query_encoded}",
            f"https://www.svforum.org/events/",
            
            # Tech communities
            f"https://www.galvanize.com/events",
            f"https://strictlyvc.com/events/",
            f"https://www.meetup.com/find/?keywords=bay+area+tech+{query_encoded}",
            f"https://cerebralvalley.ai/events",
            
            # Additional Bay Area sources
            f"https://www.techcrunch.com/events/",
            f"https://www.eventbrite.com/d/ca--palo-alto/{query_dash}/",
            f"https://www.eventbrite.com/d/ca--berkeley/{query_dash}/",
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Track successful sources
        successful_sources = 0
        max_sources = 8  # Limit to avoid timeout
        
        for url in sources[:max_sources]:
            try:
                response = requests.get(url, headers=headers, timeout=8)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Identify source name
                    if "meetup.com" in url:
                        source_name = "Meetup"
                    elif "eventbrite.com" in url:
                        source_name = "Eventbrite" 
                    elif "lu.ma" in url:
                        source_name = "Lu.ma"
                    elif "ycombinator.com" in url:
                        source_name = "Y Combinator"
                    elif "500.co" in url:
                        source_name = "500 Startups"
                    elif "a16z.com" in url:
                        source_name = "Andreessen Horowitz"
                    elif "stanford.edu" in url:
                        source_name = "Stanford Events"
                    elif "berkeley.edu" in url:
                        source_name = "Berkeley Events"
                    elif "linkedin.com" in url:
                        source_name = "LinkedIn Events"
                    elif "svforum.org" in url:
                        source_name = "Silicon Valley Forum"
                    elif "galvanize.com" in url:
                        source_name = "Galvanize"
                    elif "strictlyvc.com" in url:
                        source_name = "StrictlyVC"
                    elif "cerebralvalley.ai" in url:
                        source_name = "Cerebral Valley"
                    elif "techcrunch.com" in url:
                        source_name = "TechCrunch"
                    else:
                        source_name = "Unknown Source"
                    
                    # Extract event information and signup URLs
                    links = soup.find_all('a', href=True)
                    titles = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5'])
                    
                    # Extract specific event signup URLs based on platform
                    event_urls = []
                    if "lu.ma" in url:
                        # Lu.ma specific event URL patterns
                        for link in links:
                            href = link.get('href', '')
                            if href and ('/event/' in href or href.startswith('/') and len(href) > 5):
                                if href.startswith('/'):
                                    full_url = f"https://lu.ma{href}"
                                else:
                                    full_url = href
                                if 'lu.ma' in full_url and '/event/' in full_url:
                                    event_urls.append(full_url)
                    
                    elif "meetup.com" in url:
                        # Meetup specific event URL patterns
                        for link in links:
                            href = link.get('href', '')
                            if href and '/events/' in href and 'meetup.com' in href:
                                event_urls.append(href)
                    
                    elif "eventbrite.com" in url:
                        # Eventbrite specific event URL patterns  
                        for link in links:
                            href = link.get('href', '')
                            if href and ('/e/' in href or '/events/' in href) and 'eventbrite.com' in href:
                                event_urls.append(href)
                    
                    else:
                        # Generic event URL detection
                        for link in links:
                            href = link.get('href', '')
                            if href and any(pattern in href.lower() for pattern in ['/event/', '/events/', 'register', 'signup', 'rsvp']):
                                if href.startswith('http'):
                                    event_urls.append(href)
                                elif href.startswith('/'):
                                    base_domain = url.split('/')[2]
                                    event_urls.append(f"https://{base_domain}{href}")
                    
                    # Remove duplicates and limit
                    event_urls = list(set(event_urls))[:5]
                    
                    results.append(f"\n--- {source_name} Research Results ---")
                    results.append(f"Status: ✅ Successfully scraped")
                    results.append(f"Found: {len(links)} links, {len(titles)} headings")
                    if event_urls:
                        results.append(f"🔗 Event URLs found: {len(event_urls)}")
                        for event_url in event_urls[:3]:  # Show top 3 URLs
                            results.append(f"  📅 {event_url}")
                    
                    # Look for AI/event-related content
                    ai_content = []
                    event_content = []
                    
                    for title in titles[:10]:
                        text = title.get_text().lower().strip()
                        if text and len(text) > 5:  # Filter out empty/short content
                            # AI-related keywords
                            if any(keyword in text for keyword in [
                                'ai', 'artificial intelligence', 'machine learning', 'ml', 
                                'deep learning', 'neural', 'data science', 'nlp',
                                'computer vision', 'llm', 'gpt', 'transformer'
                            ]):
                                ai_content.append(title.get_text().strip())
                            # Event-related keywords  
                            elif any(keyword in text for keyword in [
                                'event', 'meetup', 'workshop', 'conference', 'seminar',
                                'hackathon', 'demo', 'presentation', 'talk', 'webinar'
                            ]):
                                event_content.append(title.get_text().strip())
                    
                    # Combine AI content with their potential signup URLs
                    if ai_content:
                        results.append("🤖 AI-related events found:")
                        for i, content in enumerate(ai_content[:3]):
                            event_info = f"  • EVENT: {content}"
                            # Try to match with a specific signup URL
                            if i < len(event_urls):
                                event_info += f"\n    SIGNUP URL: {event_urls[i]}"
                            results.append(event_info)
                    
                    if event_content and not ai_content:
                        results.append("📅 General events found:")
                        for i, content in enumerate(event_content[:2]):
                            event_info = f"  • EVENT: {content}"
                            # Try to match with a specific signup URL
                            if i < len(event_urls):
                                event_info += f"\n    SIGNUP URL: {event_urls[i]}"
                            results.append(event_info)
                    
                    # If we found URLs but no matching content, show the URLs anyway
                    if event_urls and not ai_content and not event_content:
                        results.append("🔗 Event URLs found (no titles detected):")
                        for event_url in event_urls[:3]:
                            results.append(f"  • SIGNUP URL: {event_url}")
                    
                    if not ai_content and not event_content and not event_urls:
                        results.append("ℹ️  No specific AI/event content or URLs detected")
                    
                    successful_sources += 1
                        
            except Exception as e:
                source_name = url.split('/')[2] if '/' in url else url
                results.append(f"\n--- {source_name} ---")
                results.append(f"Status: ❌ Error - {str(e)[:50]}...")
        
        results.insert(0, f"🔍 Deep Research Summary: Scraped {successful_sources}/{max_sources} sources")
        
        # Add a clear section with all found signup URLs for easy agent access
        all_signup_urls = []
        for result in results:
            if "SIGNUP URL:" in result:
                # Extract just the URL part
                url_part = result.split("SIGNUP URL: ", 1)[1].strip()
                if url_part and url_part.startswith("http"):
                    all_signup_urls.append(url_part)
        
        if all_signup_urls:
            results.append(f"\n🔗 SUMMARY - ALL FOUND SIGNUP URLs:")
            for i, url in enumerate(all_signup_urls[:10], 1):
                results.append(f"{i}. SIGNUP_URL: {url}")
            results.append(f"\nUSE THESE SPECIFIC URLs - DO NOT CREATE GENERIC ONES!")
        
        return f"Deep research results for '{query}':\n" + "\n".join(results)
        
    except Exception as e:
        return f"Deep research failed: {str(e)}"
        
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

        # Make API call to Claude
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            temperature=0,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        result = response.content[0].text
        st.write(result)
        return f"AI-powered search results for '{query}':\n\n{result}"
        
    except ImportError:
        return "Anthropic library not installed. Please install it with: pip install anthropic"
    except Exception as e:
        return f"Claude search failed for query '{query}': {str(e)}"

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
        backstory=f"""You are an Expert Writer on technical innovation, especially in the field of AI and machine learning. Today's date is {today_str}.

IMPORTANT: When writing event listings, you MUST:
1. Use ONLY the specific "SIGNUP URL:" provided in the research results 
2. NEVER use generic URLs like https://lu.ma/ or https://meetup.com/
3. Look for lines that say "SIGNUP URL: https://..." in the research data and use those EXACT URLs
4. If no specific signup URL is provided for an event, write "Sign up URL not available" instead of creating a generic one
5. Write in engaging, interesting but simple, straightforward and concise style.""",
        verbose=True,
        allow_delegation=False,
    )

    critic = Agent(
        role="Expert Writing Critic",
        goal="Provide feedback and criticize blog post drafts. Make sure that the tone and writing style is compelling, simple and concise",
        backstory=f"""You are a writing critic who ensures event newsletters are properly formatted. Today's date is {today_str}.

CRITICAL REQUIREMENTS for event listings:
1. Use ONLY the specific "SIGNUP URL:" provided in the research data - NEVER use generic domain URLs like https://lu.ma/ or https://meetup.com/
2. Each event must include: Event title, Date, Time, Location, Description, and the EXACT signup URL from research
3. Do NOT create or guess signup URLs - only use the specific event URLs provided by the research tool
4. Format signup URLs as plain text, not HTML links
5. Remove any platform references (don't mention "Lu.ma" or "Meetup" - just the event details)

Example of CORRECT format:
## Monday, August 26, 2025
- **AI Workshop: Deep Learning Fundamentals**  
- **Time:** 7:00 PM PST
- **Location:** Downtown SF
- **Description:** Learn deep learning basics
- **Sign Up:** https://lu.ma/event/evt-abc123-ai-workshop-2025

Example of WRONG format (DO NOT DO THIS):
- **Sign Up:** https://lu.ma/ (This is generic - BAD!)
        """,
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
        description=f"""Write a short but impactful headline, and list all the events in the order of the date. Today is {today_str}.

CRITICAL: Use ONLY the specific signup URLs provided in the research data. 

INSTRUCTIONS:
1. Look for the "SUMMARY - ALL FOUND SIGNUP URLs:" section in the research results
2. Use the URLs listed as "SIGNUP_URL: https://..." 
3. If multiple events are found, distribute the signup URLs among them
4. DO NOT create generic URLs like https://lu.ma/ or https://meetup.com/

Example of CORRECT format:
## Monday, August 25, 2025
- **AI Workshop: Deep Learning Fundamentals**
- **Time:** 7:00 PM PDT  
- **Location:** SupportVectors AI Lab
- **Description:** Two-day hands-on workshop diving deep into building AI systems
- **Sign Up:** https://lu.ma/event/evt-abc123-ai-workshop-2025

WRONG format (DO NOT DO THIS):
- **Sign Up:** <a href="https://lu.ma/">Workshop</a> ❌
- **Sign Up:** https://lu.ma/ ❌
- **Sign Up:** Sign up URL not available ❌ (only use if NO URLs found in research)

Use markdown format with plain text URLs. Look for "SIGNUP_URL:" in the research results summary section.
        """,
        agent=writer,
        expected_output="A blog article in markdown format with compelling headline featuring AI events ordered by date with specific signup URLs from research data."
    )

    task_critique = Task(
        description=f"""Review the blog post and ensure it follows the correct format and is well-written. Today is {today_str}.

CRITICAL REVIEW POINTS:
1. Check that ALL signup URLs are specific event URLs (like https://lu.ma/event/evt-abc123-event-name), NOT generic domains
2. Ensure NO HTML links are used - only plain text URLs  
3. Verify each event has: Title, Date, Time, Location, Description, and specific Sign Up URL
4. Remove any generic URLs like https://lu.ma/, https://meetup.com/, https://eventbrite.com/
5. If a specific signup URL is not available, it should say "Sign up URL not available"
6. Format should be markdown, not HTML
7. Ensure the writing is engaging and accessible

REJECT any output that uses generic domain URLs or HTML link formatting.""",
        agent=critic,
        expected_output="A finalized, well-formatted markdown blog article with specific event signup URLs (no generic domains)."
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
        today_str = date.today().strftime("%A, %B %d, %Y")
        tasks.extend([
            Task(
                description=f"""Write a short but impactful headline, and list all the events in the order of the date. Today is {today_str}.

CRITICAL: Use ONLY the specific signup URLs provided in the research data. 

INSTRUCTIONS:
1. Look for the "SUMMARY - ALL FOUND SIGNUP URLs:" section in the research results
2. Use the URLs listed as "SIGNUP_URL: https://..." 
3. If multiple events are found, distribute the signup URLs among them
4. DO NOT create generic URLs like https://lu.ma/ or https://meetup.com/

Example of CORRECT format:
## Monday, August 25, 2025
- **AI Workshop: Deep Learning Fundamentals**
- **Time:** 7:00 PM PDT  
- **Location:** SupportVectors AI Lab
- **Description:** Two-day hands-on workshop diving deep into building AI systems
- **Sign Up:** https://lu.ma/event/evt-abc123-ai-workshop-2025

WRONG format (DO NOT DO THIS):
- **Sign Up:** <a href="https://lu.ma/">Workshop</a> ❌
- **Sign Up:** https://lu.ma/ ❌
- **Sign Up:** Sign up URL not available ❌ (only use if NO URLs found in research)

Use markdown format with plain text URLs. Look for "SIGNUP_URL:" in the research results summary section.
                """,
                agent=writer,
                expected_output="A blog article in markdown format with compelling headline featuring AI events ordered by date with specific signup URLs from research data."
            ),
            Task(
                description=f"""Review the blog post and ensure it follows the correct format and is well-written. Today is {today_str}.

CRITICAL REVIEW POINTS:
1. Check that ALL signup URLs are specific event URLs (like https://lu.ma/event/evt-abc123-event-name), NOT generic domains
2. Ensure NO HTML links are used - only plain text URLs  
3. Verify each event has: Title, Date, Time, Location, Description, and specific Sign Up URL
4. Remove any generic URLs like https://lu.ma/, https://meetup.com/, https://eventbrite.com/
5. If a specific signup URL is not available, it should say "Sign up URL not available"
6. Format should be markdown, not HTML
7. Ensure the writing is engaging and accessible

REJECT any output that uses generic domain URLs or HTML link formatting.""",
                agent=critic,
                expected_output="A finalized, well-formatted markdown blog article with specific event signup URLs (no generic domains)."
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