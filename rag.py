import os
import json
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

class NewsRAG:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.db_directory = "chroma_db"
        self.vector_store = None
        self.retrieval_chain = None

    # Loads articles from JSON file and converts to documents
    def load_articles(self, json_path):
       
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            
            documents = []
            for article in articles:
                content = f"TITLE: {article['title']}\n\n"
                content += f"SOURCE: {article['source']}\n"
                content += f"DATE: {article['date']}\n"
                content += f"URL: {article['url']}\n\n"
                content += f"CONTENT: {article['content']}"
                
                metadata = {
                    "title": article['title'],
                    "source": article['source'],
                    "url": article['url'],
                    "date": article['date']
                }
                
                documents.append(Document(page_content=content, metadata=metadata))
            
            print(f"Loaded {len(documents)} articles")
            return documents
        except Exception as e:
            print(f"Error loading articles: {str(e)}")
            return []

    # Splits documents and creates vector store
    def process_documents(self, documents):
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200
        )
        
        splits = text_splitter.split_documents(documents)
        print(f"Split into {len(splits)} chunks")
       
        self.vector_store = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.db_directory
        )
        
        print(f"Vector store created with {len(splits)} chunks")
        self.vector_store.persist()
        
        
        self.setup_retrieval_chain()

    # Finds the latest news JSON file in the data directory   
    def find_latest_news_file(self):
        data_dir = "data"
        if not os.path.exists(data_dir):
            return None
            
        files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) 
                if f.startswith("news_articles_") and f.endswith(".json")]
        
        if not files:
            return None
            
        return max(files, key=os.path.getctime)
    
    # Sets up the retrieval chain for answering questions
    def setup_retrieval_chain(self):
        prompt = ChatPromptTemplate.from_template("""
        You are a helpful assistant specialized in providing information about news from Bangladesh.
        Answer the user's question based on the news articles provided in the context.
        
        If the context doesn't contain relevant information to answer the question,
        politely say that you don't have enough information from recent news to answer.
        
        Always cite your sources by mentioning the news source and providing the URL when available.
        
        Context:
        {context}
        
        Question: {input}
        """)
        
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
        
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        document_chain = create_stuff_documents_chain(llm, prompt)
        self.retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
    def query(self, question):
        if not self.retrieval_chain:
            latest_file = self.find_latest_news_file()
            if latest_file:
                documents = self.load_articles(latest_file)
                self.process_documents(documents)
            else:
                return {"answer": "No news articles have been loaded yet. Please run the scraper first."}
        
        try:
            response = self.retrieval_chain.invoke({"input": question})
            return response
        except Exception as e:
            return {"answer": f"Error processing your question: {str(e)}"}
    
    def refresh_news(self):
        from scrape import scrape_all_news
        
        # Scrape fresh news
        latest_file = scrape_all_news()
        
        if latest_file:
            documents = self.load_articles(latest_file)
            self.process_documents(documents)
            return f"Successfully refreshed news database with {len(documents)} articles"
        else:
            return "Failed to refresh news. No articles were scraped."

# Initialize the RAG system
def initialize_rag():
    rag = NewsRAG()

    latest_file = rag.find_latest_news_file()
    if latest_file:
        documents = rag.load_articles(latest_file)
        rag.process_documents(documents)
    
    return rag

if __name__ == "__main__":
    rag = initialize_rag()
    
    if not rag.retrieval_chain:
        print("No news data found. Scraping fresh news...")
        rag.refresh_news()
    
    while True:
        question = input("Enter your question (or 'exit' to quit): ")
        if question.lower() == 'exit':
            break
        print(f"Question: {question}")
        response = rag.query(question)
        print(f"Answer: {response['answer']}")