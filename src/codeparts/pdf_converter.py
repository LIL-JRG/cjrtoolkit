import os
import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfReader, PdfWriter
from docx import Document
from openpyxl import Workbook
from pptx import Presentation
from PIL import Image
import io
from system.config import RESULT_FOLDER
from docx.shared import Inches
from pptx.util import Inches as PptxInches
import tabula
import pandas as pd

class PDFConverter:
    @staticmethod
    def select_file():
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("Word files", "*.docx"), ("Excel files", "*.xlsx"), ("PowerPoint files", "*.pptx")])
        return file_path

    @staticmethod
    def create_output_folder(input_file):
        pdf_converter_folder = os.path.join(RESULT_FOLDER, "PDF Converter")
        os.makedirs(pdf_converter_folder, exist_ok=True)
        
        file_name = os.path.splitext(os.path.basename(input_file))[0]
        output_folder = os.path.join(pdf_converter_folder, file_name)
        os.makedirs(output_folder, exist_ok=True)
        
        return output_folder

    @staticmethod
    async def pdf_to_word(pdf_path: str) -> str:
        output_folder = PDFConverter.create_output_folder(pdf_path)
        output_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(pdf_path))[0]}.docx")
        try:
            pdf = PdfReader(pdf_path)
            doc = Document()
            
            for page in pdf.pages:
                text = page.extract_text()
                paragraphs = text.split('\n\n')
                for para in paragraphs:
                    doc.add_paragraph(para)
                
                # Add images
                for image in page.images:
                    img = Image.open(io.BytesIO(image.data))
                    img_path = os.path.join(output_folder, f"temp_image_{image.name}.png")
                    img.save(img_path)
                    doc.add_picture(img_path, width=Inches(6))
                    os.remove(img_path)
                
                doc.add_page_break()
            
            doc.save(output_path)
            return f"Conversión exitosa. Archivo guardado en: {output_path}"
        except Exception as e:
            return f"Error en la conversión a Word: {str(e)}"

    @staticmethod
    async def pdf_to_excel(pdf_path: str) -> str:
        output_folder = PDFConverter.create_output_folder(pdf_path)
        output_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(pdf_path))[0]}.xlsx")
        try:
            # Use tabula to extract tables from PDF
            tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
            
            with pd.ExcelWriter(output_path) as writer:
                for i, table in enumerate(tables):
                    table.to_excel(writer, sheet_name=f'Sheet{i+1}', index=False)
            
            return f"Conversión exitosa. Archivo guardado en: {output_path}"
        except Exception as e:
            return f"Error en la conversión a Excel: {str(e)}"

    @staticmethod
    async def pdf_to_powerpoint(pdf_path: str) -> str:
        output_folder = PDFConverter.create_output_folder(pdf_path)
        output_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(pdf_path))[0]}.pptx")
        try:
            pdf = PdfReader(pdf_path)
            prs = Presentation()
            
            for page in pdf.pages:
                slide = prs.slides.add_slide(prs.slide_layouts[5])
                
                # Add text
                text = page.extract_text()
                txBox = slide.shapes.add_textbox(PptxInches(0.5), PptxInches(0.5), 
                                                 PptxInches(9), PptxInches(5))
                tf = txBox.text_frame
                tf.text = text
                
                # Add images
                left = top = PptxInches(1)
                for image in page.images:
                    img = Image.open(io.BytesIO(image.data))
                    img_path = os.path.join(output_folder, f"temp_image_{image.name}.png")
                    img.save(img_path)
                    slide.shapes.add_picture(img_path, left, top, height=PptxInches(4))
                    os.remove(img_path)
                    left += PptxInches(4)
            
            prs.save(output_path)
            return f"Conversión exitosa. Archivo guardado en: {output_path}"
        except Exception as e:
            return f"Error en la conversión a PowerPoint: {str(e)}"

    @staticmethod
    async def office_to_pdf(input_path: str) -> str:
        output_folder = PDFConverter.create_output_folder(input_path)
        output_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(input_path))[0]}.pdf")
        try:
            from win32com import client
            if input_path.endswith('.docx'):
                word = client.Dispatch('Word.Application')
                doc = word.Documents.Open(input_path)
                doc.SaveAs(output_path, FileFormat=17)  # wdFormatPDF = 17
                doc.Close()
                word.Quit()
            elif input_path.endswith('.xlsx'):
                excel = client.Dispatch('Excel.Application')
                wb = excel.Workbooks.Open(input_path)
                wb.ExportAsFixedFormat(0, output_path)  # xlTypePDF = 0
                wb.Close()
                excel.Quit()
            elif input_path.endswith('.pptx'):
                powerpoint = client.Dispatch('Powerpoint.Application')
                presentation = powerpoint.Presentations.Open(input_path)
                presentation.SaveAs(output_path, 32)  # ppSaveAsPDF = 32
                presentation.Close()
                powerpoint.Quit()
            else:
                return "Formato de archivo no soportado"
            return f"Conversión exitosa. Archivo guardado en: {output_path}"
        except Exception as e:
            return f"Error en la conversión a PDF: {str(e)}"

    @staticmethod
    async def extract_images_from_pdf(pdf_path: str) -> str:
        output_folder = PDFConverter.create_output_folder(pdf_path)
        try:
            pdf = PdfReader(pdf_path)
            for page_num, page in enumerate(pdf.pages, 1):
                for img_num, image in enumerate(page.images, 1):
                    img = Image.open(io.BytesIO(image.data))
                    img_filename = f"image_page{page_num}_{img_num}.png"
                    img_path = os.path.join(output_folder, img_filename)
                    img.save(img_path)
            return f"Extracción de imágenes exitosa. Imágenes guardadas en: {output_folder}"
        except Exception as e:
            return f"Error en la extracción de imágenes: {str(e)}"