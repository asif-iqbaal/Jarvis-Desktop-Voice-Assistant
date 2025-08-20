import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser as wb
import os
import random
import pyautogui
import pyjokes
import psutil
import urllib.parse
import google.generativeai as genai
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GENAI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

stop_speaking = False
active = True   
TODO_TASK = "data.txt"
PREVIOUD_TASK = "previous_task.txt"

# Register Brave browser
brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
wb.register('brave', None, wb.BackgroundBrowser(brave_path))

def speak(audio) -> None:
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1)
        engine.say(audio)
        engine.runAndWait()
    except Exception as e:
        print(f"Speech error: {e}")

def chat_with_gemini(query: str) -> str:
    """Generates a response from the Gemini AI model."""

    if "jarvis" not in query.lower():
        return ""
    
    try:
        response = gemini_model.generate_content(query + " in the short and concise way.")
        if response and response.text:
            with open(PREVIOUD_TASK, "a", encoding="utf-8") as f:
                f.write(f"User: {query}\n")
                f.write(f"Gemini: {response.text}\n")
            print("jarvis:", response.text)  
            speak(response.text)  
            
            return response.text
        else:
            speak("Sorry, I didn&pos;t get any response.")
            return ""
    except Exception as e:
        speak("Sorry, Gemini is unavailable right now.")
        print("Gemini error:", e)
        return ""
    
def time() -> None:
    """Tells the current time."""
    current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
    speak("The current time is")
    speak(current_time)
    print("The current time is", current_time)

def date() -> None:
    """Tells the current date."""
    now = datetime.datetime.now()
    speak("The current date is")
    speak(f"{now.day} {now.strftime('%B')} {now.year}")
    print(f"The current date is {now.day}/{now.month}/{now.year}")

def wishme() -> None:
    """Greets the user based on the time of day."""
    

    hour = datetime.datetime.now().hour
    if 4 <= hour < 12:
        speak("Good morning!")
       
    elif 12 <= hour < 16:
        speak("Good afternoon!")
        
    elif 16 <= hour < 24:
        speak("Good evening!")
        
    else:
        speak("Good night, see you tomorrow.")

    speak("Welcome back sir!")
    assistant_name = load_name()
    speak(f"{assistant_name} at your service. Please tell me how may I assist you.")

def screenshot() -> None:
    """Takes a screenshot and saves it."""
    img = pyautogui.screenshot()
    img_path = os.path.expanduser("~\\Pictures\\screenshot.png")
    img.save(img_path)
    speak(f"Screenshot saved as {img_path}.")
    print(f"Screenshot saved as {img_path}.")

def takecommand() -> str:
    """Takes microphone input from the user and returns it as text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        try:
            audio = r.listen(source, timeout=5)  # wait for speech
        except sr.WaitTimeoutError:
           if active: 
            speak("Sorry sir, I didn't hear anything.")
            return None

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language="en-in")
        print("You said:", query)
        return query.lower() 
    except sr.UnknownValueError:
        if active:
            speak("problem in understanding, please repeat.")
        return None
    except sr.RequestError:
        speak("Speech recognition service is unavailable.")
        return None
    except Exception as e:
       if active: 
        speak(f"An error occurred: {e}")
        print(f"Error: {e}")
        return None

def play_music(song_name=None) -> None:
    """Plays music from the user's Music directory."""
    song_dir = os.path.expanduser("~\\Music")
    songs = os.listdir(song_dir)

    if song_name:
        songs = [song for song in songs if song_name.lower() in song.lower()]

    if songs:
        song = random.choice(songs)
        os.startfile(os.path.join(song_dir, song))
        speak(f"Playing {song}.")
        print(f"Playing {song}.")
    else:
        speak("No song found.")
        print("No song found.")

def set_name() -> None:
    """Sets a new name for the assistant."""
    speak("What would you like to name me?")
    name = takecommand()
    if name:
        with open("assistant_name.txt", "w") as file:
            file.write(name)
        speak(f"Alright, I will be called {name} from now on.")
    else:
        speak("Sorry")

