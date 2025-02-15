import requests
from bs4 import BeautifulSoup
import os
import time
import pandas as pd
import re
from lxml import html

class NDSSSpider:
    def __init__(self, year):
        self.base_url = f"https://www.ndss-symposium.org/ndss{year}/accepted-papers/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.output_dir = os.path.dirname(os.path.abspath(__file__))
        self.papers_dir = os.path.join(self.output_dir, f"ndss{year}", "papers")
        self.slides_dir = os.path.join(self.output_dir, f"ndss{year}", "slides")
        
    def create_dirs(self):
        """Create output directories if they don't exist"""
        # Create parent directory first
        os.makedirs(self.output_dir, exist_ok=True)
        # Then create subdirectories
        os.makedirs(self.papers_dir, exist_ok=True)
        os.makedirs(self.slides_dir, exist_ok=True)

    def sanitize_filename(self, filename):
        """Sanitize filename to be safe for all operating systems"""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
            
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        
        # Truncate if too long (max 255 chars including extension)
        max_length = 250  # Leave room for extension
        if len(filename) > max_length:
            filename = filename[:max_length]
            
        return filename.strip('._')  # Remove leading/trailing dots and underscores
    
    def get_paper_list(self):
        """Get list of all papers from main page"""
        response = requests.get(self.base_url, headers=self.headers)
        print(f"Response status code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        papers = []
        
        # Find all paper divs across all sections (Summer Cycle and Fall Cycle)
        paper_divs = soup.find_all('div', class_='tag-box')
        
        if not paper_divs:
            print("Could not find any papers")
            return []
        
        for div in paper_divs:
            paper = {}
            
            # Get title
            title_elem = div.find('h3', class_='blog-post-title')
            if title_elem:
                paper['title'] = title_elem.text.strip()
            
            # Get authors
            authors_elem = div.find('p')
            if authors_elem:
                paper['authors'] = authors_elem.text.strip()
                
            # Get details URL
            link_elem = div.find('a', class_='paper-link-abs')
            if link_elem:
                paper['details_url'] = link_elem['href']
                
            # Get paper cycle (Summer/Fall)
            cycle = "Unknown Cycle"
            cycle_header = div.find_previous('h2')
            if cycle_header:
                if "Summer" in cycle_header.text:
                    cycle = "Summer Cycle"
                elif "Fall" in cycle_header.text:
                    cycle = "Fall Cycle"
            paper['cycle'] = cycle
            
            if paper:
                papers.append(paper)
                print(f"Found paper: {paper['title']} ({cycle})")
                
        print(f"\nTotal papers collected: {len(papers)}")
        print(f"Summer Cycle: {sum(1 for p in papers if p['cycle'] == 'Summer Cycle')}")
        print(f"Fall Cycle: {sum(1 for p in papers if p['cycle'] == 'Fall Cycle')}")
        return papers
    
    def download_file(self, url, filepath):
        """Download a file from url with proper error handling"""
        try:
            # Check if file already exists
            if os.path.exists(filepath):
                print(f"File already exists")
                return True
            
            response = requests.get(url, headers=self.headers, stream=True)
            if response.status_code == 200:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"Successfully downloaded")
                return True
            else:
                print(f"Failed to download {url}: Status code {response.status_code}")
        except Exception as e:
            print(f"Error downloading {url}: {str(e)}")
        return False

    def get_paper_details(self, paper):
        """Get paper PDF and slides from details page"""
        try:
            response = requests.get(paper['details_url'], headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get paper title from details page
            title_elem = soup.find('h1', class_='entry-title')
            if title_elem:
                paper_title = title_elem.text.strip()
                # Update the paper title in the dictionary with the full title
                paper['title'] = paper_title
            else:
                paper_title = paper['title']
            
            # Find paper buttons div
            paper_buttons = soup.find('div', class_='paper-buttons')
            if not paper_buttons:
                print(f"No download buttons found for {paper_title}")
                return
                
            # Find all button groups
            button_groups = paper_buttons.find_all('div', class_='btn-group-vertical')
            
            # Create safe filename from paper title
            safe_title = self.sanitize_filename(paper_title)
            
            files_downloaded = False
            for group in button_groups:
                button = group.find('a', class_='btn')
                if not button:
                    continue
                    
                if 'Paper' in button.text:
                    pdf_url = button['href']
                    filename = os.path.join(self.papers_dir, f"{safe_title}.pdf")
                    if self.download_file(pdf_url, filename):
                        files_downloaded = True
                        print(f"Paper processed: {paper_title}")
                        
                elif 'Slides' in button.text:
                    slides_url = button['href']
                    filename = os.path.join(self.slides_dir, f"{safe_title}.pdf")
                    if self.download_file(slides_url, filename):
                        files_downloaded = True
                        print(f"Slides processed: {paper_title}")
            
            if not files_downloaded:
                print(f"No new files downloaded for: {paper_title}")
                    
        except Exception as e:
            print(f"Error getting paper details for {paper_title}: {str(e)}")

    def save_paper_list_to_csv(self, papers):
        """Save paper list to CSV file"""
        csv_path = os.path.join(self.output_dir, "ndss2024", "paper_list.csv")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        
        try:
            df = pd.DataFrame(papers)
            # Add index column starting from 1
            df.insert(0, 'index', range(1, len(df) + 1))
            
            # Define CSV columns order
            columns = ['index', 'title', 'authors', 'cycle', 'details_url']
            # Reorder columns if they exist in the DataFrame
            df = df[[col for col in columns if col in df.columns]]
            
            df.to_csv(csv_path, index=False, encoding='utf-8')
            print(f"\nPaper list saved to: {csv_path}")
        except Exception as e:
            print(f"Error saving paper list to CSV: {str(e)}")

    def run(self):
        """Main function to run the spider"""
        print("Creating directories...")
        self.create_dirs()
        
        print("Getting paper list...")
        papers = self.get_paper_list()
        
        print(f"Found {len(papers)} papers")
        for i, paper in enumerate(papers, 1):
            print(f"\nProcessing {i}/{len(papers)}: {paper['title']}")
            self.get_paper_details(paper)
        
        # Save paper list to CSV after all papers are processed
        # This ensures we have the full titles
        self.save_paper_list_to_csv(papers)
        
        print("\nSpider completed!")

def extract_paper_titles(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 找到所有论文标题
    titles = []
    for paper in soup.find_all('div', class_='tag-box rel-paper'):
        title = paper.find('h3', class_='blog-post-title').text.strip()
        titles.append(title)
    
    # 转换为DataFrame并保存
    # df = pd.DataFrame(titles, columns=['title'])
    # df.to_csv('ndss2024_titles.csv', index=False, encoding='utf-8')
    
    return titles

if __name__ == "__main__":
    year = input("Please input the year you want to crawl: ")
    spider = NDSSSpider(year)
    spider.run()
