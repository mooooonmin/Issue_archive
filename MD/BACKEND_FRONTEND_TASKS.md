# 백엔드/프론트엔드 개발 작업 목록

> AI 개발 제외, 백엔드/프론트엔드만 담당하는 작업 정리

---

## 📋 작업 우선순위 기준

1. **Phase 1 (기획 및 설계)**: 2026.01 (4주)
2. **Phase 2 (개발)**: 2026.02 ~ 2026.03 (8주, Sprint 1~6)
3. **Phase 3 (통합 및 고도화)**: 2026.04 초중 (4주, Sprint 7~10)
4. **Phase 4 (테스트 및 안정화)**: 2026.04 말 (2주)
5. **Phase 5 (출시 및 운영 준비)**: 2026.05 (4주)

---

## 🎨 프론트엔드 작업 목록

### 1. 인프라 및 공통 작업

#### 1.1 프로젝트 구조 설정
- [ ] Feature-based Architecture 구조 생성
  - `src/app/` 디렉토리 생성
  - `src/features/` 디렉토리 생성
  - `src/shared/` 디렉토리 생성
- [ ] TypeScript 전환
  - `.jsx` → `.tsx` 변환
  - 타입 정의 파일 생성
- [ ] 라우팅 설정
  - React Router 설치 및 설정
  - `app/router.tsx` 작성
- [ ] 공통 컴포넌트 개발
  - `shared/ui/Button.tsx`
  - `shared/ui/Input.tsx`
  - `shared/ui/Modal.tsx`
  - `shared/ui/Spinner.tsx`
- [ ] 공통 API 클라이언트
  - `shared/api/http.ts` (fetch/axios wrapper)
  - 공통 에러 처리
  - JWT 토큰 관리

#### 1.2 레이아웃 및 전역 설정
- [ ] MainLayout 컴포넌트
- [ ] Header/Navigation 컴포넌트
- [ ] Sidebar 컴포넌트 (필요시)
- [ ] 전역 Context/Provider 설정
  - 인증 상태 관리
  - 테마 설정
  - 알림 시스템

---

### 2. 인증 모듈 (로그인)

#### 2.1 기능 요구사항
- [ ] 로그인/로그아웃 화면
- [ ] 비밀번호 관리
  - 비밀번호 재설정
  - 최초 로그인 시 초기 비밀번호 변경 강제
  - 비밀번호 정책 적용 (최소 길이, 복잡도)
- [ ] JWT 토큰 관리
  - Access Token / Refresh Token 분리
  - 자동 로그인 기능 (선택 적용)
  - 세션 타임아웃 정책 적용

#### 2.2 구현 작업
- [ ] `features/auth/` 폴더 생성
- [ ] `features/auth/api.ts` - 인증 API 호출
- [ ] `features/auth/hooks/useAuth.ts` - 인증 상태 관리 훅
- [ ] `features/auth/pages/LoginPage.tsx` - 로그인 페이지
- [ ] `features/auth/pages/PasswordResetPage.tsx` - 비밀번호 재설정
- [ ] `features/auth/types.ts` - 인증 관련 타입 정의

---

### 3. AI 대화형 분석 모듈 (핵심 기능)

#### 3.1 기능 요구사항
- [ ] 채팅 인터페이스
  - 한국어 질문 입력
  - 실시간 채팅 형식 답변
  - 대화 히스토리 유지
  - 추가 질문을 통한 연속 질의 지원
  - 세션별 대화 관리
- [ ] 자동 영상 클립 제시
  - 질의 답변 시 AI가 관련 영상 클립 자동 제시
  - 클립별 개별 재생 기능
  - 구간 재생, 배속 조절 (0.5x~4x)
  - 특정 장면 캡처 지원
  - 메타데이터 오버레이 (Bounding Box, 객체 정보)
- [ ] 다중 클립 비교 및 대화 관리
  - 여러 영상 클립의 비교 재생 지원
  - 중요 대화 세션 북마크 기능
  - 분석 결과 기반 보고서 생성 기능 연계

#### 3.2 구현 작업
- [ ] `features/chat/` 폴더 생성
- [ ] `features/chat/api.ts` - 채팅 API 호출
- [ ] `features/chat/hooks/useChat.ts` - 채팅 상태 관리
- [ ] `features/chat/components/ChatInterface.tsx` - 채팅 UI
- [ ] `features/chat/components/VideoClipPlayer.tsx` - 영상 클립 플레이어
- [ ] `features/chat/components/ClipComparison.tsx` - 클립 비교 컴포넌트
- [ ] `features/chat/pages/ChatAnalysisPage.tsx` - 대화형 분석 페이지
- [ ] `features/chat/types.ts` - 채팅 관련 타입 정의

