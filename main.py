import streamlit as st
from groq import Groq
import os
import base64
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv
load_dotenv()

# initialize the Groq API client
def setup_groqapi_client(api_key):
    
    GROQ_API_KEY= os.getenv("GROQ_API_KEY")
    client=Groq(api_key=GROQ_API_KEY)
    return client

# Set the page configuration
st.set_page_config(page_title="Voice Chatbot", page_icon="🎙️")

# function to transcribe audio
def transcribe_audio(client,audio_path):
    with open(audio_path, "rb") as audio_file:
        transcribe_audio= client.audio.transcriptions.create(model="whisper-large-v3-turbo", 
                                                                   file= audio_file,language="en")
        
        return transcribe_audio.text
# fuction to get response from the chatbot
def get_response(client, input_text):
    messages=[{"role": "user", "content": input_text}]
    
    response= client.chat.completions.create(model="llama3-70b-8192", messages=messages)
    return response.choices[0].message.content

# def a function for text to speech
import os
import platform
import subprocess
from elevenlabs.client import ElevenLabs

ELEVENLABS_API_KEY=os.getenv("ElevenLabs_API_KEY")
def text_to_speech(client,input_text, filepath):
    try:
        # Initialize ElevenLabs client
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        
        # Generate audio from text
        audio = client.generate(
            text=input_text,
            voice="Aria",
            output_format="mp3_22050_32",
            model="eleven_turbo_v2"
        )
        
        # Save audio to file
        with open(filepath, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        
        # Play audio based on OS
        os_name = platform.system()
        if os_name == "Darwin":  # macOS
            subprocess.run(['afplay', filepath])
        elif os_name == "Windows":  # Windows
            subprocess.run(['powershell', '-c', f'Start-Process "{filepath}" '])
        elif os_name == "Linux":  # Linux
            subprocess.run(['aplay', filepath])  # Alternatives: 'mpg123' or 'ffplay'
        else:
            raise OSError("Unsupported operating system for audio playback.")
        
        return f"Audio successfully saved to {filepath} and played back."

    except Exception as e:
        return f"An error occurred: {e}"   

# Function to create a text card with title and text
def text_card(title, text):
    st.markdown(
        f"""
        <div style="
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            background-color: #f0f2f6;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        ">
            <h3 style="color: #2c3e50; margin-bottom: 5px;">{title}</h3>
            <p style="color: #555; font-size: 16px;">{text}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )



def main():
    
    st.sidebar.title("Groq API Configuration")
    api_key=st.sidebar.text_input("Enter your Groq API key here", type="password")
    st.sidebar.write("You can get your API key by signing up at https://groq.io")
    st.title("🎙️Voice Chatbot")
    st.subheader("""Welcome to the voice chatbot. Click the record button below.
                   """)
    if api_key:
        client=setup_groqapi_client(api_key=api_key) 
        recorded_audio = audio_recorder()   
        if recorded_audio:
            audio_file="audio.mp3"
            with open(audio_file,"wb")as file:
                file.write(recorded_audio)
            
            transcribe_text=transcribe_audio(client,audio_file)
            text_card("Audio_transription",transcribe_text)
            ai_response=get_response(client,transcribe_text)
            response_audio_file="audio.mp3"
            text_to_speech(client,ai_response,response_audio_file)
            autoplay_audio(response_audio_file)
            text_card('AI_Response',ai_response)      
       
if __name__ == "__main__":
    main()