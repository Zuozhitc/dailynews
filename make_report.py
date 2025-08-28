import tkinter as tk
from tkinter import ttk
import datetime
from tkinter import messagebox

from crawl_test import make_report
import traceback
from catch_news import delete_today_records

def main():
    try:
        def generate_report():
            manual = manual_var.get()
            news_days = news_days_var.get()
            paper_days = paper_days_var.get()
            include_news = include_news_var.get()
            include_papers = include_papers_var.get()
            include_product = include_product_var.get()

            progress_label.config(text="Generating report...")
            root.update_idletasks()

            try:
                make_report(manual, paper_days, news_days, include_news, include_papers, include_product)
                progress_label.config(text="Report generated successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate report: {e}")
                progress_label.config(text="")
            # finish the program
            root.quit()

        def delete_records():
            try:
                delete_today_records()
                messagebox.showinfo("Success", "Today's records deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete today's records: {e}")

        def confirm_delete():
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete today's records?"):
                delete_records()

        # Create the main application window
        root = tk.Tk()
        root.title("Report Generator")
        root.geometry("500x500")
        root.resizable(False, False)

        # Styling
        style = ttk.Style(root)
        style.configure("TButton", padding=6)
        style.configure("TLabel", padding=6)
        style.configure("TCheckbutton", padding=6)

        # Manual mode frame
        manual_frame = ttk.LabelFrame(root, text="Mode")
        manual_frame.pack(fill="x", padx=10, pady=10)
        manual_var = tk.BooleanVar(value=True)
        manual_check = ttk.Checkbutton(manual_frame, text="Manual Mode，附带新闻链接", variable=manual_var)
        manual_check.pack(anchor="w")

        # News section
        news_frame = ttk.LabelFrame(root, text="News Options")
        news_frame.pack(fill="x", padx=10, pady=10)
        include_news_var = tk.BooleanVar(value=True)
        include_news_check = ttk.Checkbutton(news_frame, text="Include News", variable=include_news_var)
        include_news_check.pack(anchor="w", side="left")
        news_days_label = ttk.Label(news_frame, text="Days:")
        news_days_label.pack(side="left", padx=10)
        news_days_var = tk.IntVar(value=2 if datetime.datetime.now().weekday() != 0 else 3)
        news_days_spinbox = ttk.Spinbox(news_frame, from_=0, to=14, textvariable=news_days_var,  width=5, font = ('Arial', 12))
        news_days_spinbox.pack(side="left",padx=10, pady= 10)

        # Papers section
        papers_frame = ttk.LabelFrame(root, text="Papers Options")
        papers_frame.pack(fill="x", padx=10, pady=10)
        include_papers_var = tk.BooleanVar(value=True)
        include_papers_check = ttk.Checkbutton(papers_frame, text="Include Papers", variable=include_papers_var)
        include_papers_check.pack(anchor="w", side="left")
        paper_days_label = ttk.Label(papers_frame, text="Days:")
        paper_days_label.pack(side="left", padx=5)
        paper_days_var = tk.IntVar(value=1 if datetime.datetime.now().weekday() != 1 else 3)
        paper_days_spinbox = ttk.Spinbox(papers_frame, from_=0, to=14, textvariable=paper_days_var, width=5, font = ('Arial', 12))
        paper_days_spinbox.pack(side="left", padx=10, pady= 10)

        # Product section
        product_frame = ttk.LabelFrame(root, text="Product Options")
        product_frame.pack(fill="x", padx=10, pady=10)
        include_product_var = tk.BooleanVar(value=True)
        include_product_check = ttk.Checkbutton(product_frame, text="Include Product", variable=include_product_var)
        include_product_check.pack(anchor="w")

        # Delete records button
        delete_button = ttk.Button(root, text="删除今日记录", command=confirm_delete, style="Delete.TButton")
        delete_button.pack(pady=5)

        # Generate report button
        generate_button = ttk.Button(root, text="开始生成报告", command=generate_report)
        generate_button.pack(pady=10)

        # Progress label
        progress_label = ttk.Label(root, text="")
        progress_label.pack()

        # Run the application
        root.mainloop()
        pass
    except Exception as e:
        print("An error occurred:")
        print(e)
        traceback.print_exc()

if __name__ == "__main__":
    main()
