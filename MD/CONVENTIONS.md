# 📜 Project Standard Conventions & Architecture

이 문서는 프로젝트의 코드 품질 유지, 원활한 협업, 그리고 일관된 프로젝트 구조를 위한 표준 가이드라인을 정의합니다. 모든 팀원은 개발 시작 전 본 가이드를 반드시 숙지해야 합니다.

---

## 1. 공통 기본 원칙 (Core Principles)

* **Clean Code**: 의미 있는 변수명 사용 및 함수의 단일 책임 원칙(SRP)을 준수합니다.
* **Don't Repeat Yourself (DRY)**: 중복되는 로직은 공통 모듈이나 유틸리티로 분리합니다.
* **Separation of Concerns (SoC)**: UI, 비즈니스 로직, 데이터 접근 계층을 명확히 분리합니다.
* **API-First Design**: 서비스 간 통신을 위해 API 스펙(Swagger/OpenAPI)을 먼저 정의하고 개발을 시작합니다.
* **Stateless Backend**: 서버는 상태를 가지지 않으며, 모든 인증은 JWT 토큰을 기반으로 처리합니다.
* **YAGNI (You Ain't Gonna Need It)**: 실제로 필요하기 전까지는 미리 복잡한 기능을 구현하지 않습니다.

---

## 2. 명명 규칙 (Naming Conventions)

| 대상 | React (TS) | Java (Spring) | Python (FastAPI) |
| :--- | :--- | :--- | :--- |
| **폴더 (Directory)** | `kebab-case` | `lowercase` | `snake_case` |
| **파일 (File)** | `PascalCase` (Comp) | `PascalCase` | `snake_case` |
| **클래스 (Class)** | `PascalCase` | `PascalCase` | `PascalCase` |
| **함수/변수** | `camelCase` | `camelCase` | `snake_case` |
| **상수 (Constant)** | `UPPER_SNAKE` | `UPPER_SNAKE` | `UPPER_SNAKE` |
| **DB 테이블/컬럼** | - | `snake_case` | `snake_case` |

---

## 3. 프로젝트 폴더 구조 (Project Structure)

### ⚛️ Frontend (src/)
**Feature-Sliced Design(FSD)** 개념을 차용하여 기능별 응집도를 높인 구조를 사용합니다.

- **app/**: 전역 설정 (Providers, Router, Global CSS)
- **pages/**: 라우트별 페이지 컴포넌트 (비즈니스 로직 최소화)
- **widgets/**: 여러 feature가 결합된 독립적 복합 컴포넌트
- **features/**: 도메인 기반 핵심 기능 단위 (auth, chat, report, admin)
    - **[feature]/api/**: API 호출 함수
    - **[feature]/ui/**: 해당 기능 전용 컴포넌트
    - **[feature]/hooks/**: 커스텀 훅 (Logic)
    - **[feature]/types/**: 타입 정의
- **shared/**: 전역 공통 요소 (ui-kit, utils, api-client, assets)

### ☕ Java Backend (src/main/java/...)
**Domain-Driven 패키지 구조**를 사용하여 도메인별로 계층을 분리합니다.

- **global/**: 전역 공통 설정 (Security, Config, Exception, Util)
- **domain/**: 비즈니스 도메인별 패키지 (user, video, report, chat)
    - **controller/**: API 엔드포인트
    - **service/**: 비즈니스 로직
    - **repository/**: DB 접근 인터페이스
    - **entity/**: JPA Entity
    - **dto/**: Request/Response 객체

### 🐍 Python Backend (app/)
**Module-based 구조**를 사용하여 기능별로 모듈화합니다.

- **core/**: 앱 전역 설정 (config, security, database)
- **api/**: API 라우터 정의 및 버전 관리 (v1/api.py)
- **services/**: 핵심 비즈니스 로직 및 AI 엔진 연동
- **schemas/**: Pydantic 모델 (Request/Response 데이터 검증)
- **models/**: DB 테이블 모델 (필요 시 사용)
- **main.py**: 애플리케이션 진입점 및 FastAPI 초기화

---

## 4. 기술 스택별 상세 규칙

### ⚛️ Frontend
* **컴포넌트 선언**: `const`를 사용한 화살표 함수를 권장합니다.
* **Logic-UI 분리**: 복잡한 로직은 반드시 Custom Hooks로 추출합니다.
* **상태 관리**: 서버 데이터는 `TanStack Query`, UI 상태는 `Zustand`를 사용합니다.

### ☕ Java
* **Lombok**: `@Getter`, `@NoArgsConstructor`, `@Builder`를 활용하며 `@Data`는 지양합니다.
* **DTO**: Entity를 절대 노출하지 않으며 전용 DTO를 사용합니다.
* **의존성 주입**: 생성자 주입(`@RequiredArgsConstructor`)을 원칙으로 합니다.

### 🐍 Python
* **Type Hinting**: 모든 인자와 반환값에 타입을 명시합니다.
* **Async/Await**: I/O 블로킹 방지를 위해 비동기 처리를 기본으로 합니다.

---

## 5. API 디자인 및 통신 (API Conventions)

* **버전 관리**: 모든 엔드포인트는 `/api/v1/`로 시작합니다.
* **공통 성공/실패 응답**:
```json
{
  "success": true,
  "data": { "item": "value" },
  "error": null
}

{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "사용자 메시지"
  }
}
```

---

## 6. Git 전략 및 커밋 규칙

### 🌿 브랜치 전략 (Git Flow Lite)
프로젝트의 안정성과 빠른 배포를 위해 단순화된 Git Flow를 사용합니다.

- **main**: 상시 배포 가능한 상태의 메인 브랜치 (Production)
- **develop**: 다음 출시 버전을 위해 기능을 통합하는 브랜치 (Staging)
- **feature/[기능명]**: 단위 기능을 개발하는 브랜치. 완료 후 `develop`으로 머지
- **fix/[버그명]**: 출시 버전에서 발견된 긴급 버그를 수정하는 브랜치

### 💬 커밋 메시지 형식 (Conventional Commits)
`type(scope): subject` 형식을 준수하여 히스토리 가독성을 높입니다.

- **feat**: 새로운 기능 추가
- **fix**: 버그 수정
- **docs**: 문서 수정 (README, CONVENTIONS 등)
- **refactor**: 코드 리팩토링 (기능 변경 없이 구조만 개선)
- **style**: 코드 포맷팅, 세미콜론 누락 수정 (비즈니스 로직 변경 없음)
- **test**: 테스트 코드 추가 및 리팩토링
- **chore**: 빌드 업무, 패키지 매니저 설정 등 (기타 변경사항)

**예시**: `feat(chat): AI 대화 히스토리 저장 API 구현`

---

## 7. 문서화 가이드

### 📖 API 문서화
별도의 수기 문서 대신 자동 생성 도구를 사용하여 최신 상태를 유지합니다.
- **Java (Spring Boot)**: `SpringDoc OpenAPI (Swagger)`를 활용하여 UI 제공
- **Python (FastAPI)**: 기본 내장된 `/docs` (Swagger) 및 `/redoc` 활용
- **Frontend**: API 호출 타입과 실제 응답 스펙을 명시한 `types.ts` 파일 관리

### 💡 주석 및 설명
- **Why, Not How**: 코드가 '어떻게' 작동하는지보다는 '왜' 이렇게 작성했는지에 집중하여 작성합니다.
- **표준 포맷 준수**: Java는 `Javadoc`, Python은 `Docstring` 형식을 따릅니다.
- **중요 로직**: 복잡한 알고리즘이나 비즈니스 규칙이 포함된 서비스 레이어에는 반드시 설명을 첨부합니다.

---