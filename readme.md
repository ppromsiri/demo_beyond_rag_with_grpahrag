# Workshop and Demo
## Beyound RAG with GraphRAG



นี่คือแผนการสอน Workshop และโค้ดตัวอย่างสำหรับ "Beyond RAG with GraphRAG" โดยใช้ข้อมูลสินเชื่อ 5 ไฟล์ แบ่งเป็น 2 ส่วนหลักๆ คือ แผนการสอน (Workshop Plan) และโค้ดตัวอย่าง (Demo Code) พร้อมคำอธิบาย

---

## **แผนการสอน Workshop: Beyond RAG with GraphRAG**

**ชื่อ Workshop:** ค้นหาข้อมูลเชิงลึกเกินกว่าการค้นหาตามความหมาย: พบกับ GraphRAG

**ระยะเวลาที่แนะนำ:** 45 - 60 นาที

**วัตถุประสงค์:**
1.  เข้าใจข้อจำกัดของ RAG แบบดั้งเดิม (Naive RAG) ที่ใช้การแบ่งข้อความ (Chunking)
2.  เรียนรู้หลักการของ GraphRAG และวิธีการสร้าง Knowledge Graph จากเอกสาร
3.  เปรียบเทียบประสิทธิภาพการค้นหาระหว่าง Vector Search และ Graph Query
4. สามารถนำไปปรับใช้กับข้อมูลในองค์กรของตัวเองได้

---

### **โครงสร้างการสอน (Agenda)**

#### **ส่วนที่ 1: Introduction (5 นาที)**
*   **สวัสดีและแนะนำตัว:** ทำความรู้จักกันแบบสั้นๆ
*   **RAG คืออะไร?** ทบทวนแนวคิด Retrieval-Augmented Generation แบบคร่าวๆ คือการดึงข้อมูลมาเป็นบริบทให้ LLM
*   **ปัญหาของ RAG แบบเดิม (The "Chunking Problem"):**
    *   การตัดข้อความเป็นชิ้นเล็กๆ ทำให้สูญเสียบริบทระหว่างชิ้นส่วน (Loss of Context)
    *   การค้นหาแบบ Cosine Similarity มักจะหา "ข้อความที่คล้ายกัน" ไม่ใช่ "ความสัมพันธ์ที่แท้จริง"
    *   ตัวอย่าง: การค้นหา "สินเชื่อสำหรับครูที่ต้องการเงิน 100,000 บาท" อาจจะไปเจอสินเชื่อที่มีวงเงิน 100,000 บาท แต่ไม่ใช่สำหรับครู
*   **แนะนำ GraphRAG:** แนวคิดที่จะแก้ปัญหานี้โดยการแปลงข้อมูลให้เป็นกราฟของ "เอนทิตี (Entities)" และ "ความสัมพันธ์ (Relationships)"

#### **ส่วนที่ 2: Demo ที่ 1 - Standard RAG (The "Before") (15 นาที)**
*   **อธิบาย Flow:** โหลดไฟล์ Markdown -> ตัดข้อความเป็น Chunk (Fixed Size) -> Embedding -> เก็บใน Qdrant -> ค้นหาด้วย Cosine Similarity
*   **แสดงโค้ด Python:** แสดงโค้ดการทำงานทีละส่วน พร้อมอธิบาย
*   **แสดงผลลัพธ์ใน Qdrant:** แสดงให้เห็นว่าข้อมูลใน Vector DB เป็นอย่างไร (เป็น chunk ของข้อความ)
*   **ทดสอบการค้นหา (Querying):**
    *   **Query 1 (ดี):** `"สินเชื่อสำหรับกำนัน"` -> น่าจะเจอข้อมูลที่เกี่ยวข้องได้ดี
    *   **Query 2 (ปัญหา):** `"ผมเป็นครู อยากกู้เงิน 100,000 บาท มีโครงการไหนแนะนำบ้าง"`
        *   **ผลลัพธ์ที่คาดหวัง:** อาจจะเจอ `loan5.md` (สินเชื่อบุคลากรการศึกษา) แต่ดอกเบี้ยสูง หรือเจอ `loan1.md` (สินเชื่อ 100,000 บาท) แต่ไม่ใช่สำหรับครู ทำให้ LLM อาจตอบผิดได้
        *   **สรุปปัญหา:** แสดงให้เห็นว่า RAG ไม่เข้าใจ "Constraint" หลายๆ อย่างที่เชื่อมโยงกัน (เป็นครู + เงิน 100,000)