---

### 4. 보고서 관리 모듈

#### 4.1 기능 요구사항
- [ ] 보고서 생성 기능
  - AI 대화 세션 기반 자동 한국어 보고서 생성
  - 사용자 요청에 따른 수동 보고서 생성 지원
  - 분석 결과 요약, 주요 이벤트, 통계 정보 자동 반영
- [ ] 보고서 목록 및 검색 기능
  - 생성된 보고서 목록 조회
  - 날짜, 키워드, 작성자 기준 검색 지원
  - 필터링 및 정렬 기능 제공
  - 페이지네이션 기반 대량 보고서 관리
- [ ] 보고서 상세 조회 기능
  - 분석 요약, 시간대별 주요 이벤트, 통계 및 결론 정보 제공
  - 분석에 활용된 관련 영상 클립 링크 제공
  - 차트 및 시각화된 통계 정보 제공
- [ ] 내보내기 및 공유 기능
  - PDF, Docx 형식 보고서 다운로드 지원
  - 인쇄 기능 제공
  - 이메일 전송 기능 지원
  - URL 기반 공유 기능 제공

#### 4.2 구현 작업
- [ ] `features/reports/` 폴더 생성
- [ ] `features/reports/api.ts` - 보고서 API 호출
- [ ] `features/reports/hooks/useReports.ts` - 보고서 목록 관리
- [ ] `features/reports/hooks/useReportDetail.ts` - 보고서 상세 조회
- [ ] `features/reports/components/ReportList.tsx` - 보고서 목록 컴포넌트
- [ ] `features/reports/components/ReportDetail.tsx` - 보고서 상세 컴포넌트
- [ ] `features/reports/components/ReportChart.tsx` - 통계 차트 컴포넌트
- [ ] `features/reports/pages/ReportListPage.tsx` - 보고서 목록 페이지
- [ ] `features/reports/pages/ReportDetailPage.tsx` - 보고서 상세 페이지
- [ ] `features/reports/types.ts` - 보고서 관련 타입 정의

---

### 5. 대시보드 모듈

#### 5.1 기능 요구사항
- [ ] AI 분석 현황 제공
  - 생성된 분석 결과 및 보고서 개수 제공
  - 금일 AI 질의 건수 표시
  - 분석 처리 상태 (완료 / 진행 중) 표시
  - 최근 대화 및 분석 세션 목록 제공
- [ ] 시스템 통계 정보 제공
  - 자주 사용되는 질의 유형 통계 제공
  - 기간별 분석 건수 추이 시각화 (일 / 주 / 월)
  - 영상 소스별 이용 현황 정보 제공
- [ ] 시스템 상세 모니터링
  - YOLO 기반 메타데이터 생성 진행 상태 표시
  - 시스템 리소스 사용률 (CPU, GPU, 메모리, 저장공간) 모니터링
  - 연결된 영상 소스 상태 정보 제공

#### 5.2 구현 작업
- [ ] `features/dashboard/` 폴더 생성
- [ ] `features/dashboard/api.ts` - 대시보드 통계 API 호출
- [ ] `features/dashboard/hooks/useDashboard.ts` - 대시보드 데이터 관리
- [ ] `features/dashboard/components/StatsCard.tsx` - 통계 카드 컴포넌트
- [ ] `features/dashboard/components/ChartWidget.tsx` - 차트 위젯
- [ ] `features/dashboard/components/SystemMonitor.tsx` - 시스템 모니터링 컴포넌트
- [ ] `features/dashboard/pages/DashboardPage.tsx` - 대시보드 페이지
- [ ] `features/dashboard/types.ts` - 대시보드 관련 타입 정의

---

### 6. 마이페이지 모듈

#### 6.1 기능 요구사항
- [ ] 프로필 관리 기능
  - 사용자 기본 정보 조회 및 수정
  - 이메일 및 연락처 변경 제공 기능
  - 프로필 사진 등록 및 변경 기능 지원
- [ ] 보안 설정 기능
  - 비밀번호 변경 기능 제공
  - 로그인 이력 조회 기능 제공
  - 활성 세션 관리 및 다른 기기 로그아웃 기능 제공
- [ ] 개인 설정 기능
  - 알림 설정 (이메일, 시스템 알림) 관리
  - 언어 설정 기능 제공
  - UI 테마 설정 (다크 모드 등) 지원

