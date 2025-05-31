import os
import sys
import requests
from elevenlabs import generate, play
import sounddevice as sd
import soundfile as sf
import io

def initialize_api():
    """Initialize the ElevenLabs API with the key from environment variables."""
    try:
        api_key = "sk_dda17011105e4ea85725ff39a7f4f2ebd50f7c6c2651592e"
        os.environ["ELEVEN_API_KEY"] = api_key
        print("✓ API initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing API: {e}")
        sys.exit(1)

def list_available_voices():
    """List all available voices from ElevenLabs."""
    try:
        headers = {
            "Accept": "application/json",
            "xi-api-key": os.environ["ELEVEN_API_KEY"]
        }
        response = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers)
        response.raise_for_status()
        voices_data = response.json()["voices"]
        
        print("\nAvailable voices:")
        for idx, voice in enumerate(voices_data, 1):
            print(f"{idx}. {voice['name']}")
        return voices_data
    except Exception as e:
        print(f"Error fetching voices: {e}")
        return []

def get_voice_choice(available_voices):
    """Get user's voice choice."""
    while True:
        try:
            choice = int(input("\nEnter the number of the voice you want to use: ")) - 1
            if 0 <= choice < len(available_voices):
                return available_voices[choice]
            print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def play_audio(audio_data):
    """Play the generated audio using sounddevice."""
    try:
        # Convert audio bytes to numpy array using soundfile
        with io.BytesIO(audio_data) as audio_io:
            data, samplerate = sf.read(audio_io)
            sd.play(data, samplerate)
            sd.wait()  # Wait until audio is finished playing
    except Exception as e:
        print(f"Error playing audio: {e}")

def text_to_speech(voice, text):
    """Convert text to speech using the selected voice."""
    try:
        headers = {
            "Accept": "application/json",
            "xi-api-key": os.environ["ELEVEN_API_KEY"]
        }
        audio = generate(
            text=text,
            voice=voice["voice_id"],
            model="eleven_monolingual_v1"
        )
        return audio
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None

def edit_voice_name(voice_id, new_name):
    """Edit the name of a voice."""
    try:
        headers = {
            "Accept": "application/json",
            "xi-api-key": os.environ["ELEVEN_API_KEY"]
        }
        
        response = requests.post(
            f"https://api.elevenlabs.io/v1/voices/{voice_id}/edit",
            headers=headers,
            files={
                'name': (None, new_name)
            },
        )
        response.raise_for_status()
        print(f"\n✓ Voice name updated successfully to: {new_name}")
        return True
    except Exception as e:
        print(f"Error editing voice: {e}")
        return False

def main():
    """Main function to run the voice application."""
    try:
        # Initialize the API
        initialize_api()
        
        print("Welcome to ElevenLabs Voice Generator!")
        
        while True:
            print("\nMenu:")
            print("1. Generate Speech")
            print("2. Edit Voice Name")
            print("3. Quit")
            
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == "1":
                # Get available voices
                available_voices = list_available_voices()
                if not available_voices:
                    print("No voices available. Try again...")
                    continue
                
                # Let user choose a voice
                selected_voice = get_voice_choice(available_voices)
                print(f"\nSelected voice: {selected_voice['name']}")
                
                while True:
                    # Get text input from user
                    text = input("\nEnter the text you want to convert to speech (or 'back' to return to menu): ")
                    
                    if text.lower() == 'back':
                        break
                    
                    print("\nGenerating speech...")
                    audio = text_to_speech(selected_voice, text)
                    
                    if audio:
                        print("Playing generated audio...")
                        play_audio(audio)
                        
                        # Ask if user wants to save the audio
                        save = input("\nDo you want to save this audio? (yes/no): ").lower()
                        if save == 'yes':
                            filename = input("Enter filename to save (without extension): ") + ".mp3"
                            with open(filename, 'wb') as f:
                                f.write(audio)
                            print(f"Audio saved as {filename}")
                    
                    print("\n" + "-"*50)
            
            elif choice == "2":
                # Get available voices
                available_voices = list_available_voices()
                if not available_voices:
                    print("No voices available. Try again...")
                    continue
                
                # Let user choose a voice to edit
                selected_voice = get_voice_choice(available_voices)
                print(f"\nSelected voice: {selected_voice['name']}")
                
                # Get new name
                new_name = input("\nEnter new name for the voice: ")
                if new_name:
                    edit_voice_name(selected_voice["voice_id"], new_name)
                else:
                    print("Name cannot be empty. Operation cancelled.")
            
            elif choice == "3":
                print("\nGoodbye!")
                break
            
            else:
                print("\nInvalid choice. Please try again.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return

if __name__ == "__main__":
    main()
