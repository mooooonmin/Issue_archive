# 📋 Project Task List (Back-end & Front-end) ver0.1

이 문서는 AI 서비스를 제외한 백엔드 및 프론트엔드 개발 작업의 진척도를 관리합니다.

---

## 📅 프로젝트 일정 (Phases)
- [ ] **Phase 1 (기획 및 설계)**: 2026.01 (4주)
- [ ] **Phase 2 (개발)**: 2026.02 ~ 2026.03 (8주, Sprint 1~6)
- [ ] **Phase 3 (통합 및 고도화)**: 2026.04 (4주, Sprint 7~10)
- [ ] **Phase 4 (테스트 및 안정화)**: 2026.04 말 (2주)
- [ ] **Phase 5 (출시 및 운영 준비)**: 2026.05 (4주)

---

## 🎨 프론트엔드 (React & TypeScript)

### 1. 인프라 및 공통 작업
- [ ] Feature-based Architecture 구조 생성 (`app/`, `features/`, `shared/`)
- [ ] TypeScript 환경 구성 및 타입 정의 파일 생성
- [ ] React Router 기반 라우팅 설정 (`app/router.tsx`)
- [ ] 공통 UI 컴포넌트 개발 (Button, Input, Modal, Spinner 등)
- [ ] Axios/Fetch Wrapper 기반 공통 API 클라이언트 및 에러 처리 구현
- [ ] 레이아웃 컴포넌트 구성 (MainLayout, Header, Sidebar)
- [ ] 전역 상태 관리 및 Provider 설정 (인증, 테마, 알림)

### 2. 인증 모듈 (Auth)
- [ ] 로그인/로그아웃 페이지 및 기능 구현
- [ ] 비밀번호 재설정 및 초기 비밀번호 변경 강제 로직
- [ ] JWT 토큰 관리 (Access/Refresh Token) 및 세션 만료 정책 적용

### 3. AI 대화형 분석 모듈 (Core)
- [ ] 채팅 인터페이스 구현 (실시간 응답 UI, 히스토리 관리)
- [ ] 비디오 클립 플레이어 (구간 재생, 배속 조절, 장면 캡처, Bounding Box 오버레이)
- [ ] 다중 클립 비교 및 세션 북마크 기능
- [ ] 분석 결과 보고서 생성 연계 UI

### 4. 보고서 및 대시보드
- [ ] 보고서 생성/조회/검색/페이지네이션 기능
- [ ] PDF 및 Docx 내보내기, 이메일/URL 공유 기능
- [ ] 대시보드 통계 위젯 (분석 현황, 시스템 리소스 모니터링)
- [ ] 마이페이지 (프로필 수정, 보안 설정, 개인화 알림 설정)

### 5. 관리자 기능
- [ ] 사용자 관리 (계정 CRUD, RBAC 권한 설정)
- [ ] 영상 소스 관리 (NVR/DVR 연결 및 파일 경로 설정)
- [ ] AI 분석 스케줄링 및 시스템 전역 설정 관리

---

## ☕ 백엔드 - Java (Spring Boot)

### 1. 인프라 및 인증
- [ ] Spring Boot 프로젝트 구조 및 패키지 레이어링
- [ ] PostgreSQL & TimescaleDB 연결 및 Flyway 마이그레이션 설정
- [ ] JWT 기반 인증/인가 및 RBAC(역할 기반 접근 제어) 구현
- [ ] Spring Cloud Gateway 또는 Filter 기반 API Gateway 구성

### 2. 핵심 API 구현
- [ ] **AI 채팅 API**: 자연어 질의 파싱 연계 및 대화 세션 관리
- [ ] **영상 클립 API**: 클립 스트리밍 엔드포인트 및 메타데이터 조회
- [ ] **보고서 API**: CRUD 기능 및 PDF/Docx 생성 로직
- [ ] **메타데이터 API**: YOLO/SAINT 결과 조회용 최적화 쿼리 (TimescaleDB)

### 3. 시스템 및 관리 기능
- [ ] 사용자 및 권한 관리 API
- [ ] 영상 소스 및 분석 스케줄링 관리 API (CRUD)
- [ ] 시스템 모니터링 및 리소스 통계 API
- [ ] 감사 로그(Audit Log) 기록 및 보안 강화 (SQLi, XSS 방지)

### 4. 연동 및 비동기 처리
- [ ] Python FastAPI 서비스 호출 클라이언트 (WebClient) 구현
- [ ] Redis/RabbitMQ 기반 비동기 작업 큐 및 상태 추적 로직

---

## 🐍 백엔드 - Python (FastAPI)

### 1. 영상 처리 및 클립 생성
- [ ] 비디오 메타데이터(FPS, Resolution) 추출 API
- [ ] 원본 영상 기반 지정 구간(10초) 클립 생성 및 저장 로직
- [ ] 프레임 추출 및 Base64 변환 유틸리티

### 2. AI 엔진 연동 인터페이스
- [ ] **YOLO API**: 객체 탐지 요청 수신 및 결과 반환
- [ ] **SAINT API**: 상황 인지 분석 요청 처리
- [ ] **VLM API**: 자연어 질의 기반 분석 결과 및 한국어 보고서 데이터 생성

### 3. 리소스 및 작업 관리
- [ ] GPU/Memory 사용률 모니터링 API
- [ ] Background Tasks 기반 AI 작업 상태 관리 및 결과 저장
- [ ] Java 서비스와의 데이터 규격(DTO) 통일 및 REST 통신 구현

---

## 🔗 시스템 연동 포인트 (TODO 확인필요요)
- [ ] **Java → Python**: 분석 요청, 클립 생성 요청, VLM 질의
- [ ] **Python → Java/DB**: 분석 완료 상태 업데이트, 메타데이터 직접 저장(옵션)
- [ ] **FE → Java**: 모든 비즈니스 요청 및 데이터 조회

---

26.01.12