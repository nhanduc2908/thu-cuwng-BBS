import math
import sqlite3
from datetime import date
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
                   + (SELECT COUNT(*) FROM sales_product_items pi
                      WHERE pi.order_id = o.id AND pi.combo_id IS NULL)
                   + (SELECT COUNT(DISTINCT pi.combo_id) FROM sales_product_items pi
                      WHERE pi.order_id = o.id AND pi.combo_id IS NOT NULL)
                       AS item_count
            FROM sales_orders o
            JOIN customers c ON c.id = o.customer_id
            ORDER BY o.created_at DESC, o.id DESC
            """
        ).fetchall()

    def list_order_product_items(self, order_id: int) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT pi.*, i.item_code, i.unit, i.pack_size, c.combo_code
            FROM sales_product_items pi
            JOIN inventory_items i ON i.id = pi.item_id
            LEFT JOIN product_combos c ON c.id = pi.combo_id
            WHERE pi.order_id = ?
            ORDER BY pi.id
            """,
            (order_id,),
        ).fetchall()

    def list_saleable_products(self, customer_id: int) -> list[dict[str, Any]]:
        member = self.connection.execute(
            """
            SELECT p.discount_percent
            FROM memberships m JOIN membership_plans p ON p.id = m.plan_id
            WHERE m.customer_id = ? AND m.status = 'ACTIVE'
              AND m.start_date <= date('now', 'localtime')
              AND m.end_date >= date('now', 'localtime')
            ORDER BY m.end_date DESC, m.id DESC LIMIT 1
            """,
            (customer_id,),
        ).fetchone()
        discount = float(member["discount_percent"]) if member else 0
        products = self.connection.execute(
            """
            SELECT i.*,
                   COALESCE(SUM(CASE
                       WHEN b.expiry_date IS NULL
                         OR b.expiry_date >= date('now', 'localtime')
                       THEN b.quantity_remaining ELSE 0 END), 0) AS usable,
                   COALESCE((SELECT SUM(pi.quantity)
                             FROM sales_product_items pi
                             JOIN sales_orders o ON o.id = pi.order_id
                             WHERE pi.item_id = i.id
                               AND o.status IN ('OPEN', 'PARTIALLY_PAID')), 0) AS reserved
            FROM inventory_items i
            LEFT JOIN inventory_batches b ON b.item_id = i.id
            WHERE i.is_active = 1 AND i.retail_price > 0
            GROUP BY i.id
            ORDER BY i.catalog_category, i.name COLLATE NOCASE
            """
        ).fetchall()
        result: list[dict[str, Any]] = []
        for product in products:
            product_values = dict(product)
            product_values["sale_price"] = self._effective_price(
                float(product["retail_price"]),
                product["member_price"],
                float(product["promotion_percent"]),
                discount,
                member is not None,
            )
            product_values["available"] = max(
                0, float(product["usable"]) - float(product["reserved"])
            )
            result.append(product_values)
        return result

    def list_saleable_combos(self, customer_id: int) -> list[dict[str, Any]]:
        member = self.connection.execute(
            """
            SELECT p.discount_percent
            FROM memberships m JOIN membership_plans p ON p.id = m.plan_id
            WHERE m.customer_id = ? AND m.status = 'ACTIVE'
              AND m.start_date <= date('now', 'localtime')
              AND m.end_date >= date('now', 'localtime')
            ORDER BY m.end_date DESC, m.id DESC LIMIT 1
            """,
            (customer_id,),
        ).fetchone()
        discount = float(member["discount_percent"]) if member else 0
        combos = self.connection.execute(
            "SELECT * FROM product_combos WHERE is_active = 1 ORDER BY name"
        ).fetchall()
        result: list[dict[str, Any]] = []
        for combo in combos:
            components = self.connection.execute(
                """
                SELECT ci.item_id, ci.quantity, i.is_active,
                       COALESCE(SUM(CASE
                           WHEN b.expiry_date IS NULL
                             OR b.expiry_date >= date('now', 'localtime')
                           THEN b.quantity_remaining ELSE 0 END), 0) AS usable,
                       COALESCE((SELECT SUM(pi.quantity)
                                 FROM sales_product_items pi
                                 JOIN sales_orders o ON o.id = pi.order_id
                                 WHERE pi.item_id = ci.item_id
                                   AND o.status IN ('OPEN', 'PARTIALLY_PAID')), 0) AS reserved
                FROM product_combo_items ci
                JOIN inventory_items i ON i.id = ci.item_id
                LEFT JOIN inventory_batches b ON b.item_id = i.id
                WHERE ci.combo_id = ?
                GROUP BY ci.item_id
                """,
                (combo["id"],),
            ).fetchall()
            quantities_available = [
                (float(component["usable"]) - float(component["reserved"]))
                / float(component["quantity"])
                for component in components
                if component["is_active"] and float(component["quantity"]) > 0
            ]
            max_quantity = (
                min(quantities_available)
                if len(quantities_available) == len(components)
                and quantities_available
                else 0.0
            )
            available = bool(components) and max_quantity >= 1
            available = available and all(
                bool(component["is_active"])
                and float(component["usable"]) - float(component["reserved"])
                >= float(component["quantity"])
                for component in components
            )
            combo_values = dict(combo)
            combo_values["available"] = available
            combo_values["max_quantity"] = max_quantity
            combo_values["component_count"] = len(components)
            combo_values["sale_price"] = self._effective_price(
                float(combo["sale_price"]),
                combo["member_price"],
                float(combo["promotion_percent"]),
                discount,
                member is not None,
            )
            result.append(combo_values)
        return result

    def create_product_order(self, values: dict[str, Any]) -> int:
        order_code = str(values.get("order_code", "")).strip()
        if not order_code:
            raise ValueError("Mã đơn hàng là bắt buộc.")
        product_lines = values.get("product_lines", [])
        combo_lines = values.get("combo_lines", [])
        if not product_lines and not combo_lines:
            raise ValueError("Hãy chọn ít nhất một sản phẩm hoặc combo.")
        ordered_at = str(values.get("ordered_at", "")).strip()
        try:
            order_date = date.fromisoformat(ordered_at)
        except ValueError as error:
            raise ValueError("Ngày bán không hợp lệ.") from error

        with self.connection:
            customer = self.connection.execute(
                "SELECT id FROM customers WHERE id = ?", (values["customer_id"],)
            ).fetchone()
            if customer is None:
                raise ValueError("Không tìm thấy khách hàng.")
            member = self.connection.execute(
                """
                SELECT p.discount_percent
                FROM memberships m
                JOIN membership_plans p ON p.id = m.plan_id
                WHERE m.customer_id = ? AND m.status = 'ACTIVE'
                  AND m.start_date <= ? AND m.end_date >= ?
                ORDER BY m.end_date DESC, m.id DESC LIMIT 1
                """,
                (values["customer_id"], ordered_at, ordered_at),
            ).fetchone()
            member_discount = float(member["discount_percent"]) if member else 0.0

            product_quantities: dict[int, float] = {}
            normalized_products: list[tuple[int, float, float, str]] = []
            for line in product_lines:
                item_id = int(line["item_id"])
                quantity = float(line["quantity"])
                if not math.isfinite(quantity) or quantity <= 0:
                    raise ValueError("Số lượng sản phẩm phải lớn hơn 0.")
                product = self.connection.execute(
                    """
                    SELECT id, name, pack_size, is_active, retail_price, member_price,
                           promotion_percent
                    FROM inventory_items WHERE id = ?
                    """,
                    (item_id,),
                ).fetchone()
                if product is None or not product["is_active"]:
                    raise ValueError("Sản phẩm không tồn tại hoặc đã ngừng bán.")
                price = self._effective_price(
                    float(product["retail_price"]),
                    product["member_price"],
                    float(product["promotion_percent"]),
                    member_discount,
                    member is not None,
                )
                product_quantities[item_id] = product_quantities.get(item_id, 0) + quantity
                display_name = product["name"]
                if product["pack_size"]:
                    display_name += f" · {product['pack_size']}"
                normalized_products.append((item_id, quantity, price, display_name))

            combo_allocations: list[tuple[int, int, float, float, str]] = []
            for line in combo_lines:
                combo_id = int(line["combo_id"])
                quantity = float(line["quantity"])
                if not math.isfinite(quantity) or quantity <= 0:
                    raise ValueError("Số lượng combo phải lớn hơn 0.")
                combo = self.connection.execute(
                    """
                    SELECT * FROM product_combos WHERE id = ? AND is_active = 1
                    """,
                    (combo_id,),
                ).fetchone()
                if combo is None:
                    raise ValueError("Combo không tồn tại hoặc đã ngừng bán.")
                components = self.connection.execute(
                    """
                    SELECT ci.item_id, ci.quantity, i.name, i.retail_price,
                           i.is_active, i.promotion_percent
                    FROM product_combo_items ci
                    JOIN inventory_items i ON i.id = ci.item_id
                    WHERE ci.combo_id = ?
                    """,
                    (combo_id,),
                ).fetchall()
                if not components:
                    raise ValueError(f"Combo {combo['name']} chưa có thành phần.")
                if any(not component["is_active"] for component in components):
                    raise ValueError(f"Combo {combo['name']} có sản phẩm đã ngừng bán.")
                combo_price = self._effective_price(
                    float(combo["sale_price"]),
                    combo["member_price"],
                    float(combo["promotion_percent"]),
                    member_discount,
                    member is not None,
                )
                weights = [
                    max(0.0, float(component["retail_price"]))
                    * float(component["quantity"])
                    for component in components
                ]
                weight_total = sum(weights)
                allocated = 0.0
                for index, component in enumerate(components):
                    item_id = int(component["item_id"])
                    component_quantity = float(component["quantity"]) * quantity
                    product_quantities[item_id] = (
                        product_quantities.get(item_id, 0) + component_quantity
                    )
                    if index == len(components) - 1:
                        line_total = round(combo_price * quantity - allocated, 2)
                    elif weight_total > 0:
                        line_total = round(combo_price * quantity * weights[index] / weight_total, 2)
                    else:
                        line_total = round(combo_price * quantity / len(components), 2)
                    allocated += line_total
                    combo_allocations.append(
                        (
                            item_id,
                            combo_id,
                            component_quantity,
                            line_total,
                            f"{combo['name']} · {component['name']}",
                        )
                    )

            self._ensure_available_product_stock(product_quantities)
            code = str(values.get("order_code", "")).strip()
            cursor = self.connection.execute(
                """
                INSERT INTO sales_orders
                    (order_code, customer_id, ordered_at, status, total_amount, note)
                VALUES (?, ?, ?, 'OPEN', 0, ?)
                """,
                (
                    code,
                    values["customer_id"],
                    ordered_at,
                    str(values.get("note", "")).strip(),
                ),
            )
            order_id = int(cursor.lastrowid)
            total = 0.0
            for item_id, quantity, unit_price, name in normalized_products:
                line_total = round(quantity * unit_price, 2)
                self.connection.execute(
                    """
                    INSERT INTO sales_product_items
                        (order_id, item_id, item_name, quantity, unit_price, line_total)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (order_id, item_id, name, quantity, unit_price, line_total),
                )
                total += line_total
            for item_id, combo_id, quantity, line_total, name in combo_allocations:
                self.connection.execute(
                    """
                    INSERT INTO sales_product_items
                        (order_id, item_id, combo_id, item_name, quantity,
                         unit_price, line_total)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        order_id,
                        item_id,
                        combo_id,
                        name,
                        quantity,
                        round(line_total / quantity, 2),
                        line_total,
                    ),
                )
                total += line_total
            if total <= 0:
                raise ValueError("Tổng đơn bán sản phẩm phải lớn hơn 0.")
            self.connection.execute(
                "UPDATE sales_orders SET total_amount = ? WHERE id = ?",
                (round(total, 2), order_id),
            )
            return order_id

    def _effective_price(
        self,
        retail_price: float,
        member_price: float | None,
        promotion_percent: float,
        member_discount: float,
        is_member: bool,
    ) -> float:
        promo_price = retail_price * (1 - promotion_percent / 100)
        if not is_member:
            return round(promo_price, 2)
        discounted_member_price = (
            float(member_price)
            if member_price is not None
            else promo_price * (1 - member_discount / 100)
        )
        return round(min(promo_price, discounted_member_price), 2)

    def _ensure_available_product_stock(
        self, product_quantities: dict[int, float]
    ) -> None:
        for item_id, quantity in product_quantities.items():
            item = self.connection.execute(
                """
                SELECT i.name,
                       COALESCE(SUM(CASE
                           WHEN b.expiry_date IS NULL
                             OR b.expiry_date >= date('now', 'localtime')
                           THEN b.quantity_remaining ELSE 0 END), 0) AS usable
                FROM inventory_items i
                LEFT JOIN inventory_batches b ON b.item_id = i.id
                WHERE i.id = ? AND i.is_active = 1
                GROUP BY i.id
                """,
                (item_id,),
            ).fetchone()
            if item is None:
                raise ValueError("Sản phẩm không tồn tại hoặc đã ngừng bán.")
            reserved = float(
                self.connection.execute(
                    """
                    SELECT COALESCE(SUM(pi.quantity), 0)
                    FROM sales_product_items pi
                    JOIN sales_orders o ON o.id = pi.order_id
                    WHERE pi.item_id = ? AND o.status IN ('OPEN', 'PARTIALLY_PAID')
                    """,
                    (item_id,),
                ).fetchone()[0]
            )
            available = max(0, float(item["usable"]) - reserved)
            if quantity > available:
                raise ValueError(
                    f"Tồn có thể bán của {item['name']} không đủ "
                    f"(còn {available:g})."
                )

    def _fulfill_product_order(self, order_id: int) -> None:
        lines = self.connection.execute(
            """
            SELECT pi.item_id, pi.quantity, o.order_code, o.ordered_at, pi.item_name
            FROM sales_product_items pi
            JOIN sales_orders o ON o.id = pi.order_id
            WHERE pi.order_id = ?
            ORDER BY pi.id
            """,
            (order_id,),
        ).fetchall()
        requirements: dict[int, float] = {}
        for line in lines:
            requirements[int(line["item_id"])] = (
                requirements.get(int(line["item_id"]), 0) + float(line["quantity"])
            )
        self._ensure_available_product_stock(requirements)
        for item_id, quantity in requirements.items():
            batches = self.connection.execute(
                """
                SELECT id, quantity_remaining FROM inventory_batches
                WHERE item_id = ? AND quantity_remaining > 0
                  AND (expiry_date IS NULL OR expiry_date >= date('now', 'localtime'))
                ORDER BY expiry_date IS NULL, expiry_date, id
                """,
                (item_id,),
            ).fetchall()
            remaining = quantity
            for batch in batches:
                if remaining <= 0:
                    break
                taken = min(remaining, float(batch["quantity_remaining"]))
                self.connection.execute(
                    """
                    UPDATE inventory_batches
                    SET quantity_remaining = quantity_remaining - ? WHERE id = ?
                    """,
                    (taken, batch["id"]),
                )
                self.connection.execute(
                    """
                    INSERT INTO inventory_movements
                        (item_id, batch_id, movement_type, quantity, occurred_on,
                         reference, note)
                    SELECT ?, ?, 'OUT', ?, o.ordered_at, o.order_code,
                           'Bán sản phẩm; thanh toán đủ'
                    FROM sales_orders o WHERE o.id = ?
                    """,
                    (item_id, batch["id"], taken, order_id),
                )
                remaining = round(remaining - taken, 6)
            if remaining > 0:
                raise ValueError("Tồn kho thay đổi; không thể hoàn tất xuất sản phẩm.")

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
                self._fulfill_product_order(order_id)
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
