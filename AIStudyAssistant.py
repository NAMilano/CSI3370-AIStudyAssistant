import tkinter as tk
from tkinter import filedialog, messagebox
from docx import Document
import requests
import os
import itertools
import random
    
# select and load a locally saved document 
class LoadDocument:
    def selectDocument(self):
        # get file path - SUPPORTED FILE TYPES: docx, txt, pdf
        path = filedialog.askopenfilename(filetypes=[("Word Document", "*.docx"), ("Text File", "*.txt"), ("PDF Document", "*.pdf")])

        # check to make sure a file was selected - if not exit
        if not path:
            return None, None
        
        # get the name of the file
        fileName = os.path.basename(path)
        return fileName, path


# parse a word doc, txt file, or PDF file compiling all the contents into a single string
class ParseDocument:
    def parse(self, path):
        if not path:
            return None
        try:
            # get the file type of the selected document
            fileType = path.split(".")[-1].lower()

            # word document parsing
            if fileType == "docx":
                wordDoc = Document(path)
                # combine all the contents of the document into one string
                contents = '\n'.join(sections.text for sections in wordDoc.paragraphs if sections.text)
                
            
            # # text file parsing
            # elif fileType == "txt":
            #     # parsing code here
            #    
            
            # # pdf file parsing
            # elif fileType == "pdf":
            #     #parsing code here
            #   
    
            return contents

        # error message exception catch
        except Exception as e:
            messagebox.showerror("Error", f"Error loading document: {e}")
            return None

    

# handles the Gemini API call 
class GeminiServices:
    # calls the Gemini API using a HTTP request and then receives the response in a json object
    def call(self, prompt):
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": prompt}]}], 
                 # limit output to 512 tokens ~680 words
                 # temperature set to 0.7 to balance randomness ensuring accuracy levels but allows for some creativity
                "generationConfig": {"maxOutputTokens": 512, "temperature": 0.7}
        }
        try:
            response = requests.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyC1hocc2oAhNvwTyPAmITPIMMbgocHWihc", headers = headers, json = data)
            response.raise_for_status()
            # get the generated AI answer from the returned json object
            questions = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            return questions
        except Exception as e:
            raise Exception(f"Error calling Gemini API: {e}")
        



# creates quiz questions for the selected document
# a max of 5 quiz questions but depending on the contents of the document fewer can be presented
# a keyword from the question is replaced with _______ for a fill-in-the-blank quiz experience
# Example: 
#   Question: The ________ is the main heat source for the Earth.
#   Answer: Sun
class QuizQuestions:
    # get the GeminiServices instance from the GUI class
    def __init__(self, geminiCall):
        self.geminiCall = geminiCall

    #
    def generate(self, contents):
        # check that contents string is populated
        if not contents:
            raise ValueError("Error: Selected document has no contents")
        
        # prompt used to guide the AI to create the quiz questions - Specifies how many, what we want, and how to format the answer
        prompt = f"Generate 5 fill-in-the-blank quiz questions from this text. You must be able to know the answer solely based on the information in the text. Format each as '(# of question). [question]\nAnswer: [answer]'\n\n. Example response: 1. The _____ is the main heat source for the Earth.\nAnswer: Sun\n\nAlso after each answer have a newline character. Here is the text {contents}"
        questions = self.geminiCall.call(prompt)
        return questions
    
class Flashcards:
    def __init__(self, geminiCall):
        self.geminiCall = geminiCall  # keep the same attribute name

    def generate(self, contents, n_cards=15):
        if not contents:
            raise ValueError("Error: Selected document has no contents")

        # TSV prompt
        prompt = (
            f"Create exactly {n_cards} flash-cards from the text below. Return ONLY plain text with one card per line, using a TAB between the question and the answer. Example: Are bananas berries?\tYes\n----- TEXT START -----\n"
            f"{contents}\n----- TEXT END -----"
        )
        raw = self.geminiCall.call(prompt)

        cards = []

        for ln in raw.splitlines():
            if "\t" in ln:
                q, a = ln.split("\t", 1)
                cards.append((q.strip(), a.strip()))

        if not cards:
            raise RuntimeError("Gemini did not return TSV flashcards..")
        return cards
    

