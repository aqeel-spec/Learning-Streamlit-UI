from openai import OpenAI
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pdfkit
import os
import json
from openai.types.chat.chat_completion import ChatCompletionMessage, ChatCompletion
import time
from openai.types.beta import Assistant
from openai.types.beta.thread import Thread
from openai.types.beta.threads.thread_message import ThreadMessage
from openai.types.beta.threads.run import Run
from data_analyzer import DataAnalyzerBot, MessageItem

# Set up the Streamlit page with a title and icon
st.set_page_config(page_title="ChatGPT-like Chat App", page_icon=":speech_balloon:")
# Set your OpenAI Assistant ID here
assistant_id = 'asst_Enter your assistant ID here'

##################### INITIAL STATES ########################
# Initialize session state variables for file IDs and chat control
if "file_id_list" not in st.session_state:
    st.session_state.file_id_list = []

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "model" not in st.session_state:
    st.session_state.model = "gpt-3.5-turbo-1106"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "assistant_id" not in st.session_state:
    st.session_state.assistant_id = ""
if "start_quiz" not in st.session_state:
    st.session_state.start_quiz = False
if "submit_quiz" not in st.session_state:
    st.session_state.submit_quiz = False

if "bot" not in st.session_state:
    st.session_state.bot = DataAnalyzerBot(
        name="Data Analyst", 
        instructions="Act as a financial advisor by accessing detailed financial data through the Financial Modeling Prep API. Your capabilities include providing an investement advise by analyzing key metrics, comprehensive financial statements, vital financial ratios, and tracking financial growth trends.",
    ),


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



################ LOAD THE API KEYS ##################

# Create a sidebar for API key configuration and additional features
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")
if api_key:
    # Initialize the OpenAI client (to ensure that the api key is in sidebar of app)
    client = OpenAI(api_key=api_key)
    st.sidebar.success("API key set!")
else:
    st.sidebar.error("Please enter your OpenAI API key")


# Select an assistant from dropdown
assistant = st.sidebar.selectbox(
    "Select an Assistant", ("Data Analyst", "Quiz App", "Math Tutor","Function Calling","Knowledge Retrieval")
)

    

############## SIMPLE FUNCTION CALLING ####################
    
# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location:str, unit:str="fahrenheit")->str:
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": "celsius"})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": "fahrenheit"})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": "celsius"})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})



#########################################################

def get_developer_details(name:str):
    """Get developer details"""
    if name == "Aqeel Shahzad":
        return json.dumps({"name": "Aqeel Shahzad", "email": "aqeelshahzad1215@gmail.com", "github":"https://github.com/aqeel-spec"})


def run_conversation(prompt: str)-> str:
    messages = [{"role": "user", "content": prompt}]

    #####################################################################
    # set the state of role and content 
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Now write it into the chat history
    with st.chat_message("user"):
        st.markdown(prompt)
    #####################################################################
        
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_developer_details",
                "description": "Get developer details who made this, like developer name, email, and github",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "name": {"type": "string", "description": "Developer name who develop this site i.e Aqeel Shahzad"},
                        "email": {"type": "string","description": "Developer email who develop this site i.e aqeelshahzad1215@gmail.com"},
                        "github": {"type": "string","description" : "Give me developer github link"},
                    }, 
                "required": ["name"]},
            }
        }
    ]
    response: ChatCompletion = client.chat.completions.create(
        model=st.session_state["model"],
        messages=messages, 
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message: ChatCompletionMessage = response.choices[0].message
    # also show response message in chat history
    tool_calls = response_message.tool_calls

    # create spinner when response is generating
    with st.spinner('Deciding which function to call ...'):
        time.sleep(2)
    
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_current_weather": get_current_weather,
            "get_developer_details":get_developer_details
        }  # only one function in this example, but you can have multiple
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)
            with st.chat_message("assistant"):
                st.markdown(f"Function to call = {function_name} ")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": function_response,
                }
            )
        second_response: ChatCompletion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
        )
        with st.spinner('Checking weather for you again ...'):
            time.sleep(2)
        if second_response.choices[0].message.content:
            st.session_state.messages.append({"role": "assistant", "content": second_response.choices[0].message.content})
            with st.chat_message("assistant"):
                st.markdown(second_response.choices[0].message.content)
            
        return second_response.choices[0].message.content


def create_assistant(name : str, instructions: str):
    assistant: Assistant = client.beta.assistants.create(
        name=name,
        # intruction to specific field related to the assistant
        instructions=instructions,
        tools=[{"type": "code_interpreter"}],
        model=st.session_state["model"],
    )
    st.session_state.assistant_id = assistant.id

def create_thread():
    thread: Thread  = client.beta.threads.create()
    st.session_state.thread_id = thread.id

def create_message(prompt: str):
    st.session_state.messages.append({"role": "user", "content": prompt})
    message = client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=prompt,
    )