#### 6.2 구현 작업
- [ ] `features/profile/` 폴더 생성
- [ ] `features/profile/api.ts` - 프로필 API 호출
- [ ] `features/profile/hooks/useProfile.ts` - 프로필 상태 관리
- [ ] `features/profile/components/ProfileForm.tsx` - 프로필 수정 폼
- [ ] `features/profile/components/SecuritySettings.tsx` - 보안 설정 컴포넌트
- [ ] `features/profile/components/NotificationSettings.tsx` - 알림 설정 컴포넌트
- [ ] `features/profile/pages/MyPage.tsx` - 마이페이지
- [ ] `features/profile/types.ts` - 프로필 관련 타입 정의

---

### 7. AI 시스템 관리 모듈 (관리자 전용)

#### 7.1 기능 요구사항
- [ ] 사용자 관리 기능
  - 사용자 계정 추가, 수정 및 삭제
  - 역할 및 권한 설정 (일반 사용자, 분석 담당자, 관리자)
  - 영상 소스별 접근 권한 설정
  - 사용자 활동 로그 조회
- [ ] 영상 소스 관리 기능
  - NVR/DVR 연결 설정 (IP, 포트, 인증 정보)
  - 파일 기반 영상 소스 경로 설정 (NFS, SMB)
  - 영상 소스 추가, 수정 및 삭제
  - 영상 소스 연결 상태 모니터링
- [ ] 분석 스케줄 관리 기능
  - YOLO 및 AI 분석 실행 주기 설정
  - 영상 소스별 개별 분석 스케줄 설정
  - 분석 시간대 설정 (주간 / 야간 구분)
  - 분석 작업 우선순위 설정
- [ ] 시스템 설정 기능
  - 시스템 전역 설정 (시스템 명, 시간대 등)
  - 백업 주기 및 보관 위치 설정
  - 로그 보관 정책 관리
  - 외부 연동을 위한 API 설정

#### 7.2 구현 작업
- [ ] `features/admin/` 폴더 생성
- [ ] `features/admin/api.ts` - 관리자 API 호출
- [ ] `features/admin/hooks/useUserManagement.ts` - 사용자 관리 훅
- [ ] `features/admin/hooks/useVideoSourceManagement.ts` - 영상 소스 관리 훅
- [ ] `features/admin/hooks/useScheduleManagement.ts` - 스케줄 관리 훅
- [ ] `features/admin/components/UserManagement.tsx` - 사용자 관리 컴포넌트
- [ ] `features/admin/components/VideoSourceManagement.tsx` - 영상 소스 관리 컴포넌트
- [ ] `features/admin/components/ScheduleManagement.tsx` - 스케줄 관리 컴포넌트
- [ ] `features/admin/components/SystemSettings.tsx` - 시스템 설정 컴포넌트
- [ ] `features/admin/pages/AdminPage.tsx` - 관리자 페이지
- [ ] `features/admin/types.ts` - 관리자 관련 타입 정의

---

## ⚙️ 백엔드 작업 목록

> **Java (Spring Boot)**와 **Python (FastAPI)**로 구분

---

## ☕ Java (Spring Boot) 백엔드 작업

### 1. 인프라 및 공통 작업

#### 1.1 프로젝트 구조 설정
- [ ] Spring Boot 프로젝트 구조 정리
- [ ] 패키지 구조 정리 (controller, service, dto, entity, repository)
- [ ] 공통 예외 처리 클래스 생성
- [ ] 공통 응답 포맷 정의 (ResponseDto)
- [ ] 로깅 설정 (Logback)

#### 1.2 데이터베이스 설정
- [ ] PostgreSQL 연결 설정
- [ ] TimescaleDB 연결 설정
- [ ] Flyway 마이그레이션 설정
- [ ] DB 스키마 설계 및 마이그레이션 스크립트 작성
  - users, roles 테이블
  - cameras, camera_zones 테이블
  - storage_sources 테이블
  - activity_logs 테이블
  - system_config 테이블
  - reports 테이블
  - yolo_objects 테이블 (TimescaleDB)
  - saint_situations 테이블 (TimescaleDB)
  - saint_features 테이블 (TimescaleDB)
  - saint_baselines 테이블 (TimescaleDB)

---

### 2. 인증 및 권한 관리

#### 2.1 JWT 기반 인증
- [ ] JWT 토큰 발급 및 검증 로직
- [ ] Access Token / Refresh Token 분리 운영
- [ ] 토큰 만료 정책 및 세션 상태 관리
- [ ] 비정상 인증 시도에 대한 차단 및 기록