def load_name() -> str:
    """Loads the assistant's name from a file, or uses a default name."""
    try:
        with open("assistant_name.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "Jarvis"  # Default name

def check_system():
    # Collect system info
    cpu_usage = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    battery = psutil.sensors_battery()
    

    # Build a status message
    status = (
        f"CPU is at {cpu_usage} percent. "
        f"RAM usage is {ram.percent} percent, "
        f"Battery is at {battery.percent if battery else 'unknown'} percent."
    )
    return status

def search_wikipedia(query):
    """Searches Wikipedia and returns a summary."""
    try:
        speak("Searching Wikipedia...")
        result = wikipedia.summary(query, sentences=2)
        speak(result)
        print(result)
    except wikipedia.exceptions.DisambiguationError:
        speak("Multiple results found. Please be more specific.")
    except Exception:
        speak("I couldn't find anything on Wikipedia.")

def add_task(plan: str):
    """Adds a task to the todo list."""
    with open(TODO_TASK, "a", encoding="utf-8") as f:
        f.write(plan + "\n")
        print(f"Added: {plan}")

def get_todos():
    if not os.path.exists(TODO_TASK):
        return []
    with open(TODO_TASK, "r", encoding="utf-8") as f:
        todos = f.readlines()
    return [t.strip() for t in todos if t.strip()]
        
def delete_task():
    """Deletes a task from the todo list."""
    if os.path.exists(TODO_TASK):
        os.remove(TODO_TASK)
        speak("All tasks have been deleted.")

if __name__ == "__main__":
    wishme()

    while True:
        if active:
            query = takecommand()
            if not query:
                continue

            if "time" in query:
                time()

            elif "mute" in query:
                print("Muting Jarvis.",active)
                active = False
                speak("Okay, I am muted. Say wake up to activate me again.")
                
            elif "who are you" in query:
                assistant_name = load_name()
                speak(f"I am {assistant_name}, your desktop voice assistant.")
                print(f"I am {assistant_name}, your desktop voice assistant.")

            elif "date" in query:
                date()

            elif "wikipedia" in query:
                query = query.replace("wikipedia", "").strip()
                search_wikipedia(query)

            elif "play music" in query:
                song_name = query.replace("play music", "").strip()
                play_music(song_name)

            elif "change song" in query:
                speak("Changing the song.")
                song_name = query.replace("change song", "").strip()
                play_music(song_name)

            elif "close music" in query:
                speak("Ok sir Closing music player.")
                os.system("taskkill /im Microsoft.Media.Player.exe  /f")

            elif "tasks" in query or "talk" in query or "tas" in query :
                speak("Here are the tasks open:")
                os.system("tasklist")

            elif "open vs code" in query:
                speak("Opening Visual Studio Code.")
                os.startfile(r"C:\Users\Lenovo\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Visual Studio Code\Visual Studio Code.lnk")
            
            elif "open terminal" in query:
                speak("Opening terminal.")
                os.startfile(r"C:\Users\Lenovo\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Windows PowerShell\Windows PowerShell.lnk")

            elif "close terminal" in query:
                speak("Closing terminal.")
                os.system("taskkill /f /im powershell.exe")

            elif "close vs code" in query:
                speak("Closing Visual Studio Code.")
                os.system("taskkill /f /im Code.exe")

            elif "open youtube" in query:
                speak("What would you like to search on YouTube?")
                search_query = takecommand()
                if search_query:
                    speak(f"Searching {search_query} on YouTube.")
                    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(search_query)}"    
                    wb.get('brave').open(url)
                else:
                    wb.get('brave').open("https://youtube.com")

            elif "close youtube" in query:
                speak("Closing YouTube.")
                os.system("taskkill /f /im brave.exe")

            elif "open google" in query:
                wb.get('brave').open("https://google.com")
            
            elif "open chrome" in query or "open browser " in query:
                speak("Opening Chrome Browser.")
                os.startfile(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Chrome.lnk")

            elif "close chrome" in query:
                speak("Closing Chrome Browser.")
                os.system("taskkill /f /im chrome.exe")
            
            elif "change your name" in query:
                set_name()

            elif "check system" in query:
                speak("Checking system status, please wait.")
                system_status = check_system()
                speak("Here is your system status. " + system_status)

            elif "screenshot" in query:
                screenshot()
                speak("I've taken a screenshot, please check it.")

            elif "tell me a joke" in query:
                joke = pyjokes.get_joke()
                speak(joke)
                print(joke)

            elif "open camera" in query:
                speak("Opening camera.")
                os.system("start microsoft.windows.camera:")

            elif "took a picture" in query:
                speak("Taking a picture.")
                pyautogui.screenshot("camera_picture.png")
                speak("Picture taken and saved as camera_picture.png.")

            elif "close camera" in query:
                speak("Closing camera.")
                os.system("taskkill /f /im Camera.exe")

            elif "add plan" in query or "ad plan" in query:
                speak("What task would you like to add?")
                task = takecommand() 
                speak(f"Adding task: {task}")
                add_task(task)
                speak("Task added successfully.")

            elif "show plan" in query:
                speak("Here are your tasks:")
                todos = get_todos()
                if todos:
                        speak("Here are your todo plans.")
                        for idx, t in enumerate(todos, 1):
                            speak(f"{idx}. {t}")
                else:
                        speak("You have no todo plans.")

            elif "delete plan" in query:
                speak("Deleting all tasks.")
                delete_task()

            # elif "open microsoft office" in query:
            #     speak("Opening Microsoft Office.")
            #     os.startfile(r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE")

            elif "shutdown" in query:
                speak("Shutting down the system, goodbye!")
                os.system("shutdown /s /f /t 1")
                break

            elif "restart" in query:
                speak("Restarting the system, please wait!")
                os.system("shutdown /r /f /t 1")
                break

            elif "offline" in query or "exit" in query:
                speak("Going offline. Have a good day!")
                break
            
            else:
                # unknown command chat mode 
                chat_with_gemini(query)
        else:
            query = takecommand()
            if query and "wake up" in query:
                speak("I am back online.")
                active = True