#### **ส่วนที่ 3: Demo ที่ 2 - GraphRAG (The "After") (20 นาที)**
*   **อธิบาย Flow:** โหลดไฟล์ Markdown -> ดึงเอนทิตี (ชื่อโครงการ, กลุ่มเป้าหมาย, วงเงิน, ดอกเบี้ย) และความสัมพันธ์ -> สร้าง Node และ Relation ใน Neo4j
*   **แสดงโค้ด Python:** แสดงโค้ดการแปลงข้อมูลเป็นกราฟ
*   **แสดงผลลัพธ์ใน Neo4j Browser:** เปิด Neo4j Browser ให้ผู้เรียนเห็นภาพรวมของกราฟ
    *   Node สีฟ้า: `LoanProject`
    *   Node สีเขียว: `Profession` (เช่น ครู, กำนัน)
    *   Node สีส้ม: `LoanLimit`
    *   เส้นเชื่อม: `IS_FOR`, `HAS_LIMIT` เป็นต้น
    *   **จุดเด่น:** ให้ผู้เรียนเห็นว่าข้อมูลมีความสัมพันธ์ชัดเจน
*   **ทดสอบการค้นหา (Querying):**
    *   **Query เดิม (แก้ปัญหา):** ใช้ Cypher Query หา "สินเชื่อสำหรับครูที่วงเงินสูงสุดไม่ต่ำกว่า 100,000 บาท"
        ```cypher
        MATCH (p:Profession {name: 'บุคลากรทางการศึกษา'})<-[:IS_FOR]-(l:LoanProject)-[:HAS_LIMIT]->(limit:LoanLimit)
        WHERE toInteger(replace(limit.value, ',', '')) >= 100000
        RETURN l.name, limit.value
        ```
        *   **ผลลัพธ์:** ไม่มีผลลัพธ์ (Empty result) ซึ่งเป็นคำตอบที่ **ถูกต้อง** เพราะสินเชื่อสำหรับครูมีวงเงินสูงสุดแค่ 20,000 บาท
    *   **Query ใหม่ (แสดงความสามารถ):** "โครงการไหนที่ต้องการค้ำประกันโดยคนในอำเภอเดียวกัน และดอกเบี้ยคงที่"
        ```cypher
        MATCH (l:LoanProject)-[:HAS_INTEREST_RATE]->(ir:InterestRate {type: 'คงที่'})
        WHERE l.collateral_condition CONTAINS 'อำเภอเดียวกัน'
        RETURN l.name, ir.value
        ```
        *   **ผลลัพธ์:** จะเจอเฉพาะโครงการสินเชื่อของกำนัน/ผู้ใหญ่บ้าน (`loan1.md`, `loan2.md`) ซึ่งตอบโจทย์ได้แม่นยำมาก

#### **ส่วนที่ 4: Conclusion & Q&A (5 นาที)**
*   **สรุป:**
    *   **RAG:** เหมาะกับการค้นหาข้อมูลตามความหมาย (Semantic Search) ในเอกสารขนาดใหญ่ๆ
    *   **GraphRAG:** เหมาะกับข้อมูลที่มี "เอนทิตี" และ "ความสัมพันธ์" ที่ซับซ้อน ต้องการคำตอบที่แม่นยำและตรงประเด็น
*   **เปิดรับคำถาม (Q&A)**

---

## **โค้ดตัวอย่างสำหรับ Demo (Demo Code)**

