
from PyPDF2 import PdfFileReader
from PyPDF2.pdf import ContentStream
from PyPDF2.generic import TextStringObject
from PyPDF2.utils import b_


def get_pdf_content(path):
    # Load PDF into pyPDF
    pdf = PdfFileReader(open(path, "rb"))

    # The contents will end up in this list
    lines = []

    # This vodoo code is taken from the extractText method of the PageObject.
    content = pdf.getPage(0)["/Contents"].getObject()
    if not isinstance(content, ContentStream):
        content = ContentStream(content, pdf)

    for operands, operator in content.operations:
        if operator == b_("Tj"):
            text = operands[0]
            if isinstance(text, TextStringObject):
                lines.append(text)
    return lines
