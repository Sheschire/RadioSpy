import asyncio
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scipy.io.wavfile import write
from shazamio import Shazam
import smtplib
import sounddevice as sd
import time

########################################################################################################################
########################################################################################################################
# Songs to finds
PLAYLIST = {
    "Amir": "Complémentaires",
    "David Guetta, Alphaville": "Forever Young",
    "Gims": "Ohma tokita",
    "Sound of Legend": "Moonlight Shadow",
    "Corneille, Soolking": "Seul au monde",
}

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"  # Replace with your SMTP server (e.g., for Gmail)
SMTP_PORT = 587  # Common SMTP port
EMAIL_ADDRESS = "theo.lemesle42@gmail.com"  # Your email address
EMAIL_PASSWORD = "lszz ijkf fupp fjgs "  # Your email password (use app password if needed)

# Audio record parameters
DURATION = 5  # Recording duration in seconds
output_file = "radio_sample.wav"  # Output file name
fs = 44100  # Sample rate for recording
########################################################################################################################
########################################################################################################################

def create_audio_record():
    audio_data = sd.rec(int(DURATION * fs), samplerate=fs, channels=2)
    sd.wait()
    write(output_file, fs, audio_data)



def send_email(song):
    message = song + " is playing."
    # Create the email
    msg = MIMEText(message)
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS
    msg["Subject"] = song + " is playing."
    # Send the email
    try:
        # Connect to the SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Log in
            server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())  # Send the email
    except Exception as e:
        print("Error sending mail")



async def shazam_it():
    shazam = Shazam()
    out = await shazam.recognize(output_file)
    try:
        print(out["track"]["title"])
        return str(out["track"]["title"])
    except Exception as e:
        pass



def wait_for_50k():
    song_notified = ""
    while True:
        # artist, song = get_current_song_from_html()
        create_audio_record()
        song = asyncio.run(shazam_it())
        try:
            casefold_songs = [x.casefold() for x in list(PLAYLIST.values())]
            if song_notified != song and song.casefold() in casefold_songs:
                send_email(song)
                song_notified = song
        except AttributeError as e:
            pass
        time.sleep(60)



if __name__ == "__main__":
    # Launch Chrome
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options)
    wait = WebDriverWait(driver, 10)
    driver.get("https://www.nrj.fr/webradios")

    # Accept cookies and run radio live
    wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))).click()
    driver.find_element("xpath", "//*[@title='Écouter NRJ en direct']").click()
    time.sleep(4)

    wait_for_50k()


