import tkinter as tk
from tkinter import filedialog, messagebox
from docx import Document
import requests
import os




# select and parse a locally saved document
def loadDocument():
    # get file path - SUPPORTED FILE TYPES: docx, txt, pdf
    path = filedialog.askopenfilename(filetypes=[("Word Document", "*.docx"), ("Text File", "*.txt"), ("PDF Document", "*.pdf")])
    # check to make sure a file was selected - if not exit
    if not path:
        return None, None
    try:
        # get the name of the file
        fileName = os.path.basename(path)
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
 
        return fileName, contents

    # error message exception catch
    except Exception as e:
        messagebox.showerror("Error", f"Error loading document: {e}")
        return None, None
    

# handles the Gemini API call 
class geminiCall:
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
            generatedAnswer = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            return generatedAnswer
        except Exception as e:
            raise Exception(f"Error calling Gemini API: {e}")
        

# creates quiz questions for the selected document
# a max of 5 quiz questions but depending on the contents of the document fewer can be presented
# a keyword from the question is replaced with _______ for a fill-in-the-blank quiz experience
# Example: 
#   Question: The ________ is the main heat source for the Earth.
#   Answer: Sun
class quizQuestions:
    # get the geminiCall instance from the GUI class
    def __init__(self, geminiCall):
        self.geminiCall = geminiCall

    #
    def generate(self, contents):
        # check that contents string is populated
        if not contents:
            raise ValueError("Error: Selected document has no contents")
        
        # prompt used to guide the AI to create the quiz questions - Specifies how many, what we want, and how to format the answer
        prompt = f"Generate 5 fill-in-the-blank quiz questions from this text. You must be able to know the answer solely based on the information in the text. Format each as '(# of question). [question]\nAnswer: [answer]'\n\n. Example response: 1. The _____ is the main heat source for the Earth.\nAnswer: Sun\n\nAlso after each answer have a newline character. Here is the text {contents}"
        generatedAnswer = self.geminiCall.call(prompt)
        return generatedAnswer


# GUI class for the AI study assistant
class GUI:
    def __init__(self, root):
        # setup GUI main window
        self.root = root
        self.root.title("AI Study Assistant - Powered by Gemini")
        self.root.geometry("700x470")
        self.contents = ""

        # initialize class objects
        self.geminiCall = geminiCall()
        self.quizQuestions = quizQuestions(self.geminiCall)

        # select document button
        tk.Button(self.root, text="Select Document", command = self.loadDocument).pack(pady=5)

        # status label to show file name of the loaded document
        self.status_label = tk.Label(self.root, text="No document selected")
        self.status_label.pack(pady=5) 

        # function buttons - summarization, keyTopics, flashcards, quizQuestions, pomodoroTimer
        buttons = tk.Frame(self.root)
        buttons.pack(pady=5)
        tk.Button(buttons, text="Quiz", command=self.runQuiz).pack(pady=5)

        # text output area 
        self.outputArea = tk.Text(self.root, height=20, width=80, wrap="word")
        self.outputArea.pack(pady=5)



    # calls the global loadDocument function
    # updates the UI: shows confirmation message in outputArea - shows filename under "Select Document" button
    def loadDocument(self):
        fileName, contents = loadDocument()
        if fileName and contents:
            self.contents = contents
            # clear outputArea
            self.outputArea.delete(1.0, tk.END)
            # display success message
            self.outputArea.insert(tk.END, f"Document '{fileName}' loaded.\n")
            # upadate status label to show filename under "Select Document" button
            self.status_label.config(text=fileName)
    

    # calls the quizQuestions generate function
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
            questions = self.quizQuestions.generate(self.contents)
            # clear output area
            self.outputArea.delete(1.0, tk.END)
            # display results
            self.outputArea.insert(tk.END, questions)
        except Exception as e:
            self.outputArea.delete(1.0, tk.END)
            # display error message
            self.outputArea.insert(tk.END, f"Error: {e}\n")









if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()
            
        









