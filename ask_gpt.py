import tkinter as tk
from tkinter import scrolledtext
import functions as func
import catch_news

# Constants
TEXT_HEIGHT = 10
PADDING_X = 5
PADDING_Y = 5

def summarize(input_widget, output_widget, summarize_function):
    input_text = input_widget.get("1.0", tk.END).replace('\n', '').encode('utf-8')
    output_text = summarize_function(input_text)
    output_widget.delete("1.0", tk.END)
    output_widget.insert(tk.END, output_text)
    input_string = input_text.decode('utf-8')
    if "http" in input_text.decode('utf-8'):
        catch_news.add_links([input_text])

def create_summary_section(frame, title, summarize_function):
    tk.Label(frame, text=title).pack()
    input_widget = scrolledtext.ScrolledText(frame, height=TEXT_HEIGHT)
    input_widget.pack(padx=PADDING_X, pady=PADDING_Y, fill=tk.BOTH, expand=True)
    tk.Button(frame, text="Summarize", command=lambda: summarize(input_widget, output_widget, summarize_function)).pack(pady=PADDING_Y)
    output_widget = scrolledtext.ScrolledText(frame, height=TEXT_HEIGHT)
    output_widget.pack(padx=PADDING_X, pady=PADDING_Y, fill=tk.BOTH, expand=True)
    return input_widget, output_widget

def main():
    # Create the main window
    root = tk.Tk()
    root.title("Summarization Tool")

    # Create frames for each section
    paper_frame = tk.Frame(root)
    web_frame = tk.Frame(root)
    product_frame = tk.Frame(root)

    paper_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    web_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    product_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Create summary sections
    create_summary_section(paper_frame, "Paper Summary", func.summarize_paper)
    create_summary_section(web_frame, "Web Content Summary", func.summarize_web)
    create_summary_section(product_frame, "Product Summary", func.summarize_product)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    main()
