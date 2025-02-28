from flask import request, session
from flask_session import Session
from customtkinter import *
import mysql.connector
from tkinter import ttk, messagebox
import json
from werkzeug.security import generate_password_hash, check_password_hash
import random
from pathlib import Path
from dhooks import Webhook, Embed
from CTkXYFrame import *
from PIL import Image
import gdown


#Declaring Frontend GUI
frontend = CTk()
frontend.geometry("1000x563")
frontend.title("HexTrans Drivershub")
frontend.resizable(1, 0)
frontend.grid_columnconfigure(0, weight=1)
frontend.grid_rowconfigure(0, weight=1)
frontend.update_idletasks()


#DB Connection
with open("config.json", "r") as cfg_file:
    cfg = json.load(cfg_file)

conn = mysql.connector.connect(
        host = cfg["MYSQL_HOST"],
        port = 3306,
        user = cfg["MYSQL_USER"],
        password = cfg["MYSQL_PASSWORD"],
        database = cfg["MYSQL_DATABASE"]
        )

cursor = conn.cursor()

steam_id = ""

hook = Webhook(cfg["WEBHOOK_URL"])

def save_session(email, username, steam_id):
    session_data = {
        "email": email,
        "username": username,
        "steam_id": steam_id,
        "logged_in": True,
        "theme": "dark"
    }
    
    session_file = Path("session.json")
    with open(session_file, "w") as f:
        json.dump(session_data, f)

