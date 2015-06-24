from PyPDF2 import PdfFileReader
from PyPDF2.pdf import ContentStream
from PyPDF2.generic import TextStringObject
from PyPDF2.utils import b_
import os.path
import requests
import logging
import sys
from io import StringIO

from ..exceptions import DownloadException
logger = logging.getLogger(__name__)


def get_pdf_content(path):
    # Load PDF into pyPDF
    pdf, stdout, stderr = capture(PdfFileReader, open(path, "rb"))
    if len(stderr) > 0:
        logger.warning(stderr[:-1])

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


def download(url, local_filename, override=False):
    if os.path.exists(local_filename):
        if override:
            os.unlink(local_filename)
        else:
            # Skipping already downloaded file...
            logger.info("Skipping download of existing file {0}"
                        .format(local_filename))
            return
    req = requests.get(url)
    if not req.ok:
        raise DownloadException('Failed to download %s' % url)

    with open(local_filename, 'wb') as target:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                target.write(chunk)
    logger.info("Downloaded file {0}"
                .format(local_filename))


def capture(f, *args, **kwargs):
    real_stdout = sys.stdout
    real_stderr = sys.stderr
    try:
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        result = f(*args, **kwargs)
        stdout = sys.stdout.getvalue()
        stderr = sys.stderr.getvalue()
    finally:
        # close the stream and restore original stdout/stderrerr
        sys.stdout.close()
        sys.stdout = real_stdout
        sys.stderr = real_stderr

    return (result, stdout, stderr)