#### 2.2 역할 기반 접근 제어 (RBAC)
- [ ] 역할 기반 접근 제어 구현
- [ ] 기능·리소스·API 단위 세분화된 권한 설정
- [ ] 영상 소스별 접근 권한 관리
- [ ] 모든 인증·권한 변경 이력에 대한 감사 로그 기록
- [ ] 관리자 권한 사용 이력 추적

#### 2.3 API 구현
- [ ] `POST /api/v1/auth/login` - 로그인
- [ ] `POST /api/v1/auth/logout` - 로그아웃
- [ ] `POST /api/v1/auth/refresh` - 토큰 갱신
- [ ] `POST /api/v1/auth/password/reset` - 비밀번호 재설정
- [ ] `GET /api/v1/auth/sessions` - 활성 세션 조회
- [ ] `DELETE /api/v1/auth/sessions/{sessionId}` - 세션 종료

---

### 3. API Gateway

#### 3.1 Gateway 기능
- [ ] 요청 라우팅 (URL 경로 기반 서비스 라우팅)
- [ ] 서비스 단위 트래픽 분산 처리
- [ ] API 버전별 요청 분기 관리
- [ ] JWT 토큰 검증을 통한 요청 인증
- [ ] Rate Limiting 적용 (비정상 트래픽 및 과도한 요청 차단)
- [ ] 응답 캐싱을 통한 반복 요청 성능 최적화
- [ ] 요청 응답 로깅을 통한 운영 모니터링 및 감사 대응
- [ ] 내부 서비스 장애 시 영향 범위 최소화를 위한 격리 구조 지원

#### 3.2 구현 작업
- [ ] Spring Cloud Gateway 또는 Spring Security Filter Chain 구성
- [ ] 라우팅 규칙 설정
- [ ] Rate Limiting 필터 구현
- [ ] 캐싱 전략 구현

---

### 4. AI 대화형 분석 API

#### 4.1 채팅 API
- [ ] `POST /api/v1/chat` - AI 대화형 영상 분석 질의 처리
  - 자연어 질의 파싱
  - 메타데이터 검색 (TimescaleDB 쿼리)
  - AI 서비스 호출 (VLM 엔진 연동)
  - 응답 반환
- [ ] `GET /api/v1/chat/sessions` - 대화 세션 목록 조회
- [ ] `GET /api/v1/chat/sessions/{sessionId}` - 특정 세션 대화 히스토리 조회
- [ ] `POST /api/v1/chat/sessions/{sessionId}/bookmark` - 세션 북마크

#### 4.2 영상 클립 API
- [ ] `GET /api/v1/videos/clips/{clipId}` - 영상 클립 스트리밍
- [ ] `GET /api/v1/videos/clips/{clipId}/metadata` - 클립 메타데이터 조회
- [ ] `POST /api/v1/videos/clips` - 클립 생성 요청
  - 원본 영상에서 구간 추출
  - 10초 클립 생성 (이벤트 시점 기준 앞 5초 + 뒤 5초)
  - 클립 파일 저장

---

### 5. 보고서 관리 API

#### 5.1 보고서 CRUD
- [ ] `POST /api/v1/reports` - 보고서 생성
  - AI 대화 세션 기반 자동 생성
  - 사용자 요청에 따른 수동 생성
- [ ] `GET /api/v1/reports` - 보고서 목록 조회
  - 날짜, 키워드, 작성자 기준 검색
  - 필터링 및 정렬
  - 페이지네이션
- [ ] `GET /api/v1/reports/{reportId}` - 보고서 상세 조회
- [ ] `PUT /api/v1/reports/{reportId}` - 보고서 수정
- [ ] `DELETE /api/v1/reports/{reportId}` - 보고서 삭제

#### 5.2 보고서 내보내기
- [ ] `GET /api/v1/reports/{reportId}/export/pdf` - PDF 다운로드
- [ ] `GET /api/v1/reports/{reportId}/export/docx` - DOCX 다운로드
- [ ] `POST /api/v1/reports/{reportId}/share` - URL 기반 공유
- [ ] `POST /api/v1/reports/{reportId}/email` - 이메일 전송

---

### 6. 메타데이터 조회 API

#### 6.1 YOLO 객체 데이터
- [ ] `GET /api/v1/metadata/yolo-objects` - YOLO 객체 탐지 결과 조회
  - 시간 범위 검색
  - 카메라별 검색
  - 객체 유형별 검색
  - 페이지네이션