### **การเตรียมสภาพแวดล้อม (Prerequisites)**

1.  **ติดตั้ง Libraries:**
    ```bash
    pip install "qdrant-client[fastembed]" sentence-transformers neo4j markdown
    ```
2.  **ติดตั้งและรัน Docker:**
    *   **Qdrant:**
        ```bash
        docker run -p 6333:6333 qdrant/qdrant
        ```
    *   **Neo4j:**
        ```bash
        docker run \
            -p 7474:7474 -p 7687:7687 \
            -d \
            -v $HOME/neo4j/data:/data \
            -v $HOME/neo4j/logs:/logs \
            -v $HOME/neo4j/import:/var/lib/neo4j/import \
            -v $HOME/neo4j/plugins:/plugins \
            --name neo4j-apoc \
            -e NEO4J_AUTH=neo4j/password \
            -e NEO4J_PLUGINS=["apoc"] \
            neo4j:latest
        ```
        *   **Username:** `neo4j`
        *   **Password:** `password`
        *   **Neo4j Browser:** http://localhost:7474

---

### **Demo 1: Standard RAG with Qdrant**

สร้างไฟล์ `standard_rag_demo.py`

```python
import os
import markdown
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# --- 1. การตั้งค่า ---
CHUNK_SIZE = 500  # ขนาดของ chunk ที่จะตัด
COLLECTION_NAME = "loan_documents"

# สร้างโฟลเดอร์สำหรับเก็บไฟล์ markdown และวางไฟล์ทั้ง 5 ไฟล์ไว้ที่นี่
LOAN_FILES_DIR = "loan_markdowns" 

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
def create_embeddings(chunks, model_name='paraphrase-multilingual-MiniLM-L12-v2'):
    print("Creating embeddings...")
    model = SentenceTransformer(model_name)
    texts = [chunk['text'] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings

# --- 4. การเก็บข้อมูลลง Qdrant ---
def store_in_qdrant(chunks, embeddings):
    print("Storing in Qdrant...")
    client = QdrantClient("http://localhost:6333")
    
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
def search_qdrant(query, top_k=3):
    print(f"\n--- Searching for: '{query}' ---")
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    client = QdrantClient("http://localhost:6333")
    
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
        chunks = load_and_chunk_markdowns(LOAN_FILES_DIR)
        if not chunks:
            print("No markdown files found. Exiting.")
        else:
            embeddings = create_embeddings(chunks)
            store_in_qdrant(chunks, embeddings)
            
            # --- ทดสอบการค้นหา ---
            # Query ที่น่าจะหาเจอ
            search_qdrant("วัตถุประสงค์ของสินเชื่อเพื่อบุคลากรด้านสาธารณสุข")
            
            # Query ที่เป็นปัญหา
            search_qdrant("ผมเป็นครู อยากกู้เงิน 100,000 บาท มีโครงการไหนแนะนำบ้าง")
```

---

### **Demo 2: GraphRAG with Neo4j**

สร้างไฟล์ `graph_rag_demo.py`

