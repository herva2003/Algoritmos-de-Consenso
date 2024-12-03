import datetime

def log_message(message):
    with open("logs/log.txt", "a") as log_file:
        log_file.write(f"{datetime.datetime.now()} - {message}\n")