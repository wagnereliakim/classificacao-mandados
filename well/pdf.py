from email.policy import strict
import logging
import os
import re
import urllib.request
import urllib.parse
import pdfplumber
from PyPDF2 import PdfFileReader, PdfFileWriter


def remove_CMS(path):
    path_split = path.split('.')
    p7z_extension = 'p7z'
    pdf_extension = 'pdf'
    path_name = path_split[0]
    path_extension = path_split[1]
    path_as_pdf = f'{path_name}.{pdf_extension}'

    has_pdf = os.path.exists(path_as_pdf) and os.path.isfile(path_as_pdf) and os.path.getsize(path_as_pdf) > 0
    if (not has_pdf and p7z_extension == path_extension):
        url = 'http://localhost:8080/arquivos?path=' + urllib.parse.quote_plus(path)
        response = urllib.request.urlopen(url)
        with open(path_as_pdf, 'wb') as out_file:
            data = response.read() # a `bytes` object
            out_file.write(data)
        out_file.close()

    return path_as_pdf

def extrair_with_plumber(path):
    text = ''
    try:
        file_name = remove_CMS(path)

        pdf = pdfplumber.open(file_name)
        for (index, page) in enumerate(pdf.pages):
            page_width = page.width
            page_height = page.height

            crop_coords = [10, 151, 10, 10]
            header_bbox = (crop_coords[0], crop_coords[1], page_width - crop_coords[2], page_height - crop_coords[3])
            negative_margins = list(filter(lambda x: x < 0, header_bbox))
            
            page_crop = page.crop(bbox=header_bbox) if index == 0 and len(negative_margins) == 0 else page
            text = text + ' ' + page_crop.extract_text()

        pdf.close()
    except Exception:
        logging.exception(f'Erro ao extrair texto do PDF {path}')
    return text

def extrair_with_pypdf(path, remove_header=True):
    text = ''    
    file_name = remove_CMS(path)

    # obtain PdfFileReader object 
    # pdfFileReader = PdfFileReader(path) # Or this way ：pdfFileReader = PdfFileReader(open(readFile, 'rb'))
    pdfFileReader = PdfFileReader(file_name, strict=False)

    # obtain PDF The document information of the file 
    documentInfo = pdfFileReader.getDocumentInfo()
    logging.debug('documentInfo = %s' % documentInfo)
    # Get page layout 
    pageLayout = pdfFileReader.getPageLayout()
    logging.debug('pageLayout = %s ' % pageLayout)
    # Get page mode 
    pageMode = pdfFileReader.getPageMode()
    logging.debug('pageMode = %s' % pageMode)
    xmpMetadata = pdfFileReader.getXmpMetadata()
    logging.debug('xmpMetadata = %s ' % xmpMetadata)

    if (remove_header):
        pdfFileReader = crop_out_header(pdfFileReader)

    # obtain pdf Number of pages 
    pageCount = pdfFileReader.getNumPages()
    
    for index in range(0, pageCount):
        # Returns... For the specified page number pageObject
        page_data = pdfFileReader.getPage(index)
        text = text + page_data.extract_text()

        logging.debug('pageCount = %s' % pageCount)
        logging.debug('index = %d , pageObj = %s' % (index, type(page_data))) # <class 'PyPDF2.pdf.PageObject'>
        # obtain pageObject stay PDF Page number in the document 
        pageNumber = pdfFileReader.getPageNumber(page_data)
        logging.debug('pageNumber = %s ' % pageNumber)

    return text

def crop_out_header(texto):
    # pattern = r'(?s)(?=PODER JUDIC)(.*[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)(.*)'
    pattern = r'(?s)(?=PODER JUDIC)((.*Processo\.?)|(.*Proc\.?))(.*)'
    compiled_pattern = re.compile(pattern, flags=re.M)

    groups_texto = re.search(compiled_pattern, texto).groups()

    if len(groups_texto) == 1:
        texto = groups_texto[0]
    else:
        texto = groups_texto[1]

    return texto


def extrair_texto(path, lib='pypdf'):
    if (os.path.exists(path) and os.path.isfile(path) and os.path.getsize(path) > 0):
        if (lib == 'pypdf'):
            return extrair_with_pypdf(path)
        else:
            return extrair_with_plumber(path)
    else:
        return ''

