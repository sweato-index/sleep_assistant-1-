erDiagram
    user {
        CHAR(10) user_id PK
        VARCHAR(20) phone_number UK
        VARCHAR(255) password
        VARCHAR(20) user_name
        INT age
        CHAR(2) user_type
        CHAR(2) gender
        VARCHAR(10) tag
        VARCHAR(40) description
        DATETIME birthday
        VARCHAR(20) email UK
        VARCHAR(8) sleep_notice
        VARCHAR(8) wake_notice
    }
    
    sleep_record ||--o{ user : "user_id(FK)"
    document ||--o{ user : "post_user_id(FK)"
    doc_user_action ||--o{ document : "doc_id(FK)"
    doc_user_action ||--o{ user : "user_id(FK)"
    doc_comment ||--o{ document : "doc_id(FK)"
    doc_comment ||--o{ user : "user_id(FK)"
    doc_comment ||--o{ doc_comment : "parent_id(FK)"
    sleep_challenge ||--o{ user : "initiator_id(FK)"
    user_challenge }|--|| user : "user_id(FK)"
    user_challenge }|--|| sleep_challenge : "challenge_id(FK)"
    ai_qa ||--o{ user : "user_id(FK)"

    user ||--o{ sleep_record : makes
    user ||--o{ document : posts
    user ||--o{ doc_user_action : performs
    user ||--o{ doc_comment : writes
    user ||--o{ sleep_challenge : initiates
    user ||--o{ user_challenge : participates
    user ||--o{ ai_qa : creates

    sleep_record {
        CHAR(15) record_id PK
        CHAR(10) user_id FK
        DATETIME record_time
        DATETIME sleep_time
        DATETIME wake_time
        VARCHAR(2) rating
    }

    document {
        CHAR(10) doc_id PK
        CHAR(2) doc_type
        CHAR(10) post_user_id FK
        VARCHAR(20) title
        VARCHAR(30) summary
        VARCHAR(1000) text
        VARCHAR(20) image_url
    }

    doc_user_action {
        CHAR(10) action_id PK
        CHAR(10) doc_id FK
        CHAR(10) user_id FK
        CHAR(2) action_type
        DATETIME create_time
    }

    doc_comment {
        CHAR(10) comment_id PK
        CHAR(10) doc_id FK
        CHAR(10) user_id FK
        CHAR(10) parent_id FK
        VARCHAR(50) comment
        DATETIME create_time
        CHAR(2) status
    }

    sleep_challenge {
        CHAR(10) challenge_id PK
        VARCHAR(20) challenge_title
        CHAR(10) initiator_id FK
        DATETIME create_time
        CHAR(2) status
    }

    user_challenge {
        CHAR(10) user_id PK,FK
        CHAR(10) challenge_id PK,FK
        DATETIME update_date
        CHAR(2) status
    }

    ai_qa {
        CHAR(10) qa_id PK
        CHAR(10) user_id FK
        VARCHAR(100) qa_content
        DATETIME create_time
        VARCHAR(100) answers
    }