class FlashcardViewer(tk.Toplevel):
    #class for flashcard viewer 

    def __init__(self, parent, cards):
        super().__init__(parent)
        self.title("Flash‑Card Review")
        self.geometry("500x260")

        # randomize the order of cards then cycles the same.
        random.shuffle(cards)
        self.deck = itertools.cycle(cards)

        # tkinter variables for question and answer
        self.q_var = tk.StringVar()
        self.a_var = tk.StringVar()

        # layout for the popup questions
        tk.Label(self, textvariable=self.q_var, wraplength=460,
                 font=("Helvetica", 15, "bold")).pack(pady=(25, 10))
        tk.Label(self, textvariable=self.a_var, wraplength=460,
                 font=("Helvetica", 14)).pack(pady=(0, 15))

        bar = tk.Frame(self)
        bar.pack()
        tk.Button(bar, text="Show Answer",
                  command=self.show_answer).pack(side=tk.LEFT, padx=6)
        tk.Button(bar, text="Next Card",
                  command=self.next_card).pack(side=tk.LEFT, padx=6)

        self.current = None
        self.next_card()          # shows the first q

    # helper functions 
    def next_card(self):
       # Load the next card and hide its answer
        self.current = next(self.deck)
        self.q_var.set(self.current[0])
        self.a_var.set("")

    def show_answer(self):
        # shows answer
        self.a_var.set(self.current[1])
    

class PromptController:
    def __init__(self):
        self.geminiCall = GeminiServices()
        self.quiz = QuizQuestions(self.geminiCall)
        self.cards = Flashcards(self.geminiCall)


    def generateQuizQuestions(self, contents):
        questions = self.quiz.generate(contents)
        return questions
    
    def generateFlashcards(self, contents, n_cards=15):
        return self.cards.generate(contents, n_cards)


# GUI class for the AI study assistant
class StudyAssistantGUI:
    def __init__(self, root):
        # setup GUI main window
        self.root = root
        self.root.title("AI Study Assistant - Powered by Gemini")
        self.root.geometry("700x470")
        self.contents = ""

        # initialize class objects
        self.loadDoc = LoadDocument()
        self.parseDoc = ParseDocument()
        self.promptCon = PromptController()
        self.flashcardWindow = None

        # select document button
        tk.Button(self.root, text="Select Document", command = self.selectDocument).pack(pady=5)

        # status label to show file name of the loaded document
        self.status_label = tk.Label(self.root, text="No document selected")
        self.status_label.pack(pady=5) 

        # function buttons - summarization, keyTopics, flashcards, QuizQuestions, pomodoroTimer
        buttons = tk.Frame(self.root)
        buttons.pack(pady=5)
        tk.Button(buttons, text="Quiz", command=self.runQuiz).pack(pady=5)

        tk.Button(buttons, text="Generate Flashcards", command=self.runFlashcards).pack(side=tk.LEFT, padx=5)
        
        # text output area 
        self.outputArea = tk.Text(self.root, height=20, width=80, wrap="word")
        self.outputArea.pack(pady=5)



    # select and load locally saved document
    # updates the UI: shows confirmation message in outputArea - shows filename under "Select Document" button
    def selectDocument(self):
        fileName, path = self.loadDoc.selectDocument()
        if fileName and path:
            self.contents = self.parseDoc.parse(path)
            # clear outputArea
            self.outputArea.delete(1.0, tk.END)
            # display success message
            self.outputArea.insert(tk.END, f"Document '{fileName}' loaded.\n")
            # upadate status label to show filename under "Select Document" button
            self.status_label.config(text=fileName)
    

    # generate quiz questions
    # updates the UI with the generated quiz questions
    def runQuiz(self):
        # check for a loaded document 
        if not self.contents:
            # error message when no document is loaded
            messagebox.showwarning("No document available", "Please select a document.")
            return
        
        # update output area with a processing message
        self.outputArea.delete(1.0, tk.END)
        self.outputArea.insert(tk.END, "Generating Quiz Questions...")
        self.root.update()

        try:
            # generate questions
            questions = self.promptCon.generateQuizQuestions(self.contents)
            # clear output area
            self.outputArea.delete(1.0, tk.END)
            # display results
            self.outputArea.insert(tk.END, questions)
        except Exception as e:
            self.outputArea.delete(1.0, tk.END)
            # display error message
            self.outputArea.insert(tk.END, f"Error: {e}\n")

    def runFlashcards(self):
        if not self.contents:
            messagebox.showwarning("No document available", "Please select a document.")
            return

        # show processing message
        self.outputArea.delete("1.0", tk.END)
        self.outputArea.insert(tk.END, "Generating flash-cards...")
        self.root.update()

        try:
            #flashcard method
            cards = self.promptCon.generateFlashcards(self.contents)  # returns list of (Q, A)
            self.outputArea.delete("1.0", tk.END)
            self.outputArea.insert(tk.END, f"{len(cards)} cards generated – launching viewer…")

            # check if the window is already created/open - if it is close it
            if self.flashcardWindow is not None and self.flashcardWindow.winfo_exists():
                self.flashcardWindow.destroy()

            # create flashcard UI element
            self.flashcardWindow = FlashcardViewer(self.root, cards) 
        except Exception as e:
            self.outputArea.delete("1.0", tk.END)
            self.outputArea.insert(tk.END, f"Error: {e}")



if __name__ == "__main__":
    root = tk.Tk()
    app = StudyAssistantGUI(root)
    root.mainloop()
            
        









