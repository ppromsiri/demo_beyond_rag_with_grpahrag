import os
import re
import markdown
from dotenv import load_dotenv
from neo4j import GraphDatabase

# โหลด environment variables
load_dotenv()

# --- 1. การตั้งค่า ---
LOAN_FILES_DIR = os.getenv('LOAN_FILES_DIR', 'loan_markdowns')
URI = os.getenv('NEO4J_URI', 'neo4j://localhost:7687')
AUTH = (os.getenv('NEO4J_USERNAME', 'neo4j'), os.getenv('NEO4J_PASSWORD', 'password'))

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