```python
import os
import re
import markdown
from neo4j import GraphDatabase

# --- 1. การตั้งค่า ---
LOAN_FILES_DIR = "loan_markdowns" 
URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

# --- 2. การดึงเอนทิตีและความสัมพันธ์ (Simple Extraction) ---
def extract_info_from_md(text):
    info = {
        "name": "",
        "target_audiences": [],
        "loan_limit": "",
        "interest_rate": "",
        "collateral": "",
        "loan_term": ""
    }
    
    # ดึงชื่อโครงการจากหัวข้อแรก
    headers = re.findall(r'^#+\s*(.*)', text, re.MULTILINE)
    if headers:
        info["name"] = headers[0].strip()

    # ดึงกลุ่มเป้าหมาย (ใช้ keyword ธรรมดา)
    if "ครู" in text or "บุคลากรทางการศึกษา" in text:
        info["target_audiences"].append("บุคลากรทางการศึกษา")
    if "กำนัน" in text or "ผู้ใหญ่บ้าน" in text:
        info["target_audiences"].append("กำนัน/ผู้ใหญ่บ้าน")
    if "แพทย์ประจำตำบล" in text:
        info["target_audiences"].append("แพทย์ประจำตำบล")
    if "ผู้รับบำนาญ" in text:
        info["target_audiences"].append("ผู้รับบำนาญ")
    if "ข้าราชการ" in text and "เกษตร" in text:
        info["target_audiences"].append("ข้าราชการ (เพื่อเกษตร)")

    # ดึงข้อมูลอื่นๆ ด้วย Regex
    limit_match = re.search(r'วงเงินกู้.*?ไม่เกิน\s*([\d,]+)\s*บาท', text)
    if limit_match:
        info["loan_limit"] = limit_match.group(1)
        
    interest_match = re.search(r'อัตราดอกเบี้ย.*?([\d.]+)%\s*ต่อปี', text)
    if interest_match:
        info["interest_rate"] = interest_match.group(1)
        
    collateral_match = re.search(r'หลักประกัน.*?ใช้\s*(.*?)\s*เป็น', text, re.DOTALL)
    if collateral_match:
        info["collateral"] = collateral_match.group(1).strip()

    term_match = re.search(r'ระยะเวลาการกู้.*?ไม่เกิน\s*([\d\s]+)\s*(งวด|ปี|เดือน)', text)
    if term_match:
        info["loan_term"] = term_match.group(1).strip()
        
    return info

# --- 3. การสร้างกราฟใน Neo4j ---
def create_graph_in_neo4j(extracted_data):
    print("Creating graph in Neo4j...")
    driver = GraphDatabase.driver(URI, auth=AUTH)
    driver.verify_connectivity()
    
    with driver.session() as session:
        # ลบข้อมูลเก่าเพื่อความสะอาด
        session.run("MATCH (n) DETACH DELETE n")
        print("Cleared existing graph.")

        for data in extracted_data:
            project_name = data['name']
            source_file = data['source_file']
            
            # สร้าง Node หลัก (LoanProject)
            session.run(
                "MERGE (p:LoanProject {name: $name}) SET p.source_file = $source_file",
                name=project_name, source_file=source_file
            )
            
            # สร้างความสัมพันธ์กับกลุ่มเป้าหมาย
            for audience in data['target_audiences']:
                session.run(
                    """
                    MERGE (p:LoanProject {name: $project_name})
                    MERGE (a:Profession {name: $audience})
                    MERGE (p)-[:IS_FOR]->(a)
                    """,
                    project_name=project_name, audience=audience
                )
            
            # สร้างความสัมพันธ์กับวงเงิน
            if data['loan_limit']:
                session.run(
                    """
                    MERGE (p:LoanProject {name: $project_name})
                    MERGE (l:LoanLimit {value: $limit})
                    MERGE (p)-[:HAS_LIMIT]->(l)
                    """,
                    project_name=project_name, limit=data['loan_limit']
                )
            
            # สร้างความสัมพันธ์กับดอกเบี้ย
            if data['interest_rate']:
                session.run(
                    """
                    MERGE (p:LoanProject {name: $project_name})
                    MERGE (i:InterestRate {value: $rate})
                    MERGE (p)-[:HAS_INTEREST_RATE]->(i)
                    """,
                    project_name=project_name, rate=data['interest_rate']
                )
            
            # สร้างความสัมพันธ์กับหลักประกัน
            if data['collateral']:
                session.run(
                    """
                    MERGE (p:LoanProject {name: $project_name})
                    MERGE (c:Collateral {description: $collateral})
                    MERGE (p)-[:REQUIRES_COLLATERAL]->(c)
                    """,
                    project_name=project_name, collateral=data['collateral']
                )
            
            # สร้างความสัมพันธ์กับระยะเวลา
            if data['loan_term']:
                session.run(
                    """
                    MERGE (p:LoanProject {name: $project_name})
                    MERGE (t:LoanTerm {duration: $term})
                    MERGE (p)-[:HAS_TERM]->(t)
                    """,
                    project_name=project_name, term=data['loan_term']
                )
    print("Graph created successfully.")
    driver.close()

# --- 4. การค้นหาข้อมูลด้วย Cypher ---
def query_neo4j(cypher_query):
    print(f"\n--- Running Cypher Query: ---\n{cypher_query}\n")
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        result = session.run(cypher_query)
        for record in result:
            print(record)
    driver.close()

# --- Main Execution ---
if __name__ == "__main__":
    if not os.path.exists(LOAN_FILES_DIR):
        print(f"Please put your 5 markdown files in the '{LOAN_FILES_DIR}' directory.")
    else:
        all_data = []
        for filename in os.listdir(LOAN_FILES_DIR):
            if filename.endswith(".md"):
                filepath = os.path.join(LOAN_FILES_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
                    extracted = extract_info_from_md(text)
                    extracted['source_file'] = filename
                    all_data.append(extracted)
        
        if not all_data:
            print("No markdown files found. Exiting.")
        else:
            create_graph_in_neo4j(all_data)
            
            # --- ทดสอบการค้นหา ---
            # Query 1: หาสินเชื่อทั้งหมดสำหรับครู
            query1 = """
            MATCH (p:LoanProject)-[:IS_FOR]->(a:Profession {name: 'บุคลากรทางการศึกษา'})
            RETURN p.name AS ProjectName
            """
            query_neo4j(query1)

            # Query 2: หาสินเชื่อสำหรับครูที่วงเงิน >= 100,000 (ควรได้ผลลัพธ์ว่าง)
            query2 = """
            MATCH (p:LoanProject)-[:IS_FOR]->(a:Profession {name: 'บุคลากรทางการศึกษา'}),
                  (p)-[:HAS_LIMIT]->(l:LoanLimit)
            WHERE toInteger(replace(l.value, ',', '')) >= 100000
            RETURN p.name AS ProjectName, l.value AS Limit
            """
            query_neo4j(query2)
            
            # Query 3: หาสินเชื่อที่ดอกเบี้ยต่ำกว่า 9% และไม่ต้องใช้ที่ดินค้ำ
            query3 = """
            MATCH (p:LoanProject)-[:HAS_INTEREST_RATE]->(i:InterestRate),
                  (p)-[:REQUIRES_COLLATERAL]->(c:Collateral)
            WHERE toFloat(i.value) < 9.0 AND NOT c.description CONTAINS 'ที่ดิน'
            RETURN p.name AS ProjectName, i.value AS InterestRate, c.description AS Collateral
            """
            query_neo4j(query3)
```

### **คำแนะนำในการ Demo**

1.  **เริ่มจาก Standard RAG:** รัน `standard_rag_demo.py` ก่อน แสดงให้เห็นว่ามันทำงานอย่างไร และผลลัพธ์ของ Query ที่เป็นปัญหาเป็นอย่างไร ให้ผู้เรียนรู้สึก "อืม... มันไม่ตรงประเด็นพอดี"
2.  **เปลี่ยนมาเป็น GraphRAG:** รัน `graph_rag_demo.py` หลังจากนั้นให้เปิด Neo4j Browser (http://localhost:7474) และรันคำสั่ง `MATCH (n) RETURN n` เพื่อแสดงกราฟทั้งหมด ให้ผู้เรียนชมความสวยงามและความชัดเจนของความสัมพันธ์
3.  **ทดสอบ Query:** รัน Cypher Query ที่เตรียมไว้ในสคริปต์ หรือพิมพ์ใน Neo4j Browser แบบ real-time เพื่อตอบคำถามเดิมๆ และให้เห็นว่าคำตอบแม่นยำกว่าเดิมมาก

หวังว่าแผนการและโค้ดเหล่านี้จะเป็นประโยชน์ในการจัด Workshop ของคุณนะครับ! ขอให้สนุกครับ