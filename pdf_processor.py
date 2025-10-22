"""
PDF processing utilities for BinkRead application.
"""

import os
import logging
from typing import List, Optional
import fitz
from transformers import pipeline, AutoTokenizer

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles PDF text extraction and processing."""
    
    def __init__(self, model_name: str = 'facebook/bart-large-cnn'):
        """Initialize the PDF processor with AI model."""
        self.model_name = model_name
        self.summarizer = None
        self.tokenizer = None
        self._load_models()
    
    def _load_models(self):
        """Load the summarization model and tokenizer."""
        try:
            logger.info(f"Loading {self.model_name} model...")
            self.summarizer = pipeline("summarization", model=self.model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            logger.info("Models loaded successfully")
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            pdf_document = fitz.open(file_path)
            text = ""
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text += page.get_text()
            
            pdf_document.close()
            
            # Clean and format the text
            text = self._clean_and_format_text(text)
            return text.strip()
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def _clean_and_format_text(self, text: str) -> str:
        """Clean and format extracted text for better readability."""
        import re
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove excessive whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common PDF extraction issues
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between camelCase
        text = re.sub(r'(\d+)([A-Za-z])', r'\1 \2', text)  # Add space between numbers and letters
        
        # Clean up punctuation
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)  # Remove spaces before punctuation
        text = re.sub(r'([,.!?;:])\s*([,.!?;:])', r'\1 \2', text)  # Fix double punctuation
        
        # Structure academic content better
        text = self._structure_academic_content(text)
        
        return text.strip()
    
    def _structure_academic_content(self, text: str) -> str:
        """Structure academic content for better readability."""
        import re
        
        # Identify and format course information
        course_patterns = [
            (r'(\d+[A-Z]{2}\d+)\s+([A-Z\s]+)', r'\n\n**\1 \2**\n'),  # Course codes
            (r'(Teaching Scheme|Examination Scheme|Prerequisites|Course Objectives)', r'\n\n### \1\n'),
            (r'(Lectures|Tutorial|Credit|In Semester|End Semester)', r'\n- **\1:**'),
            (r'(\d+)\s+(Hrs/Week|Marks)', r' \1 \2'),
        ]
        
        for pattern, replacement in course_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Format book references
        text = re.sub(r'([A-Z]\.[A-Z]\.\s+[A-Z][a-z]+,\s+[^,]+,\s*"[^"]+",\s*\d+)', 
                     r'\n\n**Reference:** \1\n', text)
        
        # Format tutorial lists
        text = re.sub(r'(\d+\.\s+[A-Z][^.]*\.)', r'\n- \1', text)
        
        # Separate unrelated content (like the music group text)
        # Look for content that doesn't match academic patterns
        sentences = text.split('. ')
        academic_sentences = []
        other_sentences = []
        
        for sentence in sentences:
            # Check if sentence contains academic keywords
            academic_keywords = ['course', 'teaching', 'examination', 'prerequisites', 'objectives', 
                               'lectures', 'tutorial', 'credit', 'marks', 'scheme', 'theory', 
                               'computation', 'mathematical', 'formal', 'language', 'machine']
            
            if any(keyword.lower() in sentence.lower() for keyword in academic_keywords):
                academic_sentences.append(sentence)
            else:
                other_sentences.append(sentence)
        
        # Reconstruct text with better separation
        if academic_sentences and other_sentences:
            academic_text = '. '.join(academic_sentences)
            other_text = '. '.join(other_sentences)
            text = f"{academic_text}\n\n---\n\n**Additional Content:**\n{other_text}"
        
        # Clean up multiple newlines
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        return text
    
    def split_text_into_chunks(self, text: str, chunk_size: int = 4000) -> List[str]:
        """Split text into chunks at word boundaries."""
        chunks = []
        start = 0
        
        while start < len(text):
            chunk = text[start:start + chunk_size]
            last_space_index = chunk.rfind(" ")
            
            if last_space_index == -1:
                last_space_index = chunk_size
            
            chunk_text = text[start:start + last_space_index]
            chunks.append(chunk_text)
            start += last_space_index + 1
        
        return chunks
    
    def summarize_text(self, text: str, max_length: int = 300, min_length: int = 100) -> str:
        """Summarize text using the BART model."""
        if not self.summarizer or not self.tokenizer:
            raise ValueError("Models not loaded")
        
        chunks = self.split_text_into_chunks(text)
        complete_summary = ""
        
        for i, chunk in enumerate(chunks):
            try:
                # Check token limit
                if len(self.tokenizer.encode(chunk)) > 1024:
                    logger.warning(f"Skipping chunk {i+1} - exceeds token limit")
                    continue
                
                # Summarize chunk
                summary = self.summarizer(
                    chunk, 
                    max_length=max_length, 
                    min_length=min_length
                )
                
                complete_summary += summary[0]['summary_text'] + "\n\n"
                logger.info(f"Processed chunk {i+1}/{len(chunks)}")
                
            except Exception as e:
                logger.error(f"Error processing chunk {i+1}: {e}")
                continue
        
        return complete_summary.strip()
    
    def process_pdf(self, file_path: str) -> str:
        """Complete PDF processing pipeline."""
        try:
            # Extract text
            logger.info("Extracting text from PDF...")
            pdf_text = self.extract_text(file_path)
            
            if not pdf_text.strip():
                raise ValueError("No text found in PDF")
            
            # Summarize text
            logger.info("Summarizing text...")
            summary = self.summarize_text(pdf_text)
            
            if not summary.strip():
                raise ValueError("Unable to generate summary")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise
