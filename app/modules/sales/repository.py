import sqlite3
from typing import Any

from app.modules.sales.constants import PAYMENT_METHODS


class SalesRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def list_reservations(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT r.*, c.name AS customer_name, c.phone AS customer_phone,
                   a.animal_code, a.name AS animal_name, a.species,
                   COALESCE((SELECT SUM(d.amount) FROM reservation_deposits d
                             WHERE d.reservation_id = r.id), 0) AS deposit_paid,
                   COALESCE((SELECT SUM(f.amount) FROM reservation_refunds f
                             WHERE f.reservation_id = r.id), 0) AS deposit_refunded
            FROM reservations r
            JOIN customers c ON c.id = r.customer_id
            JOIN animals a ON a.id = r.animal_id
            ORDER BY CASE WHEN r.status = 'ACTIVE' THEN 0 ELSE 1 END,
                     r.created_at DESC
            """
        ).fetchall()

    def list_saleable_animals(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT a.id, a.animal_code, a.name, a.species, a.sale_price, a.status,
                   r.customer_id AS reservation_customer_id
            FROM animals a
            LEFT JOIN reservations r ON r.animal_id = a.id AND r.status = 'ACTIVE'
            WHERE a.status IN ('AVAILABLE', 'RESERVED')
            ORDER BY a.animal_code
            """
        ).fetchall()

    def get_order_balance(self, order_id: int) -> float:
        row = self.connection.execute(
            """
            SELECT o.total_amount -
                COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.order_id = o.id), 0)
                AS balance
            FROM sales_orders o WHERE o.id = ?
            """,
            (order_id,),
        ).fetchone()
        if row is None:
            raise ValueError("Không tìm thấy đơn hàng.")
        return max(0.0, round(row["balance"], 2))

    def get_reservation_balance(self, reservation_id: int) -> float:
        row = self.connection.execute(
            """
            SELECT COALESCE((SELECT SUM(d.amount) FROM reservation_deposits d
                             WHERE d.reservation_id = r.id), 0) -
                   COALESCE((SELECT SUM(f.amount) FROM reservation_refunds f
                             WHERE f.reservation_id = r.id), 0) AS balance
            FROM reservations r WHERE r.id = ?
            """,
            (reservation_id,),
        ).fetchone()
        if row is None:
            raise ValueError("Không tìm thấy lượt giữ chỗ.")
        return max(0.0, round(row["balance"], 2))

    def create_reservation(self, values: dict[str, Any]) -> int:
        deposit = float(values.get("deposit", 0))
        if deposit < 0:
            raise ValueError("Tiền đặt cọc không thể âm.")
        with self.connection:
            customer = self.connection.execute(
                "SELECT id FROM customers WHERE id = ?",
                (values["customer_id"],),
            ).fetchone()
            if customer is None:
                raise ValueError("Không tìm thấy khách hàng.")
            animal = self.connection.execute(
                "SELECT status FROM animals WHERE id = ?",
                (values["animal_id"],),
            ).fetchone()
            if animal is None:
                raise ValueError("Không tìm thấy động vật.")
            if animal["status"] != "AVAILABLE":
                raise ValueError("Chỉ động vật đang bán mới có thể được giữ chỗ.")
            sale_price = self.connection.execute(
                "SELECT sale_price FROM animals WHERE id = ?",
                (values["animal_id"],),
            ).fetchone()["sale_price"]
            if deposit > sale_price:
                raise ValueError("Tiền đặt cọc không thể vượt quá giá bán.")
            cursor = self.connection.execute(
                """
                INSERT INTO reservations
                    (customer_id, animal_id, reserved_at, expires_at, deposit, note)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    values["customer_id"],
                    values["animal_id"],
                    values["reserved_at"],
                    values["expires_at"],
                    deposit,
                    str(values.get("note", "")).strip(),
                ),
            )
            reservation_id = int(cursor.lastrowid)
            self.connection.execute(
                "UPDATE animals SET status = 'RESERVED', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (values["animal_id"],),
            )
            if deposit > 0:
                self.connection.execute(
                    """
                    INSERT INTO reservation_deposits
                        (reservation_id, amount, paid_at, method, reference)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        reservation_id,
                        deposit,
                        values["reserved_at"],
                        values.get("deposit_method", "CASH"),
                        str(values.get("deposit_reference", "")).strip(),
                    ),
                )
            return reservation_id

    def release_reservation(self, reservation_id: int, status: str = "RELEASED") -> None:
        if status not in {"RELEASED", "EXPIRED"}:
            raise ValueError("Trạng thái giải phóng chỗ không hợp lệ.")
        with self.connection:
            reservation = self.connection.execute(
                """
                SELECT animal_id, status FROM reservations WHERE id = ?
                """,
                (reservation_id,),
            ).fetchone()
            if reservation is None:
                raise ValueError("Không tìm thấy lượt giữ chỗ.")
            if reservation["status"] != "ACTIVE":
                raise ValueError("Chỉ lượt giữ chỗ đang hoạt động mới được giải phóng.")
            deposit_total = self.connection.execute(
                """
                SELECT COALESCE(SUM(amount), 0)
                FROM reservation_deposits WHERE reservation_id = ?
                """,
                (reservation_id,),
            ).fetchone()[0]
            refunded_total = self.connection.execute(
                """
                SELECT COALESCE(SUM(amount), 0)
                FROM reservation_refunds WHERE reservation_id = ?
                """,
                (reservation_id,),
            ).fetchone()[0]
            if round(refunded_total, 2) < round(deposit_total, 2):
                raise ValueError("Cần hoàn đủ tiền cọc trước khi giải phóng lượt giữ chỗ.")
            self.connection.execute(
                """
                UPDATE reservations SET status = ?, closed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (status, reservation_id),
            )
            self.connection.execute(
                """
                UPDATE animals SET status = 'AVAILABLE', updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status = 'RESERVED'
                """,
                (reservation["animal_id"],),
            )

    def list_orders(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT o.*, c.customer_code, c.name AS customer_name,
                   c.phone AS customer_phone,
                   COALESCE((SELECT SUM(p.amount) FROM payments p
                             WHERE p.order_id = o.id), 0) AS paid_amount,
                   (SELECT COUNT(*) FROM order_items i WHERE i.order_id = o.id)
                       AS item_count
            FROM sales_orders o
            JOIN customers c ON c.id = o.customer_id
            ORDER BY o.created_at DESC, o.id DESC
            """
        ).fetchall()

    def list_order_items(self, order_id: int) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT i.*, a.animal_code, a.name AS animal_name, a.species
            FROM order_items i
            JOIN animals a ON a.id = i.animal_id
            WHERE i.order_id = ? ORDER BY i.id
            """,
            (order_id,),
        ).fetchall()

    def create_order(self, values: dict[str, Any]) -> int:
        order_code = str(values.get("order_code", "")).strip()
        if not order_code:
            raise ValueError("Mã đơn hàng là bắt buộc.")
        animal_ids = list(dict.fromkeys(values["animal_ids"]))
        if not animal_ids:
            raise ValueError("Đơn hàng phải có ít nhất một động vật.")
        with self.connection:
            customer = self.connection.execute(
                "SELECT id FROM customers WHERE id = ?",
                (values["customer_id"],),
            ).fetchone()
            if customer is None:
                raise ValueError("Không tìm thấy khách hàng.")
            cursor = self.connection.execute(
                """
                INSERT INTO sales_orders
                    (order_code, customer_id, ordered_at, status, note)
                VALUES (?, ?, ?, 'OPEN', ?)
                """,
                (
                    order_code,
                    values["customer_id"],
                    values["ordered_at"],
                    str(values.get("note", "")).strip(),
                ),
            )
            order_id = int(cursor.lastrowid)
            total = 0.0
            for animal_id in animal_ids:
                animal = self.connection.execute(
                    """
                    SELECT a.id, a.status, a.sale_price, r.customer_id, r.status AS reservation_status
                    FROM animals a
                    LEFT JOIN reservations r ON r.animal_id = a.id AND r.status = 'ACTIVE'
                    WHERE a.id = ?
                    """,
                    (animal_id,),
                ).fetchone()
                if animal is None:
                    raise ValueError(f"Không tìm thấy động vật mã cơ sở dữ liệu {animal_id}.")
                if animal["status"] == "AVAILABLE":
                    pass
                elif (
                    animal["status"] == "RESERVED"
                    and animal["customer_id"] == values["customer_id"]
                    and animal["reservation_status"] == "ACTIVE"
                ):
                    pass
                else:
                    raise ValueError(
                        f"Động vật {animal_id} không còn sẵn sàng bán cho khách hàng này."
                    )
                price = float(animal["sale_price"])
                if price < 0:
                    raise ValueError("Giá bán không thể âm.")
                self.connection.execute(
                    """
                    INSERT INTO order_items (order_id, animal_id, unit_price)
                    VALUES (?, ?, ?)
                    """,
                    (order_id, animal_id, price),
                )
                self.connection.execute(
                    "UPDATE animals SET status = 'RESERVED', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (animal_id,),
                )
                active_reservation = self.connection.execute(
                    """
                    SELECT id FROM reservations
                    WHERE animal_id = ? AND customer_id = ? AND status = 'ACTIVE'
                    """,
                    (animal_id, values["customer_id"]),
                ).fetchone()
                if active_reservation:
                    deposit = self.connection.execute(
                        """
                        SELECT COALESCE(SUM(amount), 0)
                        FROM reservation_deposits WHERE reservation_id = ?
                        """,
                        (active_reservation["id"],),
                    ).fetchone()[0]
                    if deposit:
                        self.connection.execute(
                            """
                            INSERT INTO payments
                                (order_id, amount, method, paid_at, reference, note)
                            SELECT ?, amount, method, paid_at, reference,
                                   'Tiền cọc từ lượt giữ chỗ'
                            FROM reservation_deposits WHERE reservation_id = ?
                            """,
                            (order_id, active_reservation["id"]),
                        )
                    self.connection.execute(
                        """
                        UPDATE reservations SET status = 'CONVERTED',
                            closed_at = CURRENT_TIMESTAMP, order_id = ?
                        WHERE id = ?
                        """,
                        (order_id, active_reservation["id"]),
                    )
                total += price
            self.connection.execute(
                "UPDATE sales_orders SET total_amount = ? WHERE id = ?",
                (total, order_id),
            )
            initial_paid = self.connection.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE order_id = ?",
                (order_id,),
            ).fetchone()[0]
            if initial_paid >= total:
                self.connection.execute(
                    """
                    UPDATE sales_orders SET status = 'PAID', paid_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (order_id,),
                )
                self.connection.execute(
                    """
                    UPDATE animals SET status = 'SOLD', updated_at = CURRENT_TIMESTAMP
                    WHERE id IN (SELECT animal_id FROM order_items WHERE order_id = ?)
                    """,
                    (order_id,),
                )
            elif initial_paid > 0:
                self.connection.execute(
                    "UPDATE sales_orders SET status = 'PARTIALLY_PAID' WHERE id = ?",
                    (order_id,),
                )
            return order_id

    def add_payment(self, order_id: int, values: dict[str, Any]) -> int:
        amount = float(values["amount"])
        if amount <= 0:
            raise ValueError("Số tiền thanh toán phải lớn hơn 0.")
        method = values["method"]
        if method not in PAYMENT_METHODS:
            raise ValueError("Phương thức thanh toán không hợp lệ.")
        with self.connection:
            order = self.connection.execute(
                "SELECT total_amount, status FROM sales_orders WHERE id = ?",
                (order_id,),
            ).fetchone()
            if order is None:
                raise ValueError("Không tìm thấy đơn hàng.")
            if order["status"] in {"PAID", "CANCELLED"}:
                raise ValueError("Đơn hàng đã thanh toán xong hoặc đã hủy.")
            paid = self.connection.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE order_id = ?",
                (order_id,),
            ).fetchone()[0]
            balance = round(order["total_amount"] - paid, 2)
            if amount > balance:
                raise ValueError(f"Số tiền vượt quá công nợ còn lại ({balance:.2f}).")
            cursor = self.connection.execute(
                """
                INSERT INTO payments
                    (order_id, amount, method, paid_at, reference, note)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    amount,
                    method,
                    values["paid_at"],
                    str(values.get("reference", "")).strip(),
                    str(values.get("note", "")).strip(),
                ),
            )
            new_paid = round(paid + amount, 2)
            if new_paid >= round(order["total_amount"], 2):
                self.connection.execute(
                    "UPDATE sales_orders SET status = 'PAID', paid_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (order_id,),
                )
                self.connection.execute(
                    """
                    UPDATE animals SET status = 'SOLD', updated_at = CURRENT_TIMESTAMP
                    WHERE id IN (SELECT animal_id FROM order_items WHERE order_id = ?)
                    """,
                    (order_id,),
                )
            else:
                self.connection.execute(
                    "UPDATE sales_orders SET status = 'PARTIALLY_PAID' WHERE id = ?",
                    (order_id,),
                )
            return int(cursor.lastrowid)

    def cancel_unpaid_order(self, order_id: int) -> None:
        with self.connection:
            order = self.connection.execute(
                "SELECT status FROM sales_orders WHERE id = ?", (order_id,)
            ).fetchone()
            if order is None:
                raise ValueError("Không tìm thấy đơn hàng.")
            if order["status"] != "OPEN":
                raise ValueError(
                    "Chỉ hủy được đơn chưa thanh toán; đơn đã có thanh toán cần xử lý hoàn tiền."
                )
            self.connection.execute(
                "UPDATE sales_orders SET status = 'CANCELLED' WHERE id = ?",
                (order_id,),
            )
            self.connection.execute(
                """
                UPDATE animals SET status = 'AVAILABLE', updated_at = CURRENT_TIMESTAMP
                WHERE id IN (SELECT animal_id FROM order_items WHERE order_id = ?)
                  AND status = 'RESERVED'
                """,
                (order_id,),
            )

    def list_payments(self, order_id: int) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT * FROM payments WHERE order_id = ? ORDER BY paid_at DESC, id DESC
            """,
            (order_id,),
        ).fetchall()

    def list_reservation_deposits(self, reservation_id: int) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT * FROM reservation_deposits
            WHERE reservation_id = ? ORDER BY paid_at, id
            """,
            (reservation_id,),
        ).fetchall()

    def refund_reservation_deposit(
        self, reservation_id: int, values: dict[str, Any]
    ) -> int:
        amount = float(values["amount"])
        if amount <= 0:
            raise ValueError("Số tiền hoàn cọc phải lớn hơn 0.")
        if values["method"] not in PAYMENT_METHODS:
            raise ValueError("Phương thức hoàn tiền không hợp lệ.")
        with self.connection:
            reservation = self.connection.execute(
                """
                SELECT status FROM reservations WHERE id = ?
                """,
                (reservation_id,),
            ).fetchone()
            if reservation is None:
                raise ValueError("Không tìm thấy lượt giữ chỗ.")
            if reservation["status"] != "ACTIVE":
                raise ValueError("Chỉ lượt giữ chỗ đang hoạt động mới được hoàn cọc.")
            deposited = self.connection.execute(
                """
                SELECT COALESCE(SUM(amount), 0) FROM reservation_deposits
                WHERE reservation_id = ?
                """,
                (reservation_id,),
            ).fetchone()[0]
            refunded = self.connection.execute(
                """
                SELECT COALESCE(SUM(amount), 0) FROM reservation_refunds
                WHERE reservation_id = ?
                """,
                (reservation_id,),
            ).fetchone()[0]
            remaining = round(deposited - refunded, 2)
            if amount > remaining:
                raise ValueError(f"Số tiền vượt quá cọc chưa hoàn ({remaining:.2f}).")
            cursor = self.connection.execute(
                """
                INSERT INTO reservation_refunds
                    (reservation_id, amount, refunded_at, method, reference, note)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    reservation_id,
                    amount,
                    values["refunded_at"],
                    values["method"],
                    str(values.get("reference", "")).strip(),
                    str(values.get("note", "")).strip(),
                ),
            )
            return int(cursor.lastrowid)

    def list_reservation_refunds(self, reservation_id: int) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT * FROM reservation_refunds
            WHERE reservation_id = ? ORDER BY refunded_at, id
            """,
            (reservation_id,),
        ).fetchall()
