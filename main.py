# pylint: disable=too-few-public-methods
# pylint: disable=line-too-long
import os
from bs4 import BeautifulSoup
import requests
import openai

NOTION_BASE_URL = "https://www.notion.so"
openai.api_key = os.getenv("OPENAI_API_KEY")

def invoke_LLM(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error invoking ChatGPT API: {str(e)}"

# page objects will follow this schema:

class HelpPage:
    def __init__(self, title, href, sub_articles):
        self.title = title
        self.href = href
        self.sub_articles = sub_articles
        
class HelpArticle:
    def __init__(self, title, href, content):
        self.title = title
        self.href = href
        self.content = content

class NotionExtracter:

    def __init__(self, main_url):
        self.main_url = main_url
        self.page_objects = []

    # ----------------------------------  SUB-PAGES  -----------------------------------------------------

    # extract the sub-pages from the main page
    def extract_sub_pages(self, soup):
        
        # sub-pages live in elements that look like: <a class="helpCenterArticleGrid_titleLink__hTrdL">
        sub_page_class = 'helpCenterArticleGrid_titleLink__hTrdL'
        sub_page_links = soup.find_all('a', class_=sub_page_class)
        for link in sub_page_links:
            self.page_objects.append(
                HelpPage(
                    title=link.text,
                    href=link.get('href'),
                    sub_articles=[] # to be populated with help-articles
                )
            )

    # -------------------------------  SUB-ARTICLES (within sub-pages)  ---------------------------------

    # extract the help-articles from each sub-page
    def extract_sub_articles(self, soup, sub_articles):
        # sub-articles live in <a> elements that are children of <article> elements that look like:
        # <article class="helpCenterContentPreview_articlePreview__Epc1O article-preview-condensed">
        article_class = 'helpCenterContentPreview_articlePreview__Epc1O article-preview-condensed'
        articles = soup.find_all('article', class_=article_class)
        
        for article in articles:
            link = article.find('a')
            if link:
                sub_articles.append(
                    HelpArticle(
                        title=link.get('title'),
                        href=link.get('href'),
                        content=None # to be populated with content later
                    )
                )

        return sub_articles


    # ----------------------------------  CONTENT EXTRACTION  --------------------------------------------

    # extract the content from a leaf article (help page)
    # specifically include all titles, notes, and paragraphs
    def extract_content(self, href):
        response = requests.get(f"{NOTION_BASE_URL}{href}", timeout=10000)
        soup = BeautifulSoup(response.content, "html.parser")
        content = []

        
        # Find the element with the specific class
        content_element = soup.find(class_="contentfulRichText_richText__rW7Oq contentfulRichText_sans__UVbfz")

        prompt = f"""
            Please extract and organize the content from this article into coherent sections.
            Follow these guidelines:
            1. Keep headings with their associated paragraphs
            2. Keep bulleted/numbered lists intact - do not split them
            3. Each section should be approximately 750 characters, but can exceed this if needed to preserve context
            4. Maintain the hierarchical structure and relationships between elements
            5. Preserve any code blocks, tables, or special formatting as complete units
            6. Return the content as an array of logically grouped text sections. Nothing else, no text, just the array.
            7. The topic of the article is: {href}
            Here is the content:
            {content_element.prettify()}
        """
        try:
            res = invoke_LLM(prompt)
            if res:
                return res
        except Exception as e:
            print(f"Error invoking LLM: {e}")

        # if LLM fails, manually extract as fallback
        content = []
        list_items = content_element.find_all('li', class_='contentfulRichText_listItem___Swmu')
        for item in list_items:
            # Find the paragraph within the list item
            paragraph = item.find('p', class_='contentfulRichText_paragraph___hjRE')
            if paragraph:
                # Clean and add the text
                text = paragraph.get_text().strip()
                if text:
                    content.append(f"• {text}")
        
        # Find standalone paragraphs (not within lists)
        paragraphs = soup.find_all('p', class_='contentfulRichText_paragraph___hjRE', recursive=False)
        for para in paragraphs:
            text = para.get_text().strip()
            if text:
                content.append(text)
        
        return "\n".join(content)
    
    # ----------------------------------  PRINTING  ------------------------------------------------------

    def print_extracted_resources(self, pages):
        for article in pages:
            print(f"Title: {article.title}, href: {article.href}")
            
    # ----------------------------------  Bonus: prettify with LLM  ---------------------------------------
    
    def prettify_output_LLM(self, sub_article_title, sub_article_content):
        prompt = f"""
            You are a technical writer helping to format and structure help documentation.
            I will provide you with content from a help article titled '{sub_article_title}'. 
            The content consists of paragraphs and list items. Please format this content to be clear, concise and well-structured while preserving the key information.

            Here is the content:
            {sub_article_content}

            Please rewrite this content to be more polished and professional while maintaining accuracy.
        """
        try:
            res = invoke_LLM(prompt)
            if res:
                return res
        except Exception as e:
            print(f"Error invoking LLM: {e}")
        
        
    # --------------------------------------  MAIN  ------------------------------------------------------

    # extract the sub-pages from the main page
                
    def run(self):
        # -------------------- get the pages from top level ---------------------
        response = requests.get(self.main_url, timeout=10000)
        soup = BeautifulSoup(response.content, "html.parser")
        input(f"Press Enter to extract articles from {self.main_url} ")

        # self.page_objects will contain sub-pages and sub-articles, and their contents
        self.extract_sub_pages(soup)
        
        # if input(f"Found {len(self.page_objects)} sub-pages, each containing multiple articles.\nPrint the sub-pages? (y/n): ") == "y":
        self.print_extracted_resources(self.page_objects)    
        print('-' * 30)
            
        # -------------------- get the sub-pages from each page --------------------
        for sub_page in self.page_objects:
            print(f"\nExtracting sub-articles for '{sub_page.title}':")
            # extract the sub-articles from the sub-page, and populate the page_objects
            sub_page_response = requests.get(f"{NOTION_BASE_URL}{sub_page.href}", timeout=10000)
            sub_page_soup = BeautifulSoup(sub_page_response.content, "html.parser")
            self.extract_sub_articles(sub_page_soup, sub_page.sub_articles)

            # if input(f"Found {len(sub_page.sub_articles)} help-articles for '{sub_page.title}'.\nPrint the help-articles? (y/n): ") == "y":
            self.print_extracted_resources(sub_page.sub_articles)
            print('-' * 30)
            
        prettified_content = list()
        
        # -------------------- print the content for each page ---------------------
        interactive_mode = input("Would you like to review each article individually? (y/n): ") == "y"
        
        for sub_page in self.page_objects:
            for sub_article in sub_page.sub_articles:
                if interactive_mode:
                    if input(f"From '{sub_page.title}', Help Article: {sub_article.title}, href: {sub_article.href}\nExtract the content? (y/n): ") == "y":
                        sub_article.content = self.extract_content(sub_article.href)
                        print(sub_article.content)
                        
                        if input("Prettify the content with LLM? (y/n): ") == "y":
                            prettified_content.append(
                                self.prettify_output_LLM(
                                    sub_article.title,
                                    sub_article.content
                                )
                            )
                            print(prettified_content[-1])
                            print(f"added processed content for {sub_article.title} to prettified_content")
                        else:
                            prettified_content.append(sub_article.content)
                            print(f"added raw content for {sub_article.title} to prettified_content")
                else:
                    sub_article.content = self.extract_content(sub_article.href)
                    prettified_content.append(
                        self.prettify_output_LLM(
                            sub_article.title,
                            sub_article.content
                        )
                    )
                    print(f"added processed content for '{sub_page.title}' -> '{sub_article.title}' to prettified_content")
            if interactive_mode:
                print('-' * 30)
            
        return prettified_content
            
if __name__ == "__main__":
    NotionExtracter = NotionExtracter(main_url=f"{NOTION_BASE_URL}/help/reference")
    NotionExtracter.run()
