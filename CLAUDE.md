# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 문서 구조

- @docs/PRD.md — 이 모듈의 상세 요구사항
- @docs/HARNESS.md — 이 모듈이 참여하는 에이전틱 개발 오케스트레이션에서의 역할

## 프로젝트 컨텍스트

이 저장소(`ConsoleMVC-YongjinLee-22038808`)는 "반도체 시료 생산주문관리 시스템"의 미션1(PoC) 산출물이며, 최종 통합 저장소 `SampleOrderSystem-YongjinLee-22038808`의 `modules/console-mvc/`로 포함된다. 상세 요구사항은 이 저장소의 `docs/PRD.md`와 통합 저장소의 `docs/PRD.md`, `docs/SCHEMA.md`(공유 데이터 스키마)를 따른다.

## 커밋 메시지 컨벤션

모든 커밋 메시지는 아래 두 접두사 중 하나로 시작한다.

| 접두사 | 대상 |
|---|---|
| `[PLAN]` | 계획/설계 내용 — `PRD.md` 등 문서 작성·수정, 요구사항 정리, 설계 결정 |
| `[ACTION]` | 실제 구현 내용 — 코드 작성/수정/리팩터링, 테스트 작성, 버그 수정 등 실행 가능한 변경 |

예: `[PLAN] MVC 패키지 구조 정의`, `[ACTION] Controller 라우팅 구현`
