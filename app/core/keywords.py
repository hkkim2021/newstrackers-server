NEWS_KEYWORDS = {
    # IT 일반
    "IT_general": [
        "IT", "정보기술", "기술", "테크", "소프트웨어", "하드웨어",
        "디지털", "온라인", "플랫폼", "서비스", "솔루션",
        "스타트업", "벤처", "유니콘", "테크기업", "IT기업",
    ],
    
    # 채용/인사
    "job": [
        "채용", "구인", "모집", "신입", "경력", "인턴", "취업", "이직",
        "개발자", "엔지니어", "프로그래머", "연봉", "복지", "재택근무",
        "면접", "코딩테스트", "포트폴리오", "이력서", "자소서",
    ],
    
    # 백엔드
    "backend": [
        "백엔드", "서버", "Server", "Backend", "API", "REST", "GraphQL",
        "Spring", "Spring Boot", "Django", "FastAPI", "Flask", "Express",
        "Node.js", "NestJS", "Laravel", "Ruby on Rails",
        "Java", "Python", "Go", "Golang", "Kotlin", "Rust", "C#", ".NET",
        "MSA", "마이크로서비스", "모놀리식", "아키텍처",
    ],
    
    # 프론트엔드
    "frontend": [
        "프론트엔드", "프론트", "Frontend", "클라이언트",
        "React", "Vue", "Vue.js", "Angular", "Svelte",
        "Next.js", "Nuxt", "Gatsby", "Remix",
        "JavaScript", "TypeScript", "HTML", "CSS", "SASS", "Tailwind",
        "웹팩", "Webpack", "Vite", "번들러", "SPA", "SSR", "SSG",
    ],
    
    # 모바일
    "mobile": [
        "모바일", "앱개발", "Android", "안드로이드", "iOS", "아이폰",
        "React Native", "Flutter", "Swift", "Kotlin", "SwiftUI",
        "Jetpack Compose", "앱스토어", "플레이스토어",
    ],
    
    # 데이터베이스
    "database": [
        "데이터베이스", "DB", "DBMS", "SQL", "NoSQL",
        "PostgreSQL", "MySQL", "MariaDB", "Oracle", "MSSQL",
        "MongoDB", "Redis", "Elasticsearch", "DynamoDB",
        "Cassandra", "Neo4j", "InfluxDB", "TimescaleDB",
    ],
    
    # 클라우드/인프라
    "cloud_infra": [
        "클라우드", "Cloud", "AWS", "Azure", "GCP", "Google Cloud",
        "NCP", "Naver Cloud", "KT Cloud", "IDC", "서버리스",
        "EC2", "S3", "Lambda", "RDS", "CloudFront",
        "VM", "가상화", "컨테이너", "온프레미스",
    ],
    
    # DevOps/CI/CD
    "devops": [
        "DevOps", "데브옵스", "SRE", "CI/CD", "파이프라인",
        "Docker", "Kubernetes", "K8s", "쿠버네티스", "Helm",
        "Jenkins", "GitHub Actions", "GitLab CI", "ArgoCD",
        "Terraform", "Ansible", "IaC", "인프라스트럭처",
        "모니터링", "로깅", "Prometheus", "Grafana", "ELK",
    ],
    
    # AI/ML/Data
    "ai_data": [
        "AI", "인공지능", "머신러닝", "딥러닝", "ML", "DL",
        "ChatGPT", "GPT", "LLM", "생성AI", "Generative AI",
        "TensorFlow", "PyTorch", "Keras", "scikit-learn",
        "데이터분석", "데이터사이언스", "빅데이터", "Big Data",
        "데이터엔지니어링", "ETL", "Spark", "Hadoop", "Kafka",
        "자연어처리", "NLP", "컴퓨터비전", "CV", "추천시스템",
    ],
    
    # 보안
    "security": [
        "보안", "정보보안", "사이버보안", "Security", "해킹", "방화벽",
        "암호화", "인증", "OAuth", "JWT", "HTTPS", "SSL", "TLS",
        "보안인증", "개인정보", "GDPR", "취약점", "펜테스트",
    ],
    
    # 게임
    "game": [
        "게임", "게임개발", "Unity", "Unreal", "언리얼",
        "게임엔진", "3D", "그래픽", "렌더링", "물리엔진",
        "MMORPG", "모바일게임", "PC게임", "콘솔게임",
    ],
    
    # 블록체인/Web3
    "blockchain": [
        "블록체인", "Blockchain", "암호화폐", "가상화폐", "비트코인",
        "이더리움", "NFT", "Web3", "DeFi", "스마트컨트랙트",
        "메타버스", "디지털자산",
    ],
    
    # 기타 기술
    "other_tech": [
        "오픈소스", "GitHub", "Git", "버전관리", "협업툴",
        "Slack", "Jira", "Confluence", "Notion", "Figma",
        "애자일", "Agile", "스크럼", "Scrum", "칸반",
        "테스트", "QA", "TDD", "단위테스트", "통합테스트",
    ],
    
    # 대기업 - IT/전자
    "major_tech": [
        "삼성전자", "삼성SDS", "삼성SDI", "삼성디스플레이",
        "LG전자", "LG CNS", "LG유플러스", "LGU+",
        "SK텔레콤", "SKT", "SK하이닉스", "SK이노베이션",
        "현대자동차", "현대모비스", "현대오토에버",
        "KT", "KT클라우드", "KT DS",
        "포스코", "포스코ICT", "롯데정보통신",
    ],
    
    # 네이버 계열
    "naver": [
        "네이버", "NAVER", "라인", "LINE", "네이버클라우드",
        "네이버페이", "네이버웹툰", "네이버쇼핑", "스노우",
        "제페토", "ZEPETO", "왓챠", "밴드",
    ],
    
    # 카카오 계열
    "kakao": [
        "카카오", "Kakao", "카카오뱅크", "카카오페이", "카카오모빌리티",
        "카카오엔터", "카카오게임즈", "카카오톡", "카카오맵",
        "다음", "Daum", "멜론", "지그재그",
    ],
    
    # 이커머스/배달
    "commerce": [
        "쿠팡", "Coupang", "이츠", "쿠팡이츠",
        "배달의민족", "배민", "우아한형제들",
        "마켓컬리", "컬리", "SSG", "신세계",
        "11번가", "옥션", "지마켓", "G마켓", "이베이",
        "무신사", "29CM", "에이블리",
    ],
    
    # 핀테크/금융
    "fintech": [
        "토스", "Toss", "비바리퍼블리카",
        "카카오뱅크", "케이뱅크", "K뱅크",
        "뱅크샐러드", "핀다", "렌딧", "8퍼센트",
        "카카오페이", "네이버페이", "페이코", "삼성페이",
        "핀테크", "디지털금융", "모바일뱅킹", "간편결제",
    ],
    
    # 모빌리티
    "mobility": [
        "카카오모빌리티", "카카오T", "타다", "TADA",
        "쏘카", "그린카", "피플카", "카셰어링",
        "우버", "Uber", "그랩", "Grab",
    ],
    
    # 게임사
    "game_company": [
        "넥슨", "Nexon", "엔씨소프트", "NC", "넷마블",
        "크래프톤", "KRAFTON", "펄어비스", "넷게임즈",
        "스마일게이트", "컴투스", "게임빌", "위메이드",
    ],
    
    # 스타트업/유니콘
    "startup": [
        "당근마켓", "직방", "야놀자", "여기어때",
        "두나무", "업비트", "빗썸",
        "센드버드", "하이퍼커넥트", "리디",
        "원티드", "로켓펀치", "리멤버", "잡플래닛",
        "패스트캠퍼스", "인프런", "클래스101",
        "번개장터", "당근", "중고나라",
    ],
    
    # 글로벌 빅테크
    "global_tech": [
        "구글", "Google", "메타", "Meta", "페이스북", "Facebook",
        "아마존", "Amazon", "애플", "Apple", "마이크로소프트", "Microsoft",
        "넷플릭스", "Netflix", "테슬라", "Tesla",
        "오픈AI", "OpenAI", "앤쓰로픽", "Anthropic",
    ],
    
    # 반도체
    "semiconductor": [
        "반도체", "칩", "Chip", "웨이퍼", "파운드리",
        "삼성전자", "SK하이닉스", "인텔", "Intel",
        "TSMC", "엔비디아", "NVIDIA", "AMD",
        "DRAM", "NAND", "SSD", "AP", "CPU", "GPU",
    ],
    
    # 트렌드/이슈
    "trend": [
        "ChatGPT", "생성AI", "Generative AI", "Copilot",
        "자율주행", "전기차", "EV", "배터리",
        "메타버스", "VR", "AR", "XR", "MR",
        "IoT", "사물인터넷", "5G", "6G",
        "양자컴퓨팅", "엣지컴퓨팅",
    ],
}

# 전체 키워드를 하나의 리스트로 평탄화
ALL_KEYWORDS = []
for category_keywords in NEWS_KEYWORDS.values():
    ALL_KEYWORDS.extend(category_keywords)

# 중복 제거
ALL_KEYWORDS = list(set(ALL_KEYWORDS))

# 우선순위 키워드 (매일 수집)
PRIORITY_KEYWORDS = (
    NEWS_KEYWORDS["IT_general"] + 
    NEWS_KEYWORDS["job"] + 
    NEWS_KEYWORDS["naver"] + 
    NEWS_KEYWORDS["kakao"] + 
    NEWS_KEYWORDS["commerce"] +
    NEWS_KEYWORDS["fintech"]
)