def load_session():
    session_file = Path("session.json")
    if session_file.exists():
        try:
            with open(session_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading session: {e}")
    return None

def clear_session():
    session_file = Path("session.json")
    if session_file.exists():
        os.remove(session_file)

def check_existing_session():
    session_data = load_session()
    if session_data and session_data.get("logged_in"):
        global steam_id
        steam_id = session_data.get("steam_id", "")
        username = session_data.get("username", "")
        messagebox.showinfo("Session Restored", f"Welcome back, {username}!")
        tabview.set("Jobs")
        return True
    return False

tabview = CTkTabview(frontend)
tabview.pack(pady=5, padx=5, fill=BOTH, expand=True)
registerTab = tabview.add("Register")
loginTab = tabview.add("Login")
loggerTab = tabview.add("Logger")
jobsTab = tabview.add("Jobs")
profileTab = tabview.add("Profile")
#modsTab = tabview.add("Mods")


def logout():
    global steam_id
    steam_id = ""
    clear_session()
    messagebox.showinfo("Logged Out", "You have been logged out successfully.")
    tabview.set("Login")

#Login logic
def login():
    email = loginEmailEntry.get()
    password = loginPasswordEntry.get()
    
    try:
        cursor.execute("SELECT password, username FROM users WHERE email = %s", (email,))
        logging_user = cursor.fetchone()
        
        if logging_user is None:
            messagebox.showerror("Error", f"User with email {email} does not exist! Please register")
            tabview.set("Register")
        else:
            hashed_password = logging_user[0]
            username = logging_user[1]
            if check_password_hash(hashed_password, password):
                global steam_id
                cursor.execute("SELECT steam_id FROM users WHERE email = %s", (email,))
                steam_id_result = cursor.fetchone()
                if steam_id_result:
                    steam_id = steam_id_result[0]
                    # Save session data
                    save_session(email, username, steam_id)
                    messagebox.showinfo("Success", f"Welcome back, {username}!")
                    tabview.set("Jobs")
                    tabview.delete("Login")
                    tabview.delete("Register")
                else:
                    messagebox.showerror("Error", "Steam ID not found for this user.")
            else:
                messagebox.showerror("Error", "Incorrect password.")
    except Exception as e:
        print(f"Login error: {e}")
        messagebox.showerror("Error", "Login failed. Please try again.")

#Register logic 
def register():
    register_mail = registerMail.get()
    register_username = registerUsername.get()
    register_password = registerPassword.get()
    register_confirm_password = registerConfirmPassword.get()
    username = register_username
    email = register_mail

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    if username in users:
        messagebox.showerror("Error", f"User {username} already exists!")
    else:
        if register_password == register_confirm_password:
            hashed_password = generate_password_hash(register_password, method="pbkdf2:sha256")
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
            conn.commit()
            messagebox.showinfo("Success", f"Welcome {username}! You should now be able to log in using your credentials!")
            tabview.set("Login")
        else:
            messagebox.showerror("Error", "Passwords don't match, please try again!")
  



#Font Variables:
h1 = ("Arial Bold", 36)
h2 = ("Arial Bold", 24)
font_entry = ("Arial", 20)
font_job = ("Arial", 18)

#Register GUI
registerTabFrame = CTkFrame(registerTab)
registerTabFrame.pack(pady=5, padx=5, fill=BOTH, expand=True)

registerTabForm = CTkFrame(registerTabFrame)
registerTabForm.place(relx=0.5, rely=0.5, anchor=CENTER)

registerUsername = CTkEntry(registerTabForm, placeholder_text="Username", font=font_entry)
registerUsername.grid(row=0, column=0, pady=5, padx=5)

registerMail = CTkEntry(registerTabForm, placeholder_text="E-Mail", font=font_entry)
registerMail.grid(row=1, column=0, pady=5, padx=5)

registerPassword = CTkEntry(registerTabForm, placeholder_text="Password", font=font_entry, show="*")
registerPassword.grid(row=2, column=0, pady=5, padx=5)
    
registerConfirmPassword = CTkEntry(registerTabForm, placeholder_text="Confirm Password", font=font_entry, show="*")
registerConfirmPassword.grid(row=3, column=0, pady=5, padx=5)

registerButton = CTkButton(registerTabForm, text="Register", font=font_entry, command=register)
registerButton.grid(row=4, column=0, pady=5, padx=5)

#Login GUI
loginTabFrame = CTkFrame(loginTab)
loginTabFrame.pack(pady=5, padx=5, fill=BOTH, expand=True)

loginTabForm = CTkFrame(loginTabFrame)
loginTabForm.place(relx=0.5, rely=0.5, anchor=CENTER)

loginEmailEntry = CTkEntry(loginTabForm, placeholder_text="E-Mail", font=font_entry)
loginEmailEntry.grid(row=0, column=0, pady=5, padx=5)

loginPasswordEntry = CTkEntry(loginTabForm, placeholder_text="Password", font=font_entry, show="*")
loginPasswordEntry.grid(row=1, column=0, pady=5, padx=5)

loginButton = CTkButton(loginTabForm, text="Log In", font=font_entry, command=login)
loginButton.grid(row=2, column=0, pady=5, padx=5)

#Jobs GUI + Func
jobsTabFrame = CTkFrame(jobsTab)
jobsTabFrame.pack(fill=BOTH, expand=True)



def get_jobs():
    if steam_id:
        try:
            # Fetch jobs from DB
            cursor.execute(f"SELECT * FROM jobs WHERE steam_id = %s", (steam_id,))
            jobs = cursor.fetchall() 
            if jobs:
                jobsTable = CTkScrollableFrame(jobsTabFrame, orientation="horizontal") if len(jobs) <= 10 else CTkXYFrame(jobsTabFrame)
                jobsTable.grid(row=1, column=0, pady=5, padx=5, sticky="nsew")

                jobsTabFrame.grid_rowconfigure(1, weight=1)
                jobsTabFrame.grid_columnconfigure(0, weight=1)

                loadJobsButton.configure(text="Refresh Jobs")
                loadJobsButton.place_forget()
                loadJobsButton.grid(row=0, column=0, pady=5, padx=5, sticky="ew")

                row = 0

                jobDateLabel = CTkLabel(jobsTable, text="Delivery Date", font=h2)	
                jobDateLabel.grid(row=row, column=0, pady=5, padx=5)

                jobStartLabel = CTkLabel(jobsTable, text="Start", font=h2)
                jobStartLabel.grid(row=row, column=1, pady=5, padx=5)

                jobFinishLabel = CTkLabel(jobsTable, text="Finish", font=h2)
                jobFinishLabel.grid(row=row, column=2, pady=5, padx=5)

                jobCargoLabel = CTkLabel(jobsTable, text="Cargo", font=h2)
                jobCargoLabel.grid(row=row, column=3, pady=5, padx=5)

                jobWeightLabel = CTkLabel(jobsTable, text="Weight", font=h2)
                jobWeightLabel.grid(row=row, column=4, pady=5, padx=5)

                jobDistanceLabel = CTkLabel(jobsTable, text="Distance", font=h2)
                jobDistanceLabel.grid(row=row, column=5, pady=5, padx=5)

                jobIncomeLabel = CTkLabel(jobsTable, text="Income", font=h2)
                jobIncomeLabel.grid(row=row, column=6, pady=5, padx=5)

                jobTruckTrailerLabel = CTkLabel(jobsTable, text="Truck + Trailer", font=h2)
                jobTruckTrailerLabel.grid(row=row, column=7, pady=5, padx=5)

                jobFuelLabel = CTkLabel(jobsTable, text="Fuel", font=h2)
                jobFuelLabel.grid(row=row, column=8, pady=5, padx=5)

                for job in jobs:
                    jobDate = CTkLabel(jobsTable, text=jobs[row][2], font=font_job)
                    jobDate.grid(row=row+1, column=0, pady=5, padx=5)

                    jobStart = CTkLabel(jobsTable, text=jobs[row][3], font=font_job)
                    jobStart.grid(row=row+1, column=1, pady=5, padx=5)

                    jobFinish = CTkLabel(jobsTable, text=jobs[row][4], font=font_job)
                    jobFinish.grid(row=row+1, column=2, pady=5, padx=5)

                    jobCargo = CTkLabel(jobsTable, text=jobs[row][5], font=font_job)
                    jobCargo.grid(row=row+1, column=3, pady=5, padx=5)

                    jobWeight = CTkLabel(jobsTable, text=f"{jobs[row][6]}T", font=font_job)
                    jobWeight.grid(row=row+1, column=4, pady=5, padx=5)

                    jobDistance = CTkLabel(jobsTable, text=f"{jobs[row][7]}km", font=font_job)
                    jobDistance.grid(row=row+1, column=5, pady=5, padx=5)

                    jobIncome = CTkLabel(jobsTable, text=f"{jobs[row][8]}€", font=font_job)
                    jobIncome.grid(row=row+1, column=6, pady=5, padx=5)

                    jobTruckTrailer = CTkLabel(jobsTable, text=f"{jobs[row][9]} + {jobs[row][10]}")
                    jobTruckTrailer.grid(row=row+1, column=7, pady=5, padx=5)

                    jobFuel = CTkLabel(jobsTable, text=f"{jobs[row][11]}L", font=font_job)
                    jobFuel.grid(row=row+1, column=8, pady=5, padx=5)

                    row += 1
            else:
                messagebox.showerror("Error", "You haven't logged a job, please log a job first, then try again!")
                tabview.set("Logger")

            frontend.update_idletasks()
            frontend.geometry("")

        except Exception as e:
            print(f"Error loading jobs: {e}")
            if steam_id == "" or steam_id == None or isinstance(steam_id, float):
                messagebox.showerror("Error", "Failed to load jobs. Please log in first or log a job")    
        
loadJobsButton = CTkButton(jobsTabFrame, text="Load Jobs", command=get_jobs)
loadJobsButton.place(relx=0.5, rely=0.1, anchor=CENTER)

#Logger GUI
loggerTabFrame = CTkFrame(loggerTab)
loggerTabFrame.pack(fill=BOTH, expand=True)

loggerTabFrameForm = CTkFrame(loggerTabFrame)
loggerTabFrameForm.place(relx=0.5, rely=0.5, anchor=CENTER)

def submit_job():
    global steam_id
    steam_id = int(steam_id)
    job_id = random.randint(100000, 999999)
    date = loggerDateEntry.get()
    start = loggerStartEntry.get()
    finish = loggerFinishEntry.get()
    cargo = loggerCargoEntry.get()
    weight = int(loggerWeightEntry.get())

    distance = int(loggerDistanceEntry.get())
    income = int(loggerIncomeEntry.get())
    truck = loggerTruckEntry.get()
    trailer = loggerTrailerEntry.get()
    fuel = int(loggerFuelEntry.get())
    cursor.execute("SELECT username FROM users WHERE steam_id = %s", (steam_id,))
    username = cursor.fetchone()

    cursor.execute("INSERT INTO jobs VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (job_id, steam_id, date, start, finish, cargo, weight, distance, income, truck, trailer, fuel))
    conn.commit()

    embed = Embed(
        title="Job Submitted",
        description=f"A new job has been submitted by **{username}**.",  # Description
        color=0x8c52ff    
        )

    embed.add_field(name="Job ID", value=str(job_id), inline=True)
    embed.add_field(name="Date", value=date, inline=True)
    embed.add_field(name="Start", value=start, inline=True)
    embed.add_field(name="Finish", value=finish, inline=True)
    embed.add_field(name="Cargo", value=f"{cargo} - ({weight}T)", inline=True)
    embed.add_field(name="Distance", value=f"{distance}km", inline=True)
    embed.add_field(name="Income", value=f"{income}€", inline=True)
    embed.add_field(name="Truck + Trailer", value=f"{truck} + {trailer}", inline=True)
    embed.add_field(name="Fuel", value=f"{fuel}L", inline=True)

    hook.send(embed=embed)

    messagebox.showinfo(("Job Submitted on %s by %s", (date, username)), "Job ID: %s\n%s - %s (%skm)\nCargo: %s - (%sT)\nIncome: %s€\nVehicle: %s + %s\nFuel: %sL", (job_id, start, finish, distance, cargo, weight, income, truck, trailer, fuel))

    

#Left Column
loggerDateEntry = CTkEntry(loggerTabFrameForm, placeholder_text="YYYY-MM-DD", font=font_entry)
loggerDateEntry.grid(row=0, column=0, pady=5, padx=5)

loggerStartEntry = CTkEntry(loggerTabFrameForm, placeholder_text="From (City, Country)", font=font_entry)
loggerStartEntry.grid(row=1, column=0, pady=5, padx=5)

loggerFinishEntry = CTkEntry(loggerTabFrameForm, placeholder_text="To (City, Country)", font=font_entry)
loggerFinishEntry.grid(row=2, column=0, pady=5, padx=5)

loggerCargoEntry = CTkEntry(loggerTabFrameForm, placeholder_text="Cargo", font=font_entry)
loggerCargoEntry.grid(row=3, column=0, pady=5, padx=5)

loggerWeightEntry = CTkEntry(loggerTabFrameForm, placeholder_text="Weight (T)", font=font_entry)
loggerWeightEntry.grid(row=4, column=0, pady=5, padx=5)

#Right Column
loggerDistanceEntry = CTkEntry(loggerTabFrameForm, placeholder_text="Distance (km)", font=font_entry)
loggerDistanceEntry.grid(row=0, column=1, pady=5, padx=5)

loggerIncomeEntry = CTkEntry(loggerTabFrameForm, placeholder_text="Income (€)", font=font_entry)
loggerIncomeEntry.grid(row=1, column=1, pady=5, padx=5)

loggerTruckEntry = CTkEntry(loggerTabFrameForm, placeholder_text="Truck", font=font_entry)
loggerTruckEntry.grid(row=2, column=1, pady=5, padx=5)

loggerTrailerEntry = CTkEntry(loggerTabFrameForm, placeholder_text="Trailer", font=font_entry)
loggerTrailerEntry.grid(row=3, column=1, pady=5, padx=5)

loggerFuelEntry = CTkEntry(loggerTabFrameForm, placeholder_text="Fuel (L)", font=font_entry)
loggerFuelEntry.grid(row=4, column=1, pady=5, padx=5)

loggerSubmitJob = CTkButton(loggerTabFrameForm, text="Submit Job", font=font_entry, command=submit_job)
loggerSubmitJob.grid(row=5, column=0, columnspan=2, pady=5, padx=5, sticky="ew")

logoutButton = CTkButton(frontend, text="Logout", command=logout, width=80)
logoutButton.place(relx=0.97, rely=0.02, anchor="ne")

profileTabFrame = CTkFrame(profileTab)
profileTabFrame.pack(fill=BOTH, expand=True)

profileTabGrid = CTkFrame(profileTabFrame)
profileTabGrid.place(relx=0.5, rely=0.5, anchor=CENTER)

#Profile GUI
def load_profile():
    global steam_id

    if steam_id != "":
        cursor.execute("SELECT * FROM users WHERE steam_id = %s", (steam_id,))
        user = cursor.fetchone()

        for i in range(4):
            profileTabGrid.columnconfigure(i, weight=1)

        nameLabel = CTkLabel(profileTabGrid, text=f"Welcome {user[3]}({user[6]})!", font=h1)
        nameLabel.grid(row=0, column=0, columnspan=3, sticky="ew", pady=5, padx=5)

        jobsFrame = CTkFrame(profileTabGrid)
        jobsFrame.grid(row=1, column=0, sticky="nsew", pady=5, padx=5)

        jobsHeading = CTkLabel(jobsFrame, text="Jobs", font=h2, anchor=CENTER)
        jobsHeading.grid(row=0, column=0, sticky="ew", pady=5, padx=5)

        jobsAmount = CTkLabel(jobsFrame, text=user[7], font=font_job, anchor=CENTER)
        jobsAmount.grid(row=1, column=0, sticky="ew", pady=5, padx=5)

        mileageFrame = CTkFrame(profileTabGrid)
        mileageFrame.grid(row=1, column=1, sticky="nsew", pady=5, padx=5)

        mileageHeading = CTkLabel(mileageFrame, text="Mileage", font=h2, anchor=CENTER)
        mileageHeading.grid(row=0, column=0, sticky="ew", pady=5, padx=5)

        mileageAmount = CTkLabel(mileageFrame, text=f"{user[8]}km", font=font_job, anchor=CENTER)
        mileageAmount.grid(row=1, column=0, sticky="ew", pady=5, padx=5)

        profitFrame = CTkFrame(profileTabGrid)
        profitFrame.grid(row=1, column=2, sticky="nsew", pady=5, padx=5)

        profitHeading = CTkLabel(profitFrame, text="Profit", font=h2, anchor=CENTER)
        profitHeading.grid(row=0, column=0, sticky="ew", pady=5, padx=5)

        profitAmount = CTkLabel(profitFrame, text=f"{user[9]}€", font=font_job, anchor=CENTER)
        profitAmount.grid(row=1, column=0, sticky="ew", pady=5, padx=5)

        levelFrame = CTkFrame(profileTabGrid)
        levelFrame.grid(row=1, column=3, sticky="nsew", pady=5, padx=5)

        levelHeading = CTkLabel(levelFrame, text="Level", font=h2, anchor=CENTER)
        levelHeading.grid(row=0, column=0, sticky="ew", pady=5, padx=5)

        levelAmount = CTkLabel(levelFrame, text=f"Lvl. {user[10]}", anchor=CENTER)
        levelAmount.grid(row=1, column=0, sticky="ew", pady=5, padx=5)

        loadProfileButton.place_forget()
        loadProfileButton.configure(text="Refresh Profile")
        loadProfileButton.grid(row=2, column=0, columnspan=4, sticky="ew", in_=profileTabGrid)
    else:
        messagebox.showerror("Error", "Please login first!")


loadProfileButton = CTkButton(profileTabGrid, text="Load Profile", font=font_entry, command=load_profile)
loadProfileButton.place(relx=0.5, rely=0.5, anchor=CENTER)

"""
def download_file_from_drive(url, output):
    #Download a file from Google Drive
    gdown.download(url, output, quiet=False)
    print(f"Downloaded to {output}")

def download_mod(mod_number):
    #Download a mod file based on user selection
    file_urls = {
        1: "https://drive.google.com/uc?id=1nSj9dD8HdvjJSDRY9xUTZyV7FYc95uM9",
        2: "https://drive.google.com/uc?id=14nsl5zGeEjRXxurqjJfcVxtDQBrP_vaw",
        3: "https://drive.google.com/uc?id=1XLSlARWxjm-_bxUrG-UhTO-4gtqR06mw",
        4: "https://drive.google.com/uc?id=1BTY4d1Jxi0KtD9mQ6AgJvIgPuxpdxokr"
    }
    
    file_url = file_urls.get(mod_number)
    if not file_url:
        messagebox.showerror("Error", "Invalid mod number.")
        return
    
    # Ask user for a destination folder
    folder_selected = filedialog.askdirectory(title="Select Download Folder")
    if not folder_selected:
        messagebox.showinfo("Cancelled", "Download cancelled.")
        return
    
    output = f"{folder_selected}/mod_{mod_number}.zip"
    download_file_from_drive(file_url, output)
    messagebox.showinfo("Download Complete", f"Mod {mod_number} downloaded to:\n{output}")


#Mods GUI
modsTabFrame = CTkFrame(modsTab)
modsTabFrame.pack(pady=5, padx=5, fill=BOTH, expand=True)

modsTabGrid = CTkFrame(modsTabFrame)
modsTabGrid.place(relx=0.5, rely=0.5, anchor=CENTER)

modsHeading = CTkLabel(modsTabFrame, text="Download our mods!", font=h2)
modsHeading.grid(row=0, column=1, columnspan=2, pady=5, padx=5, sticky="ew")

mod1Frame = CTkFrame(modsTabGrid)
mod1Frame.grid(row=1, column=0, pady=5, padx=5, sticky="nsew")

mod2Frame = CTkFrame(modsTabGrid)
mod2Frame.grid(row=1, column=1, pady=5, padx=5, sticky="nsew")

mod3Frame = CTkFrame(modsTabGrid)
mod3Frame.grid(row=2, column=0, pady=5, padx=5, sticky="nsew")

mod4Frame = CTkFrame(modsTabGrid)
mod4Frame.grid(row=2, column=1, pady=5, padx=5, sticky="nsew")

mod1Image = CTkImage(light_image=Image.open('./assets/placeholder1.jpg'), dark_image=Image.open('./assets/placeholder1.jpg'), size=(256,144))
mod1ImageLabel = CTkLabel(mod1Frame, text="", image=mod1Image)
mod1ImageLabel.grid(row=0, column=0, sticky="nse", pady=(0, 5), padx=0)
mod1Heading = CTkLabel(mod1Frame, text="Mod 1", font=h2)
mod1Heading.grid(row=1, column=0, sticky="ew")
mod1Button = CTkButton(mod1Frame, text="Download", font=h2, command=lambda: download_mod(1))
mod1Button.grid(row=2, column=0, sticky="sew")

mod2Image = CTkImage(light_image=Image.open('./assets/placeholder2.jpg'), dark_image=Image.open('./assets/placeholder2.jpg'), size=(256,144))
mod2ImageLabel = CTkLabel(mod2Frame, text="", image=mod2Image)
mod2ImageLabel.grid(row=0, column=0, sticky="nse", pady=(0, 5), padx=0)
mod2Heading = CTkLabel(mod2Frame, text="Mod 2", font=h2)
mod2Heading.grid(row=1, column=0, sticky="ew")
mod2Button = CTkButton(mod2Frame, text="Download", font=h2, command=lambda: download_mod(2))
mod2Button.grid(row=2, column=0, sticky="sew")

mod3Image = CTkImage(light_image=Image.open('./assets/placeholder3.jpg'), dark_image=Image.open('./assets/placeholder3.jpg'), size=(256,144))
mod3ImageLabel = CTkLabel(mod3Frame, text="", image=mod3Image)
mod3ImageLabel.grid(row=0, column=0, sticky="nse", pady=(0, 5), padx=0)
mod3Heading = CTkLabel(mod3Frame, text="Mod 3", font=h2)
mod3Heading.grid(row=1, column=0, sticky="ew")
mod3Button = CTkButton(mod3Frame, text="Download", font=h2, command=lambda: download_mod(3))
mod3Button.grid(row=2, column=0, sticky="sew")

mod4Image = CTkImage(light_image=Image.open('./assets/placeholder4.jpg'), dark_image=Image.open('./assets/placeholder4.jpg'), size=(256,144))
mod4ImageLabel = CTkLabel(mod4Frame, text="", image=mod4Image)
mod4ImageLabel.grid(row=0, column=0, sticky="nse", pady=(0, 5), padx=0)
mod4Heading = CTkLabel(mod4Frame, text="Mod 4", font=h2)
mod4Heading.grid(row=1, column=0, sticky="ew")
mod4Button = CTkButton(mod4Frame, text="Download", font=h2, command=lambda: download_mod(4))
mod4Button.grid(row=2, column=0, sticky="sew")"""

if __name__ == "__main__":
    if check_existing_session() == True:
        tabview.delete("Login")
        tabview.delete("Register")
    frontend.mainloop()

