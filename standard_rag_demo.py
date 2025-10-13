import os
import markdown
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# โหลด environment variables
load_dotenv()

# --- 1. การตั้งค่า ---
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 500))  # ขนาดของ chunk ที่จะตัด
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'loan_documents')
QDRANT_URL = os.getenv('QDRANT_URL', 'http://localhost:6333')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'paraphrase-multilingual-MiniLM-L12-v2')
DEFAULT_TOP_K = int(os.getenv('DEFAULT_TOP_K', 3))

# สร้างโฟลเดอร์สำหรับเก็บไฟล์ markdown และวางไฟล์ทั้ง 5 ไฟล์ไว้ที่นี่
LOAN_FILES_DIR = os.getenv('LOAN_FILES_DIR', 'loan_markdowns') 

# --- 2. การโหลดข้อมูลและตัดเป็น Chunk ---
def load_and_chunk_markdowns(directory):
    chunks = []
    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                # แบ่งข้อความตามขนาดที่กำหนด
                for i in range(0, len(text), CHUNK_SIZE):
                    chunks.append({
                        "source": filename,
                        "text": text[i:i + CHUNK_SIZE]
                    })
    return chunks

# --- 3. การสร้าง Embedding ---
def create_embeddings(chunks, model_name=None):
    if model_name is None:
        model_name = EMBEDDING_MODEL
    print("Creating embeddings...")
    model = SentenceTransformer(model_name)
    texts = [chunk['text'] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings

# --- 4. การเก็บข้อมูลลง Qdrant ---
def store_in_qdrant(chunks, embeddings):
    print("Storing in Qdrant...")
    client = QdrantClient(QDRANT_URL)
    
    # ลบ collection เก่าถ้ามี
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)
        
    # สร้าง collection ใหม่
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=embeddings.shape[1], distance=Distance.COSINE),
    )
    
    # เตรียมข้อมูลสำหรับนำเข้า
    points = [
        PointStruct(
            id=id,
            vector=embeddings[id],
            payload={"source": chunk["source"], "text": chunk["text"]}
        )
        for id, chunk in enumerate(chunks)
    ]
    
    # นำเข้าข้อมูล
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Stored {len(points)} points in Qdrant.")

# --- 5. การค้นหาข้อมูล ---
def search_qdrant(query, top_k=None):
    if top_k is None:
        top_k = DEFAULT_TOP_K
    print(f"\n--- Searching for: '{query}' ---")
    model = SentenceTransformer(EMBEDDING_MODEL)
    client = QdrantClient(QDRANT_URL)
    
    query_embedding = model.encode(query)
    
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=top_k
    )
    
    for i, result in enumerate(search_result):
        print(f"\nResult {i+1}:")
        print(f"Score: {result.score:.4f}")
        print(f"Source: {result.payload['source']}")
        print(f"Text: {result.payload['text'][:200]}...") # แสดงข้อความเพียง 200 ตัวอักษรแรก

# --- Main Execution ---
if __name__ == "__main__":
    # สร้างโฟลเดอร์และวางไฟล์ก่อนรัน
    if not os.path.exists(LOAN_FILES_DIR):
        os.makedirs(LOAN_FILES_DIR)
        print(f"Please put your 5 markdown files in the '{LOAN_FILES_DIR}' directory.")
    else:
        # chunks = load_and_chunk_markdowns(LOAN_FILES_DIR)
        # if not chunks:
        #     print("No markdown files found. Exiting.")
        # else:
            # embeddings = create_embeddings(chunks)
            # store_in_qdrant(chunks, embeddings)
            
            # --- ทดสอบการค้นหา ---
            # Query ที่น่าจะหาเจอ
            search_qdrant("วัตถุประสงค์ของสินเชื่อเพื่อบุคลากรด้านสาธารณสุข")
            print("="*50)
            # Query ที่เป็นปัญหา
            search_qdrant("ผมเป็นครู อยากกู้เงิน 100,000 บาท มีโครงการไหนแนะนำบ้าง")