from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io


def add_page_numbers(input_pdf_path, output_pdf_path):
    # Read the input PDF
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # For each page
    for page_num in range(len(reader.pages)):
        # Create a PDF with just the page number
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

        # Add page number in bottom right
        can.setFont("Helvetica", 13)
        page_text = f"ACTUAL PAGE NUMBER: {page_num + 1}"
        # Position text in bottom right, 15 pixels from bottom and right edges
        can.drawString(
            letter[0] / 2 - 50, 5, page_text
        )  # Centered horizontally, 5 pixels from bottom
        can.save()

        # Move to the beginning of the BytesIO buffer
        packet.seek(0)
        number_pdf = PdfReader(packet)

        # Get the existing page
        page = reader.pages[page_num]

        # Merge the page with the page number
        page.merge_page(number_pdf.pages[0])

        # Add the merged page to the output
        writer.add_page(page)

    # Write the output PDF
    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)


if __name__ == "__main__":
    input_pdf = "manual_130.pdf"
    output_pdf = "manual_130_numbered.pdf"
    add_page_numbers(input_pdf, output_pdf)
    print(f"Added page numbers to {input_pdf}. Output saved as {output_pdf}")
