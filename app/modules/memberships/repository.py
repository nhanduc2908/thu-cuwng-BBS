import secrets
import sqlite3
from datetime import date, timedelta
from typing import Any

from app.modules.sales.constants import PAYMENT_METHODS
from app.modules.services.constants import MEMBERSHIP_MODES, SERVICE_CATEGORIES


class MembershipRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def list_plans(self, include_inactive: bool = True) -> list[sqlite3.Row]:
        query = "SELECT * FROM membership_plans"
        if not include_inactive:
            query += " WHERE is_active = 1"
        return self.connection.execute(query + " ORDER BY price, name").fetchall()

    def save_plan(self, values: dict[str, Any], plan_id: int | None = None) -> int:
        code = str(values.get("code", "")).strip().upper()
        name = str(values.get("name", "")).strip()
        duration = int(values.get("duration_days", 0))
        price = float(values.get("price", -1))
        discount = float(values.get("discount_percent", 0))
        points = float(values.get("points_rate", 1))
        max_pets = int(values.get("max_pets", 1))
        billing_mode = str(values.get("billing_mode", "MEMBER_DISCOUNT"))
        included_visits = int(values.get("included_visits", 0))
        service_category = str(values.get("service_category", "")).strip().upper()
        if not code or not name:
            raise ValueError("Mã và tên gói hội viên là bắt buộc.")
        if duration <= 0 or price < 0 or not 0 <= discount <= 100:
            raise ValueError("Thời hạn, giá hoặc tỷ lệ giảm giá không hợp lệ.")
        if points < 0 or max_pets <= 0:
            raise ValueError("Tỷ lệ điểm và số thú cưng không hợp lệ.")
        if billing_mode not in MEMBERSHIP_MODES:
            raise ValueError("Kiểu gói hội viên không hợp lệ.")
        if included_visits < 0:
            raise ValueError("Số lượt sử dụng không thể âm.")
        if billing_mode == "PREPAID_VISITS" and included_visits <= 0:
            raise ValueError("Gói trả trước phải có ít nhất một lượt sử dụng.")
        if service_category and service_category not in SERVICE_CATEGORIES:
            raise ValueError("Nhóm dịch vụ áp dụng cho gói hội viên không hợp lệ.")
        fields = (
            code,
            name,
            str(values.get("description", "")).strip(),
            duration,
            price,
            discount,
            points,
            str(values.get("benefits", "")).strip(),
            max_pets,
            billing_mode,
            included_visits,
            service_category,
            int(bool(values.get("is_active", True))),
        )
        with self.connection:
            if plan_id is None:
                cursor = self.connection.execute(
                    """
                    INSERT INTO membership_plans
                        (code, name, description, duration_days, price,
                         discount_percent, points_rate, benefits, max_pets,
                         billing_mode, included_visits, service_category, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    fields,
                )
                return int(cursor.lastrowid)
            cursor = self.connection.execute(
                """
                UPDATE membership_plans SET code = ?, name = ?, description = ?,
                    duration_days = ?, price = ?, discount_percent = ?,
                    points_rate = ?, benefits = ?, max_pets = ?, billing_mode = ?,
                    included_visits = ?, service_category = ?, is_active = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (*fields, plan_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("Không tìm thấy gói hội viên.")
            return plan_id

    def list_memberships(self, search: str = "") -> list[sqlite3.Row]:
        query = """
            SELECT m.*, c.name AS customer_name, c.customer_code, c.phone,
                   p.name AS plan_name, p.code AS plan_code,
                   card.card_number,
                   CASE WHEN card.status = 'ACTIVE'
                                  AND card.expiry_date < date('now', 'localtime')
                        THEN 'EXPIRED' ELSE card.status END AS card_status,
                   card.expiry_date AS card_expiry,
                   CASE WHEN m.status = 'ACTIVE' AND m.end_date < date('now', 'localtime')
                        THEN 'EXPIRED' ELSE m.status END AS display_status,
                   (SELECT COUNT(*) FROM bills b WHERE b.membership_id = m.id)
                       AS bill_count
            FROM memberships m
            JOIN customers c ON c.id = m.customer_id
            JOIN membership_plans p ON p.id = m.plan_id
            LEFT JOIN membership_cards card ON card.id = (
                SELECT mc.id FROM membership_cards mc
                WHERE mc.membership_id = m.id
                ORDER BY mc.id DESC LIMIT 1
            )
        """
        parameters: tuple[str, ...] = ()
        if search.strip():
            pattern = f"%{search.strip()}%"
            query += """
                WHERE c.name LIKE ? OR c.phone LIKE ? OR c.customer_code LIKE ?
                   OR m.membership_code LIKE ? OR card.card_number LIKE ?
            """
            parameters = (pattern, pattern, pattern, pattern, pattern)
        return self.connection.execute(
            query + " ORDER BY m.created_at DESC, m.id DESC", parameters
        ).fetchall()

    def list_bills(self, search: str = "") -> list[sqlite3.Row]:
        query = """
            SELECT b.*, c.name AS customer_name, c.customer_code,
                   COALESCE(SUM(p.amount), 0) AS amount_paid,
                   MAX(p.paid_at) AS last_paid_at
            FROM bills b
            JOIN customers c ON c.id = b.customer_id
            LEFT JOIN bill_payments p ON p.bill_id = b.id
        """
        parameters: tuple[str, ...] = ()
        if search.strip():
            pattern = f"%{search.strip()}%"
            query += " WHERE b.bill_number LIKE ? OR c.name LIKE ? OR c.customer_code LIKE ?"
            parameters = (pattern, pattern, pattern)
        query += " GROUP BY b.id ORDER BY b.issued_at DESC, b.id DESC"
        return self.connection.execute(query, parameters).fetchall()

    def list_bill_payments(self, bill_id: int) -> list[sqlite3.Row]:
        return self.connection.execute(
            "SELECT * FROM bill_payments WHERE bill_id = ? ORDER BY paid_at, id",
            (bill_id,),
        ).fetchall()

    def create_membership(
        self, customer_id: int, plan_id: int, issued_at: str | None = None
    ) -> int:
        start = date.fromisoformat(issued_at) if issued_at else date.today()
        with self.connection:
            customer = self.connection.execute(
                "SELECT id FROM customers WHERE id = ?", (customer_id,)
            ).fetchone()
            plan = self.connection.execute(
                "SELECT * FROM membership_plans WHERE id = ? AND is_active = 1",
                (plan_id,),
            ).fetchone()
            if customer is None:
                raise ValueError("Không tìm thấy khách hàng.")
            if plan is None:
                raise ValueError("Gói hội viên không tồn tại hoặc đã ngừng hoạt động.")
            membership_code = self._next_code("PT", start.year, "memberships")
            end = start + timedelta(days=plan["duration_days"] - 1)
            cursor = self.connection.execute(
                """
                INSERT INTO memberships
                    (customer_id, plan_id, membership_code, start_date, end_date, status)
                VALUES (?, ?, ?, ?, ?, 'PENDING_PAYMENT')
                """,
                (customer_id, plan_id, membership_code, start.isoformat(), end.isoformat()),
            )
            membership_id = int(cursor.lastrowid)
            card_cursor = self.connection.execute(
                """
                INSERT INTO membership_cards
                    (customer_id, membership_id, card_number, card_token,
                     issue_date, expiry_date, status)
                VALUES (?, ?, ?, ?, ?, ?, 'PENDING')
                """,
                (
                    customer_id,
                    membership_id,
                    self._next_code("CARD", start.year, "membership_cards"),
                    secrets.token_urlsafe(32),
                    start.isoformat(),
                    end.isoformat(),
                ),
            )
            self._record_card_history(int(card_cursor.lastrowid), "PENDING", "Chờ thanh toán gói hội viên.")
            bill_id = self._create_bill(
                customer_id,
                membership_id,
                "MEMBERSHIP",
                plan["price"],
                plan["name"],
                0,
                start.isoformat(),
            )
            if float(plan["price"]) == 0:
                self.connection.execute(
                    "UPDATE memberships SET status = 'ACTIVE' WHERE id = ?",
                    (membership_id,),
                )
                self.connection.execute(
                    """
                    UPDATE membership_cards SET status = 'ACTIVE',
                        activation_date = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE membership_id = ?
                    """,
                    (start.isoformat(), membership_id),
                )
                self.connection.execute(
                    "UPDATE bills SET status = 'PAID', paid_at = ? WHERE id = ?",
                    (start.isoformat(), bill_id),
                )
                card = self.connection.execute(
                    "SELECT id FROM membership_cards WHERE membership_id = ?",
                    (membership_id,),
                ).fetchone()
                self._record_card_history(int(card["id"]), "ACTIVE", "Gói miễn phí.")
            return membership_id

    def create_renewal_bill(
        self, membership_id: int, issued_at: str | None = None
    ) -> int:
        issue_date = date.fromisoformat(issued_at) if issued_at else date.today()
        with self.connection:
            membership = self.connection.execute(
                """
                SELECT m.*, p.name AS plan_name, p.price, p.duration_days
                FROM memberships m JOIN membership_plans p ON p.id = m.plan_id
                WHERE m.id = ?
                """,
                (membership_id,),
            ).fetchone()
            if membership is None:
                raise ValueError("Không tìm thấy hội viên.")
            if membership["status"] in {"PENDING_PAYMENT", "SUSPENDED", "CANCELLED"}:
                raise ValueError("Trạng thái hội viên hiện tại không cho phép gia hạn.")
            pending_bill = self.connection.execute(
                """
                SELECT id FROM bills WHERE membership_id = ?
                  AND bill_type = 'RENEWAL'
                  AND status IN ('PENDING', 'PARTIALLY_PAID')
                LIMIT 1
                """,
                (membership_id,),
            ).fetchone()
            if pending_bill is not None:
                raise ValueError("Hội viên đã có bill gia hạn chưa thanh toán.")
            return self._create_bill(
                membership["customer_id"],
                membership_id,
                "RENEWAL",
                membership["price"],
                f"Gia hạn {membership['plan_name']}",
                membership["duration_days"],
                issue_date.isoformat(),
            )

    def add_bill_payment(
        self, bill_id: int, values: dict[str, Any]
    ) -> int:
        amount = round(float(values.get("amount", 0)), 2)
        method = str(values.get("method", ""))
        if amount <= 0:
            raise ValueError("Số tiền thanh toán phải lớn hơn 0.")
        if method not in PAYMENT_METHODS:
            raise ValueError("Phương thức thanh toán không hợp lệ.")
        paid_at = str(values.get("paid_at", date.today().isoformat())).strip()
        try:
            date.fromisoformat(paid_at)
        except ValueError as error:
            raise ValueError("Ngày thanh toán không hợp lệ.") from error

        with self.connection:
            bill = self.connection.execute(
                "SELECT * FROM bills WHERE id = ?", (bill_id,)
            ).fetchone()
            if bill is None:
                raise ValueError("Không tìm thấy bill.")
            if bill["status"] in {"PAID", "CANCELLED"}:
                raise ValueError("Bill đã thanh toán đủ hoặc đã hủy.")
            paid = float(
                self.connection.execute(
                    "SELECT COALESCE(SUM(amount), 0) FROM bill_payments WHERE bill_id = ?",
                    (bill_id,),
                ).fetchone()[0]
            )
            balance = round(float(bill["total_amount"]) - paid, 2)
            if amount > balance:
                raise ValueError(f"Số tiền vượt quá số dư còn lại ({balance:,.0f} VND).")
            payment_code = self._next_code("PAY", date.today().year, "bill_payments")
            cursor = self.connection.execute(
                """
                INSERT INTO bill_payments
                    (bill_id, payment_code, payment_method, amount, reference, note, paid_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    bill_id,
                    payment_code,
                    method,
                    amount,
                    str(values.get("reference", "")).strip(),
                    str(values.get("note", "")).strip(),
                    paid_at,
                ),
            )
            new_paid = round(paid + amount, 2)
            if new_paid >= round(float(bill["total_amount"]), 2):
                self.connection.execute(
                    """
                    UPDATE bills SET status = 'PAID', paid_at = ?,
                        updated_at = CURRENT_TIMESTAMP WHERE id = ?
                    """,
                    (paid_at, bill_id),
                )
                if bill["membership_id"] is not None:
                    self._activate_or_renew_membership(bill, paid_at)
            else:
                self.connection.execute(
                    "UPDATE bills SET status = 'PARTIALLY_PAID', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (bill_id,),
                )
            return int(cursor.lastrowid)

    def verify_card(self, token: str) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT card.card_number,
                   CASE WHEN card.status = 'ACTIVE'
                                  AND card.expiry_date >= date('now', 'localtime')
                                  AND membership.status = 'ACTIVE'
                        THEN 'ACTIVE'
                        WHEN card.expiry_date < date('now', 'localtime') THEN 'EXPIRED'
                        ELSE card.status END AS status,
                   card.expiry_date, plan.name AS plan_name
            FROM membership_cards card
            JOIN memberships membership ON membership.id = card.membership_id
            JOIN membership_plans plan ON plan.id = membership.plan_id
            WHERE card.card_token = ?
            """,
            (token,),
        ).fetchone()

    def _activate_or_renew_membership(
        self, bill: sqlite3.Row, paid_at: str
    ) -> None:
        membership_id = int(bill["membership_id"])
        membership = self.connection.execute(
            "SELECT * FROM memberships WHERE id = ?", (membership_id,)
        ).fetchone()
        if bill["bill_type"] == "RENEWAL":
            current_end = date.fromisoformat(membership["end_date"])
            effective_start = max(current_end + timedelta(days=1), date.fromisoformat(paid_at))
            end = effective_start + timedelta(days=int(bill["renewal_days"]) - 1)
            self.connection.execute(
                """
                UPDATE memberships SET end_date = ?, status = 'ACTIVE',
                    renewal_count = renewal_count + 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (end.isoformat(), membership_id),
            )
        else:
            end = date.fromisoformat(membership["end_date"])
            self.connection.execute(
                "UPDATE memberships SET status = 'ACTIVE', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (membership_id,),
            )
        cards = self.connection.execute(
            """
            SELECT id, status FROM membership_cards
            WHERE membership_id = ? AND status IN ('PENDING', 'ACTIVE', 'EXPIRED')
            ORDER BY id DESC LIMIT 1
            """,
            (membership_id,),
        ).fetchone()
        if cards is not None:
            self.connection.execute(
                """
                UPDATE membership_cards SET status = 'ACTIVE', activation_date = COALESCE(
                    activation_date, ?), expiry_date = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (paid_at, end.isoformat(), cards["id"]),
            )
            if cards["status"] != "ACTIVE" or bill["bill_type"] == "RENEWAL":
                note = (
                    f"Gia hạn thẻ đến {end.isoformat()}."
                    if bill["bill_type"] == "RENEWAL"
                    else "Bill thanh toán đầy đủ."
                )
                self._record_card_history(int(cards["id"]), "ACTIVE", note)

    def _create_bill(
        self,
        customer_id: int,
        membership_id: int,
        bill_type: str,
        amount: float,
        item_name: str,
        renewal_days: int,
        issued_at: str,
    ) -> int:
        year = date.fromisoformat(issued_at).year
        bill_number = self._next_code("BILL", year, "bills")
        cursor = self.connection.execute(
            """
            INSERT INTO bills
                (bill_number, customer_id, membership_id, bill_type, subtotal,
                 total_amount, issued_at, renewal_days)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (bill_number, customer_id, membership_id, bill_type, amount, amount, issued_at, renewal_days),
        )
        bill_id = int(cursor.lastrowid)
        self.connection.execute(
            """
            INSERT INTO bill_items (bill_id, item_name, quantity, unit_price, total)
            VALUES (?, ?, 1, ?, ?)
            """,
            (bill_id, item_name, amount, amount),
        )
        return bill_id

    def _next_code(self, prefix: str, year: int, table: str) -> str:
        count = int(self.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
        return f"{prefix}-{year}-{count + 1:08d}"

    def _record_card_history(self, card_id: int, status: str, note: str) -> None:
        self.connection.execute(
            "INSERT INTO membership_card_history (card_id, status, note) VALUES (?, ?, ?)",
            (card_id, status, note),
        )
