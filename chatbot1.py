import google.generativeai as genai
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading


API_KEY = "AIzaSyDxg9z7XFXJzNJehDhLjbPgDoxoweX0XNw"  
genai.configure(api_key=API_KEY)


class EducationalChatbot:
    def __init__(self, root):
        self.root = root
        self.root.title("Educational AI Chatbot")
        self.root.geometry("600x700")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize the Gemini model
        self.model = genai.GenerativeModel('gemini-pro-latest')
        self.chat = self.model.start_chat(history=[])
        
        # Set system context for educational purposes
        self.system_context = """You are a helpful educational assistant for students. 
        Your role is to:
        - Explain concepts clearly and simply
        - Help with homework and assignments
        - Provide step-by-step solutions
        - Answer questions on any subject
        - Be encouraging and supportive
        Keep your answers clear and student-friendly."""
        
        self.is_processing = False 
        
        self.setup_gui()
    
    def setup_gui(self):
       
        title_label = tk.Label(
            self.root, 
            text="📚 Educational AI Assistant", 
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
            fg="#333"
        )
        title_label.pack(pady=10)
        
      
        subtitle = tk.Label(
            self.root,
            text="Ask me anything about your studies!",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666"
        )
        subtitle.pack()
        
    
        chat_frame = tk.Frame(self.root, bg="#f0f0f0")
        chat_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=70,
            height=25,
            font=("Arial", 10),
            bg="#F5F5DC",  
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
       
        input_frame = tk.Frame(self.root, bg="#f0f0f0")
        input_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.user_input = tk.Entry(
            input_frame,
            font=("Arial", 11),
            bg="white"
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.user_input.bind("<Return>", lambda e: self.send_message())
        
        send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            width=10,
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0
        )
        send_button.pack(side=tk.RIGHT)
        
       
        clear_button = tk.Button(
            self.root,
            text="Clear Chat",
            command=self.clear_chat,
            bg="#c62d22",
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0
        )
        clear_button.pack(pady=5)
        
        
        self.display_message("Bot", "Hello! I'm your educational AI assistant. Ask me anything about your studies - math, science, history, or any subject!")
    
    def send_message(self):
        # Prevent multiple simultaneous requests
        if self.is_processing:
            return
            
        user_message = self.user_input.get().strip()
        
        if not user_message:
            return
        
        
        self.display_message("You", user_message)
        self.user_input.delete(0, tk.END)
        
       
        self.display_message("Bot", "Typing...")
        
        
        self.is_processing = True
        
        # Run API call in separate thread to keep GUI responsive
        thread = threading.Thread(target=self.get_bot_response, args=(user_message,))
        thread.daemon = True 
        thread.start()
    
    def get_bot_response(self, user_message):
        """This runs in a separate thread"""
        try:
            
            if len(self.chat.history) == 0:
                full_message = self.system_context + "\n\nStudent question: " + user_message
            else:
                full_message = user_message
            
            response = self.chat.send_message(full_message)
            bot_response = response.text
            
            
            self.root.after(0, self.update_bot_response, bot_response)
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}\n\nPlease check your API key and internet connection."
            self.root.after(0, self.update_bot_response, error_msg)
    
    def update_bot_response(self, bot_response):
        """This runs in the main GUI thread"""
        
        self.chat_display.config(state=tk.NORMAL)
        content = self.chat_display.get(1.0, tk.END)
        lines = content.split('\n')
        
    
        for i in range(len(lines) - 1, -1, -1):
            if "Typing..." in lines[i]:
                # Calculate position to delete
                line_num = i + 1
                self.chat_display.delete(f"{line_num}.0", f"{line_num}.end+1c")
                break
        
        self.chat_display.config(state=tk.DISABLED)
        
        
        self.display_message("Bot", bot_response)
        
    
        self.is_processing = False
    
    def display_message(self, sender, message):
        self.chat_display.config(state=tk.NORMAL)
        
        if sender == "You":
            self.chat_display.insert(tk.END, f"\n You: ", "user")
            self.chat_display.tag_config("user", foreground="#2196F3", font=("Arial", 10, "bold"))
        else:
            self.chat_display.insert(tk.END, f"\n Bot: ", "bot")
            self.chat_display.tag_config("bot", foreground="#4CAF50", font=("Arial", 10, "bold"))
        
        self.chat_display.insert(tk.END, f"{message}\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def clear_chat(self):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Reset chat history
        self.chat = self.model.start_chat(history=[])
        
        
        self.display_message("Bot", "Chat cleared! Ask me a new question.")


# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    app = EducationalChatbot(root)
    root.mainloop()
