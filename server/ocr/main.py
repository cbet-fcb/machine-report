import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from PIL import Image, ImageTk
import argparse

import preprocessing
import ocr
import postprocessing

class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR Pipeline GUI")
        self.root.geometry("800x600")

        # UI Elements
        self.image_label = tk.Label(self.root, text="No image selected", width=50)
        self.image_label.pack(pady=10)

        self.select_button = tk.Button(self.root, text="Select Image", command=self.select_image)
        self.select_button.pack()

        self.run_button = tk.Button(self.root, text="Run OCR Pipeline", command=self.run_pipeline)
        self.run_button.pack(pady=10)

        self.output = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=100, height=25)
        self.output.pack(padx=10, pady=10)

        self.selected_image_path = None

    def select_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            self.selected_image_path = path
            self.image_label.config(text=path)

    def run_pipeline(self):
        if not self.selected_image_path:
            messagebox.showwarning("No Image", "Please select an image first.")
            return

        try:
            pass
            # Step 1: Preprocessing
            # img = preprocessing.load_and_preprocess_image(self.selected_image_path)

            # # Step 2: OCR
            # raw_ocr_results = ocr.ocr_image(img)

            # # Step 3: Postprocessing
            # final_data = postprocessing.process_ocr_results(raw_ocr_results)

            # # Show result
            # self.output.delete("1.0", tk.END)
            # self.output.insert(tk.END, final_data)

        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong:\n{str(e)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run PaddleOCR on a local image or URL.')
    parser.add_argument('--image', required=True, help='Path to local image or URL, or directory of images')
    parser.add_argument('--prep_dir', default=None, help='Directory to save preprocessed images (if set, preprocessing is applied)')
    parser.add_argument('--json_dir', default='ocr_output', help='Directory to save output JSON files')
    parser.add_argument('--font', default='C:/Windows/Fonts/arial.ttf', help='Path to .ttf font for drawing')
    parser.add_argument('--no_show', action='store_true', help="Don't display OCR result image")
    args = parser.parse_args()

    image_paths = ocr.get_image_paths(args.image)

    if args.prep_dir:
        print("Preprocessing images in parallel…")
        image_paths = preprocessing.process_batched_preprocessing(image_paths, args.prep_dir)

    print(f"Processing {len(image_paths)} images…")
    
    ocr.process_batched_images_to_ocr(
        image_paths=image_paths,
        font_path=args.font,
        save_json=True,
        json_dir=args.json_dir
    )

    print("✅ All images processed successfully.")
    pass