#### 6.2 SAINT 상황 데이터
- [ ] `GET /api/v1/metadata/situations` - SAINT 상황 판단 결과 조회
  - 정상/드묾/이상 필터링
  - 심각도별 필터링
  - 시간 범위 검색
  - 카메라별 검색

---

### 7. 사용자 관리 API (관리자)

#### 7.1 사용자 CRUD
- [ ] `GET /api/v1/users` - 사용자 목록 조회
- [ ] `POST /api/v1/users` - 사용자 계정 추가
- [ ] `GET /api/v1/users/{userId}` - 사용자 상세 조회
- [ ] `PUT /api/v1/users/{userId}` - 사용자 정보 수정
- [ ] `DELETE /api/v1/users/{userId}` - 사용자 계정 삭제
- [ ] `PUT /api/v1/users/{userId}/role` - 역할 및 권한 설정
- [ ] `GET /api/v1/users/{userId}/activity` - 사용자 활동 로그 조회

---

### 8. 영상 소스 관리 API (관리자)

#### 8.1 영상 소스 CRUD
- [ ] `GET /api/v1/system/video-sources` - 영상 소스 목록 조회
- [ ] `POST /api/v1/system/video-sources` - 영상 소스 추가
  - NVR/DVR 연결 설정 (IP, 포트, 인증 정보)
  - 파일 기반 영상 소스 경로 설정 (NFS, SMB)
- [ ] `GET /api/v1/system/video-sources/{sourceId}` - 영상 소스 상세 조회
- [ ] `PUT /api/v1/system/video-sources/{sourceId}` - 영상 소스 수정
- [ ] `DELETE /api/v1/system/video-sources/{sourceId}` - 영상 소스 삭제
- [ ] `GET /api/v1/system/video-sources/{sourceId}/status` - 연결 상태 모니터링
- [ ] `POST /api/v1/system/video-sources/{sourceId}/test` - 연결 테스트

---

### 9. 스케줄링 및 작업 관리 API (관리자)

#### 9.1 스케줄 관리
- [ ] `GET /api/v1/system/schedules` - 분석 스케줄 목록 조회
- [ ] `POST /api/v1/system/schedules` - 분석 스케줄 생성
  - YOLO 및 AI 분석 실행 주기 설정
  - 영상 소스별 개별 분석 스케줄 설정
  - 분석 시간대 설정 (주간 / 야간 구분)
  - 분석 작업 우선순위 설정
- [ ] `PUT /api/v1/system/schedules/{scheduleId}` - 스케줄 수정
- [ ] `DELETE /api/v1/system/schedules/{scheduleId}` - 스케줄 삭제

#### 9.2 작업 관리
- [ ] `GET /api/v1/system/jobs` - 작업 목록 조회
- [ ] `GET /api/v1/system/jobs/{jobId}` - 작업 상세 조회
- [ ] `GET /api/v1/system/jobs/{jobId}/status` - 작업 상태 조회
- [ ] `POST /api/v1/system/jobs/{jobId}/retry` - 실패 작업 재시도

---

### 10. 시스템 설정 API (관리자)

#### 10.1 시스템 설정
- [ ] `GET /api/v1/system/config` - 시스템 전역 설정 조회
- [ ] `PUT /api/v1/system/config` - 시스템 전역 설정 수정
  - 시스템 명, 시간대 등
  - 백업 주기 및 보관 위치 설정
  - 로그 보관 정책 관리
  - 외부 연동을 위한 API 설정

#### 10.2 시스템 모니터링
- [ ] `GET /api/v1/system/monitoring/stats` - 시스템 통계 정보
  - YOLO 기반 메타데이터 생성 진행 상태
  - 시스템 리소스 사용률 (CPU, GPU, 메모리, 저장공간)
  - 연결된 영상 소스 상태 정보
- [ ] `GET /api/v1/system/monitoring/resources` - 리소스 사용률 상세

---

### 11. AI 서비스 연동 (Python FastAPI 호출)

#### 11.1 AI 서비스 클라이언트
- [ ] Python FastAPI 서비스 호출 클라이언트 구현
  - HTTP 클라이언트 (RestTemplate 또는 WebClient)
  - YOLO 엔진 호출 인터페이스
  - SAINT 엔진 호출 인터페이스
  - VLM 엔진 호출 인터페이스
- [ ] 에러 처리 및 재시도 로직
- [ ] 타임아웃 설정

