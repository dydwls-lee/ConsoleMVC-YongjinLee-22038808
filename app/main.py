"""Main loop entry point.

Wires Model (repositories / production queue), Controller and View
together, and routes the user's menu selection to the matching
sub-menu loop. This module owns the only console I/O calls that
originate outside `view/`, and it delegates every actual print/input
to `view.console_io.ConsoleIO` so behaviour stays testable.
"""

from __future__ import annotations

from datetime import datetime
from typing import Callable

from controller.approval_controller import ApprovalController
from controller.history_controller import HistoryController
from controller.monitor_controller import MonitorController
from controller.order_controller import OrderController
from controller.production_controller import ProductionController
from controller.release_controller import ReleaseController
from controller.sample_controller import SampleController
from controller.summary_controller import SummaryController
from model.production import ProductionQueue
from model.repository import InMemoryOrderRepository, InMemorySampleRepository
from view import formatters
from view.console_io import ConsoleIO


class App:
    def __init__(self, io: ConsoleIO | None = None, clock: Callable[[], datetime] = datetime.now) -> None:
        self.io = io or ConsoleIO()

        self.sample_repo = InMemorySampleRepository()
        self.order_repo = InMemoryOrderRepository()
        self.production_queue = ProductionQueue()

        self.sample_controller = SampleController(self.sample_repo)
        self.order_controller = OrderController(self.order_repo, self.sample_repo, clock=clock)
        self.approval_controller = ApprovalController(
            self.order_repo, self.sample_repo, self.production_queue
        )
        self.monitor_controller = MonitorController(self.order_repo, self.sample_repo)
        self.production_controller = ProductionController(self.production_queue)
        self.release_controller = ReleaseController(self.order_repo)
        self.summary_controller = SummaryController(
            self.sample_repo, self.order_repo, self.production_queue
        )
        self.history_controller = HistoryController(self.order_repo)

        self._main_actions = {
            "1": self._sample_menu,
            "2": self._order_menu,
            "3": self._approval_menu,
            "4": self._monitor_menu,
            "5": self._production_menu,
            "6": self._release_menu,
        }

    def run(self) -> None:
        while True:
            summary = self.summary_controller.summarize()
            self.io.show(formatters.render_main_menu(summary))
            choice = self.io.prompt("메뉴 번호를 선택하세요: ")
            if choice == "0":
                self.io.show("프로그램을 종료합니다.")
                return
            action = self._main_actions.get(choice)
            if action is None:
                self.io.show_error("올바른 메뉴 번호를 입력하세요.")
                continue
            action()

    # -- 시료 관리 -----------------------------------------------------
    def _sample_menu(self) -> None:
        while True:
            self.io.show("[시료 관리] 1.등록 2.전체조회 3.이름검색 0.뒤로가기")
            choice = self.io.prompt("선택: ")
            if choice == "0":
                return
            if choice == "1":
                self._register_sample()
            elif choice == "2":
                self.io.show(formatters.render_samples(self.sample_controller.list_all()))
            elif choice == "3":
                keyword = self.io.prompt("검색어(이름): ")
                self.io.show(formatters.render_samples(self.sample_controller.search_by_name(keyword)))
            else:
                self.io.show_error("올바른 메뉴 번호를 입력하세요.")

    def _register_sample(self) -> None:
        try:
            sample_id = self.io.prompt("시료 ID: ")
            name = self.io.prompt("시료명: ")
            avg_time = float(self.io.prompt("평균 생산시간(min/ea): "))
            yield_rate = float(self.io.prompt("수율(0~1): "))
            result = self.sample_controller.register(sample_id, name, avg_time, yield_rate)
            self.io.show(f"등록 완료: {result}")
        except ValueError as e:
            self.io.show_error(str(e))

    # -- 시료 주문 -----------------------------------------------------
    def _order_menu(self) -> None:
        while True:
            self.io.show("[시료 주문] 1.주문접수 2.전체 주문 조회 0.뒤로가기")
            choice = self.io.prompt("선택: ")
            if choice == "0":
                return
            if choice == "1":
                self._place_order()
            elif choice == "2":
                self.io.show(formatters.render_orders(self.history_controller.list_all()))
            else:
                self.io.show_error("올바른 메뉴 번호를 입력하세요.")

    def _place_order(self) -> None:
        try:
            sample_id = self.io.prompt("시료 ID: ")
            customer_name = self.io.prompt("고객명: ")
            quantity = int(self.io.prompt("수량: "))
            result = self.order_controller.place_order(sample_id, customer_name, quantity)
            self.io.show(f"주문 접수 완료: {result}")
        except ValueError as e:
            self.io.show_error(str(e))

    # -- 주문 승인/거절 -------------------------------------------------
    def _approval_menu(self) -> None:
        while True:
            self.io.show("[주문 승인/거절] 1.RESERVED목록 2.승인 3.거절 0.뒤로가기")
            choice = self.io.prompt("선택: ")
            if choice == "0":
                return
            if choice == "1":
                self.io.show(formatters.render_orders(self.approval_controller.list_reserved()))
            elif choice == "2":
                self._approve_order()
            elif choice == "3":
                self._reject_order()
            else:
                self.io.show_error("올바른 메뉴 번호를 입력하세요.")

    def _approve_order(self) -> None:
        try:
            order_id = self.io.prompt("승인할 주문번호: ")
            result = self.approval_controller.approve(order_id)
            self.io.show(f"승인 처리 완료: {result['status']}")
        except ValueError as e:
            self.io.show_error(str(e))

    def _reject_order(self) -> None:
        try:
            order_id = self.io.prompt("거절할 주문번호: ")
            result = self.approval_controller.reject(order_id)
            self.io.show(f"거절 처리 완료: {result['status']}")
        except ValueError as e:
            self.io.show_error(str(e))

    # -- 모니터링 -------------------------------------------------------
    def _monitor_menu(self) -> None:
        while True:
            self.io.show("[모니터링] 1.상태별 주문 수 2.재고 현황 0.뒤로가기")
            choice = self.io.prompt("선택: ")
            if choice == "0":
                return
            if choice == "1":
                self.io.show(formatters.render_status_counts(self.monitor_controller.status_counts()))
            elif choice == "2":
                self.io.show(formatters.render_stock_status(self.monitor_controller.stock_status()))
            else:
                self.io.show_error("올바른 메뉴 번호를 입력하세요.")

    # -- 생산라인 조회 ---------------------------------------------------
    def _production_menu(self) -> None:
        while True:
            self.io.show("[생산라인 조회] 1.현황 조회 0.뒤로가기")
            choice = self.io.prompt("선택: ")
            if choice == "0":
                return
            if choice == "1":
                self.io.show(
                    formatters.render_production_queue(
                        self.production_controller.current_job(),
                        self.production_controller.pending_jobs(),
                    )
                )
            else:
                self.io.show_error("올바른 메뉴 번호를 입력하세요.")

    # -- 출고 처리 -------------------------------------------------------
    def _release_menu(self) -> None:
        while True:
            self.io.show("[출고 처리] 1.CONFIRMED목록 2.출고 0.뒤로가기")
            choice = self.io.prompt("선택: ")
            if choice == "0":
                return
            if choice == "1":
                self.io.show(formatters.render_orders(self.release_controller.list_confirmed()))
            elif choice == "2":
                self._release_order()
            else:
                self.io.show_error("올바른 메뉴 번호를 입력하세요.")

    def _release_order(self) -> None:
        try:
            order_id = self.io.prompt("출고할 주문번호: ")
            result = self.release_controller.release(order_id)
            self.io.show(f"출고 처리 완료: {result['status']}")
        except ValueError as e:
            self.io.show_error(str(e))


if __name__ == "__main__":
    App().run()
