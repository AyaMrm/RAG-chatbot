import PyPDF2
from pathlib import Path
from typing import List, Dict, Union
import logging

logger = logging.getLogger(__name__)

class PDFProcessor: 
    def __init__(self):
        self.supported_extensions = ['.pdf']
        
    def extract_text(self, path: Union[str, Path]) -> str : 
        
        pdf_path = Path(path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"File {pdf_path} doesn't exist!")
        
        if pdf_path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {pdf_path.suffix}.")
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                if len(reader.pages)== 0 :
                    logger.warning(f"No pages found in PDF: {pdf_path}")
                    return ""
                
                text_parts = []
                for num, page in enumerate(reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            cleaned = self.clean_text(page_text)
                            text_parts.append(cleaned)
                        else:
                            logger.debug(f"Page {num} has no extractable text")
                    except Exception as e:
                        logger.error(f"Error extracting pages {num}: {e}")
                        continue
                return ' '.join(text_parts)
        except PyPDF2.errors.PdfReadError as e :
            raise ValueError(f"Corrupted or invalid PDF {pdf_path} : {e}") 
        except Exception as e :
            raise RuntimeError(f"Unexpected error processing PDF {pdf_path} : {e}")
                
    
    def extract_text_with_pages(self, path: Union[str, Path]) -> List[Dict]:
        path = Path(path)
        pages = []
        
        try:
            with open(path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for i, page in enumerate(reader.pages, 1):
                    raw_text = page.extract_text() or ""
                    cleaned = self.clean_text(raw_text)
                    pages.append({
                        'num': i,
                        'text': cleaned,
                        'char_count':len(cleaned),
                        'word_count': len(cleaned.split()),
                        'has_text': bool(cleaned.strip())
                    })
            return pages
        except Exception as e :
            logger.error(f"Failed to extract pages from {path}: {e}")
            raise
        
    def clean_text(self, text:str) -> str :
        if not text:
            return ""
        
        text = ' '.join(text.split())
        
        text = text.replace('\x00', '')
        return text.strip()
    
    def get_metadata(self, path: Union[str, Path]) -> Dict:
        path = Path(path)
        try:
            with open(path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                metadata = reader.metadata or {}
                return {
                    'nb_pages': len(reader.pages),
                    'author': metadata.get('/Author', ''),
                    'title': metadata.get('/Title', ''),
                    'subject': metadata.get('/Subject', ''),
                    'creator': metadata.get('/Creator', ''),
                    'producer': metadata.get('/Producer', '')
                }
        except Exception as e :
            logger.warning(f"Failed to extract metadata from {path}: {e}")
            return {'nb_pages': 0 }
        