#### 11.2 비동기 작업 처리
- [ ] 작업 큐 시스템 구현 (RabbitMQ 또는 Redis Queue)
- [ ] 비동기 작업 상태 관리
- [ ] 작업 결과 저장 및 조회
- [ ] Python 서비스와의 비동기 통신

---

### 12. 데이터베이스 쿼리 최적화

#### 12.1 TimescaleDB 쿼리 최적화
- [ ] 시간 범위 검색 쿼리 최적화
- [ ] 카메라별 검색 쿼리 최적화
- [ ] 객체 유형별 검색 쿼리 최적화
- [ ] 집계 쿼리 최적화
- [ ] 인덱스 최적화

#### 12.2 PostgreSQL 쿼리 최적화
- [ ] 사용자 조회 쿼리 최적화
- [ ] 보고서 조회 쿼리 최적화
- [ ] 활동 로그 조회 쿼리 최적화

---

### 13. 보안 및 감사 로그

#### 13.1 감사 로그
- [ ] 모든 인증·권한 변경 이력 기록
- [ ] 관리자 권한 사용 이력 추적
- [ ] 사용자 활동 로그 기록
- [ ] API 호출 로그 기록

#### 13.2 보안 강화
- [ ] SQL Injection 방지
- [ ] XSS 방지
- [ ] CSRF 방지
- [ ] 민감 정보 암호화

---

### 14. 테스트

#### 14.1 Unit Test
- [ ] Service 레이어 테스트
- [ ] Repository 레이어 테스트
- [ ] Controller 레이어 테스트
- [ ] 커버리지 80% 이상 목표

#### 14.2 Integration Test
- [ ] API 엔드포인트 통합 테스트
- [ ] 데이터베이스 통합 테스트
- [ ] Python FastAPI 서비스 연동 테스트 (Mock)

---

## 🐍 Python (FastAPI) 백엔드 작업

### 1. 인프라 및 공통 작업

#### 1.1 프로젝트 구조 설정
- [ ] FastAPI 프로젝트 구조 정리
- [ ] 패키지 구조 정리 (routers, services, models, utils)
- [ ] 공통 예외 처리 클래스 생성
- [ ] 공통 응답 포맷 정의
- [ ] 로깅 설정

#### 1.2 의존성 관리
- [ ] requirements.txt 정리
- [ ] 가상환경 설정
- [ ] 의존성 버전 관리

---

### 2. 영상 처리 API

#### 2.1 비디오 정보 조회
- [ ] `GET /api/video/info` - 비디오 정보 조회
  - FPS, 총 프레임 수, 해상도, 길이 등
- [ ] `GET /api/video/stream` - 비디오 스트리밍
  - 원본 영상 파일 스트리밍

#### 2.2 프레임 추출
- [ ] `GET /api/video/frames` - 프레임 추출
  - 지정된 간격으로 프레임 추출
  - Base64 인코딩된 이미지 반환

---

### 3. 영상 클립 생성 API

#### 3.1 클립 생성
- [ ] `POST /api/video/clips` - 영상 클립 생성
  - 원본 영상에서 구간 추출
  - 10초 클립 생성 (이벤트 시점 기준 앞 5초 + 뒤 5초)
  - 클립 파일 저장
- [ ] `GET /api/video/clips/{clipId}` - 클립 스트리밍
- [ ] `GET /api/video/clips/{clipId}/metadata` - 클립 메타데이터 조회

---

### 4. YOLO 엔진 연동 API

#### 4.1 YOLO 객체 탐지
- [ ] `POST /api/yolo/detect` - 객체 탐지 요청
  - 영상 파일 경로 또는 프레임 데이터 받기
  - YOLO 모델 호출
  - 객체 탐지 결과 반환
- [ ] `POST /api/yolo/detect-batch` - 배치 객체 탐지
  - 여러 프레임 일괄 처리
- [ ] `GET /api/yolo/models` - 사용 가능한 모델 목록

#### 4.2 YOLO 결과 처리
- [ ] 탐지 결과를 TimescaleDB 저장 형식으로 변환
- [ ] Java Spring Boot로 결과 전달 (또는 직접 DB 저장)

---

### 5. SAINT 엔진 연동 API

#### 5.1 SAINT 상황 인지
- [ ] `POST /api/saint/analyze` - 상황 분석 요청
  - YOLO 탐지 결과 받기
  - 카메라 메타정보 받기
  - SAINT 모델 호출
  - 상황 판단 결과 반환
- [ ] `POST /api/saint/learn` - 학습 요청
  - 새로운 패턴 학습
  - 베이스라인 업데이트

