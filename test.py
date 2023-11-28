import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Function to set voice by gender
def set_voice_by_gender(gender):
    for voice in voices:
        if gender.lower() == "male" and "david" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
        elif gender.lower() == "female" and "zira" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

# Example usage
set_voice_by_gender("female")
engine.say("Hello, this is a test message.")
engine.runAndWait()