def run_assistant(instructions: str="") -> str:
    run: Run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=st.session_state.assistant_id,
        # example like instruxtion 
        # like -> Please address the user as Jane Doe. The user has a premium account.
        instructions=instructions
    )
    return run.id

def main(name: str, model_instructions: str, behaver_intstructions: str="",prompt: str=""):
    # step 1 -> Create assistant
    create_assistant(name=name, instructions=model_instructions)
    # step 2 -> Create thread
    # create_thread()
    # step 3 -> Create message
    # create_message(prompt=prompt)
    # step 4 -> Run assistant
    run_id = run_assistant(instructions=behaver_intstructions)

    # Chack the run status
    run: Run = client.beta.threads.runs.retrieve(
        thread_id=st.session_state.thread_id,
        run_id=run_id
    )
      # Poll for the run to complete and retrieve the assistant's messages
    while run.status != 'completed':
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id
        )
    
    # st.write("retrieve run",run)
    messages: list[ThreadMessage] = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    return messages




import time
from PIL import Image
from IPython.display import Image, display

def download_and_save_image(file_id: str, save_path: str) -> None:
    download_url = f"https://api.openai.com/v1/files/{file_id}/content"
    response = requests.get(
        download_url, headers={"Authorization": f"Bearer {api_key}"}
    )
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            file.write(response.content)
    else:
        st.write(f"Image downloading failed: Status Code {response.status_code}")


        
############## WEB SCRAPING ####################

# Define functions for scraping, converting text to PDF, and uploading to OpenAI
def scrape_website(url):
    """Scrape text from a website URL."""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Website error: {response.status_code}")
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()
    except Exception as e:
        st.error(f"Error scraping website: {e}")
        return None

# Function to convert text content to a PDF file
def text_to_pdf(text, filename):
    try:
        config = pdfkit.configuration(wkhtmltopdf=os.environ.get("/usr/bin/wkhtmltopdf"))
        pdfkit.from_string(text, filename, configuration=config)
        return filename
    except Exception as e:
        st.error(f"Error converting text to PDF: {e}")
        return None

############### UPLOAD FILE TO OPENAI EMBEDDING ####################
def upload_to_openai(filepath):
    """Upload a file to OpenAI and return its file ID."""
    with open(filepath, "rb") as file:
        response = client.files.create(file=file.read(), purpose="assistants")
    return response.id


# Additional features in the sidebar for web scraping and file uploading
st.sidebar.header("Additional Features")
website_url = st.sidebar.text_input("Enter a website URL to scrape and organize into a PDF", key="website_url")
# Button to scrape a website, convert to PDF, and upload to OpenAI
if st.sidebar.button("Scrape and Upload"):
    # Scrape, convert, and upload process
    scraped_text = scrape_website(website_url)
    if scraped_text:
        # Implement OpenAI upload using their API
        # https://openai.com/docs/api-reference/
        uploaded_pdf_path = text_to_pdf(scraped_text, "scraped_content.pdf")
        file_id = upload_to_openai(uploaded_pdf_path)
        with open("scraped_content.pdf", "rb") as f:
            st.download_button("Download Scraped PDF", f, file_name="scraped_content.pdf")
        # Button to download scrapped pdf
        st.success("Scraped text uploaded to OpenAI!")
    else:
        st.error("Failed to scrape website. Please try again.")

########################### FILE UPLOADER ##############################
# Sidebar option for users to upload their own files
# Concept of knowledge retrieval
uploaded_file = st.sidebar.file_uploader("Upload a file to OpenAI embeddings", key="file_uploader")