#### 5.2 SAINT 결과 처리
- [ ] 판단 결과를 TimescaleDB 저장 형식으로 변환
- [ ] Java Spring Boot로 결과 전달 (또는 직접 DB 저장)

---

### 6. VLM 엔진 연동 API

#### 6.1 VLM 자연어 분석
- [ ] `POST /api/vlm/query` - 자연어 질의 처리
  - 사용자 자연어 질의 받기
  - 메타데이터 검색 결과 받기 (Java에서 전달)
  - VLM 모델 호출
  - 분석 결과 및 설명 생성
- [ ] `POST /api/vlm/generate-report` - 보고서 생성
  - 분석 결과를 기반으로 한국어 보고서 생성
  - Word 문서 형식으로 변환

#### 6.2 VLM 결과 처리
- [ ] 분석 결과 텍스트 반환
- [ ] 관련 영상 클립 경로 반환
- [ ] 보고서 생성 데이터 반환

---

### 7. AI 엔진 관리 API

#### 7.1 모델 관리
- [ ] `GET /api/ai/models` - 사용 가능한 모델 목록
- [ ] `POST /api/ai/models/{modelId}/load` - 모델 로드
- [ ] `POST /api/ai/models/{modelId}/unload` - 모델 언로드
- [ ] `GET /api/ai/models/{modelId}/status` - 모델 상태 조회

#### 7.2 리소스 모니터링
- [ ] `GET /api/ai/monitoring/gpu` - GPU 사용률 조회
- [ ] `GET /api/ai/monitoring/memory` - 메모리 사용률 조회
- [ ] `GET /api/ai/monitoring/jobs` - 실행 중인 작업 목록

---

### 8. 비동기 작업 처리

#### 8.1 작업 큐
- [ ] Celery 또는 FastAPI Background Tasks 설정
- [ ] 작업 큐 구현
- [ ] 작업 상태 관리
- [ ] 작업 결과 저장

#### 8.2 작업 API
- [ ] `POST /api/jobs` - 작업 생성
- [ ] `GET /api/jobs/{jobId}` - 작업 상태 조회
- [ ] `GET /api/jobs/{jobId}/result` - 작업 결과 조회
- [ ] `POST /api/jobs/{jobId}/cancel` - 작업 취소

---

### 9. Java Spring Boot와의 통신

#### 9.1 통신 인터페이스
- [ ] Java에서 호출할 수 있는 REST API 제공
- [ ] Java에서 전달받은 데이터 처리
- [ ] 결과를 Java로 전달 (또는 직접 DB 저장)

#### 9.2 데이터 형식
- [ ] 요청/응답 데이터 형식 정의
- [ ] 에러 응답 형식 정의
- [ ] 공통 DTO 모델 정의

---

### 10. 데이터베이스 연동

#### 10.1 TimescaleDB 연동
- [ ] TimescaleDB 연결 설정
- [ ] YOLO 결과 저장
- [ ] SAINT 결과 저장
- [ ] 쿼리 최적화

#### 10.2 PostgreSQL 연동 (선택)
- [ ] 작업 이력 저장
- [ ] 설정 정보 저장

---

### 11. 영상 파일 관리

#### 11.1 파일 시스템 연동
- [ ] NVR/DVR 마운트 경로 읽기
- [ ] 영상 파일 접근
- [ ] 클립 파일 저장
- [ ] 파일 경로 관리

#### 11.2 스토리지 최적화
- [ ] 파일 캐싱
- [ ] 임시 파일 정리
- [ ] 스토리지 용량 관리

---

### 12. 테스트

#### 12.1 Unit Test
- [ ] Service 레이어 테스트
- [ ] 모델 호출 테스트 (Mock)
- [ ] 유틸리티 함수 테스트
- [ ] 커버리지 80% 이상 목표

#### 12.2 Integration Test
- [ ] API 엔드포인트 통합 테스트
- [ ] AI 엔진 연동 테스트 (Mock)
- [ ] Java Spring Boot 연동 테스트

---

## 📊 작업 우선순위 (Sprint별)

### Sprint 1-2: 인증 시스템 및 기본 인프라
- **프론트엔드**: 인증 모듈, 공통 컴포넌트
- **Java 백엔드**: 인증 API, 기본 API 구조, DB 스키마
- **Python 백엔드**: 프로젝트 구조 설정, 기본 API

### Sprint 3-4: 대시보드 및 기본 화면
- **프론트엔드**: 대시보드 모듈, 레이아웃
- **Java 백엔드**: 통계 API, 모니터링 API
- **Python 백엔드**: 영상 처리 API 개선

### Sprint 5-6: AI 대화형 분석 (AI 서비스 연동)
- **프론트엔드**: 채팅 인터페이스, 영상 클립 플레이어
- **Java 백엔드**: 채팅 API, 메타데이터 조회 API, Python 서비스 호출 클라이언트
- **Python 백엔드**: 클립 생성 API, YOLO/SAINT/VLM 엔진 연동 API

### Sprint 7-8: 보고서 및 관리 기능
- **프론트엔드**: 보고서 모듈, 관리자 모듈
- **Java 백엔드**: 보고서 API, 사용자 관리 API, 영상 소스 관리 API
- **Python 백엔드**: 보고서 생성 API, AI 엔진 관리 API

### Sprint 9-10: 통합 및 최적화
- **프론트엔드**: 전체 통합, UX 개선
- **Java 백엔드**: 성능 최적화, 보안 강화, Python 서비스 연동 최적화
- **Python 백엔드**: 성능 최적화, 리소스 관리, Java 연동 최적화

---

## 🔗 Java ↔ Python 연동 포인트

### Java → Python (요청)

#### 1. YOLO 엔진 호출
- **Java가 전달**: 영상 파일 경로, 처리 우선순위
- **Python이 반환**: 객체 탐지 결과 (JSON)
- **API**: `POST /api/yolo/detect`

#### 2. SAINT 엔진 호출
- **Java가 전달**: YOLO 탐지 결과 (TimescaleDB에서 조회), 카메라 메타정보
- **Python이 반환**: 상황 판단 결과 (JSON)
- **API**: `POST /api/saint/analyze`

#### 3. VLM 엔진 호출
- **Java가 전달**: 사용자 자연어 질의, 검색된 메타데이터 (TimescaleDB 쿼리 결과), 관련 영상 파일 경로
- **Python이 반환**: 분석 결과 텍스트, 관련 영상 클립 경로, 보고서 생성 데이터
- **API**: `POST /api/vlm/query`, `POST /api/vlm/generate-report`

#### 4. 영상 클립 생성
- **Java가 전달**: 원본 영상 경로, 시작 시간, 종료 시간
- **Python이 반환**: 생성된 클립 파일 경로
- **API**: `POST /api/video/clips`

### Python → Java (결과 저장)

#### 1. YOLO 결과 저장
- **Python이 생성**: 객체 탐지 결과
- **저장 방식**: 
  - 옵션 A: Python에서 직접 TimescaleDB 저장
  - 옵션 B: Java API로 전달하여 Java에서 저장
    ₩
#### 2. SAINT 결과 저장
- **Python이 생성**: 상황 판단 결과
- **저장 방식**: 
  - 옵션 A: Python에서 직접 TimescaleDB 저장
  - 옵션 B: Java API로 전달하여 Java에서 저장

#### 3. 작업 상태 업데이트
- **Python이 전달**: 작업 진행 상태, 완료 여부
- **Java가 관리**: 작업 큐, 상태 추적
- **API**: `PUT /api/jobs/{jobId}/status` (Java에서 제공)

---

## 📝 참고사항

### 역할 분담
- **Java (Spring Boot)**: 메인 API 서버, 인증/권한, CRUD, 관리 기능, DB 관리
- **Python (FastAPI)**: 영상 처리, AI 엔진 연동, 클립 생성, AI 서비스 인터페이스
- **AI 엔진 개발**: 별도 팀에서 담당 (YOLO, SAINT, VLM 모델 자체는 AI 팀)

### 개발 전략
- **Phase 1-2**: Java와 Python 각각 독립적으로 개발 가능
- **Phase 3**: Java ↔ Python 연동 인터페이스 정의 및 구현
- **Mock 데이터**: AI 엔진이 준비되기 전까지 Mock 응답으로 개발 가능

### 기술 스택
- **Java**: Spring Boot 3.2.5, Spring Security 6.2.3, Java 17
- **Python**: FastAPI 0.110.0, Python 3.11.9
- **통신**: RESTful API (HTTP/JSON)
- **비동기**: RabbitMQ 또는 Redis Queue (선택)

### 문서화
- 모든 API는 Swagger/OpenAPI 문서로 자동 생성
- Java: SpringDoc OpenAPI
- Python: FastAPI 자동 문서화

### 아키텍처 원칙
- 프론트엔드: Feature-based Architecture 구조 준수
- Java 백엔드: RESTful API 원칙 준수, 계층화된 구조
- Python 백엔드: RESTful API 원칙 준수, 모듈화된 구조