# Button to upload a user's file and store the file ID
if st.sidebar.button("Upload File"):
    # Upload file provided by user
    if uploaded_file:
        with open(f"{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        additional_file_id = upload_to_openai(f"{uploaded_file.name}")
        st.session_state.file_id_list.append(additional_file_id)
        st.sidebar.write(f"Additional File ID: {additional_file_id}")

# Display all file IDs
if st.session_state.file_id_list:
    st.sidebar.write("Uploaded File IDs:")
    for file_id in st.session_state.file_id_list:
        st.sidebar.write(file_id)
        # Associate files with the assistant
        assistant_file = client.beta.assistants.files.create(
            assistant_id=st.session_state.assistant_id, 
            file_id=file_id
        )

########################## BUTTON TO START CHAT SESSION ###################################
# Button to start the chat session
if st.sidebar.button("Start Chat"):
    # Check if files are uploaded before starting chat
    if st.session_state.file_id_list:
        st.session_state.start_chat = True
        # Create a thread once and store its ID in session state
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
        st.write("thread id: ", thread.id)
    else:
        st.sidebar.warning("Please upload at least one file to start the chat.")
    

# Define the function to process messages with citations
def process_message_with_citations(message):
    """Extract content and annotations from the message and format citations as footnotes."""
    message_content = message.content[0].text
    annotations = message_content.annotations if hasattr(message_content, 'annotations') else []
    citations = []

    # Iterate over the annotations and add footnotes
    for index, annotation in enumerate(annotations):
        # Replace the text with a footnote
        message_content.value = message_content.value.replace(annotation.text, f' [{index + 1}]')

        # Gather citations based on annotation attributes
        if (file_citation := getattr(annotation, 'file_citation', None)):
            # Retrieve the cited file details (dummy response here since we can't call OpenAI)
            cited_file = {'filename': 'cited_document.pdf'}  # This should be replaced with actual file retrieval
            citations.append(f'[{index + 1}] {file_citation.quote} from {cited_file["filename"]}')
        elif (file_path := getattr(annotation, 'file_path', None)):
            # Placeholder for file download citation
            cited_file = {'filename': 'downloaded_document.pdf'}  # This should be replaced with actual file retrieval
            citations.append(f'[{index + 1}] Click [here](#) to download {cited_file["filename"]}')  # The download link should be replaced with the actual download path

    # Add footnotes to the end of the message content
    full_response = message_content.value + '\n\n' + '\n'.join(citations)
    return full_response



# Only show the chat interface if the chat has been started
if st.session_state.start_chat:
    
    # Chat input for the user
    if assistant == "Math Tutor":
        create_assistant("Math Tutor", "Please answer the queries using the knowledge provided in the files. When adding other information mark it clearly as such with a different color.")
    elif assistant == "Knowledge Retrieval":
        assistant: Assistant = client.beta.assistants.create(
            name="Student Support Assistant",
            instructions="You are a student support chatbot. Use your knowledge base to best respond to student queries about Zia U. Khan.",
            model="gpt-3.5-turbo-1106",
            tools=[{"type": "retrieval"}],
            file_ids=[file_id for file_id in st.session_state.file_id_list],
        )
        st.session_state.assistant_id = assistant.id
        thread: Thread  = client.beta.threads.create()
        st.session_state.thread_id = thread.id
        # create_assistant("Student Support Assistant","You are a student support chatbot. Use your knowledge base to best respond to student queries about Zia U. Khan.")
    if prompt := st.chat_input("What is up?"):
        if assistant == "Function Calling":
            run_conversation(prompt=prompt)
        # Below code runs everytime for assistant apis
        elif assistant == "Data Analyst" and prompt != "":
            data_analyzer_bot : DataAnalyzerBot = st.session_state.bot()
            # send prompt message 
            data_analyzer_bot.send_message(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Now check the response status
            bot_status = data_analyzer_bot.isCompleted()
            if bot_status in ["in_progress", "queued"]:
                print(f"Run is {bot_status}. Waiting...")
                with st.status(bot_status, expanded=False) as status:
                    st.write(f"Run is {bot_status}...")
                    time.sleep(5)
                    st.write(bot_status)
                    time.sleep(3)
                    st.write(bot_status)
                    time.sleep(2)
                    status.update(label="Function called complete!", state="complete", expanded=False)
            elif bot_status == "completed":
                print(f"Run is {bot_status}.")
                response_messages = data_analyzer_bot.get_lastest_response()
                for message in response_messages.data:
                    print("*************")
                    for content in message.content:
                        role_label = "User" if message.role == "user" else "Assistant"
                        if role_label == "assistant" and content.type == "text" :
                            message_content = content.text.value
                            print(f"{role_label}: {message_content}\n")
                            st.session_state.messages.append({"role": "assistant", "content": message_content})
                        # elif content.type == "image_file":
                        #     image_file_id = content.image_file.file_id
                        #     image_save_path = f"output_images/image_{image_file_id}.png"
                        #     self.download_and_save_image(image_file_id, image_save_path)
                        #     display(Image(filename=image_save_path))
            elif bot_status == "failed":
                print("Run failed.")
                st.error("Run failed.")
            else:
                print("Unknown status.")
                st.error("Unknown status.")


        else:
            # Add user message to the state and display it
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Add the user's message to the existing thread
            client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=prompt
            )

            # Create a run with additional instructions
            run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=st.session_state.assistant_id,
                instructions="Please answer the queries using the knowledge provided in the files.When adding other information mark it clearly as such.with a different color"
            )
            
            # Poll for the run to complete and retrieve the assistant's messages
            my_bar = st.progress(0, text="Initializing...")

            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1, text="Progress: " + str(percent_complete + 1) + "%")
            time.sleep(1)
            my_bar.empty()
            

            while run.status != "completed":
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
                
                    

            # Retrieve messages added by the assistant
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )
            # Process and display assistant messages
            assistant_messages_for_run = [
                message for message in messages 
                if message.run_id == run.id and message.role == "assistant"
            ]
            for message in assistant_messages_for_run:
                full_response = process_message_with_citations(message)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                with st.chat_message("assistant"):
                    st.markdown(full_response, unsafe_allow_html=True)
else:
    # Prompt to start the chat
    st.write("Please upload files and click 'Start Chat' to begin the conversation.")


