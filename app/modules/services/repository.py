import math
import sqlite3
from datetime import date, datetime, timedelta
from typing import Any

from app.modules.memberships.repository import MembershipRepository
from app.modules.services.catalog_seed import MEMBERSHIP_PACKAGES, SERVICE_PACKAGES
from app.modules.services.constants import (
    COAT_SURCHARGE_TYPES,
    COAT_TYPE_CODES,
    SERVICE_CATEGORIES,
)
APPOINTMENT_TRANSITIONS = {
    "SCHEDULED": frozenset({"CHECKED_IN", "CANCELLED", "NO_SHOW"}),
    "CHECKED_IN": frozenset({"IN_PROGRESS", "CANCELLED", "NO_SHOW"}),
    "IN_PROGRESS": frozenset({"COMPLETED", "CANCELLED"}),
}


class ServicesRepository:
    def __init__(
        self, connection: sqlite3.Connection, memberships: MembershipRepository
    ) -> None:
        self.connection = connection
        self.memberships = memberships

    def seed_catalog(self) -> tuple[int, int]:
        with self.connection:
            for package in SERVICE_PACKAGES:
                self.connection.execute(
                    """
                    INSERT OR IGNORE INTO service_packages
                        (code, category, name, description, species, coat_types,
                         min_weight, max_weight, duration_minutes, list_price,
                         member_price, included_weight_kg, surcharge_per_kg,
                         coat_surcharge, is_demo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        package["code"],
                        package["category"],
                        package["name"],
                        package["description"],
                        package["species"],
                        package["coat_types"],
                        package["min_weight"],
                        package["max_weight"],
                        package["duration_minutes"],
                        package["list_price"],
                        package["member_price"],
                        package["included_weight_kg"],
                        package["surcharge_per_kg"],
                        package["coat_surcharge"],
                        int(package["is_demo"]),
                    ),
                )
            for package in MEMBERSHIP_PACKAGES:
                self.connection.execute(
                    """
                    INSERT OR IGNORE INTO membership_plans
                        (code, name, description, duration_days, price,
                         discount_percent, benefits, max_pets, billing_mode,
                         included_visits, service_category)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        package["code"],
                        package["name"],
                        package["description"],
                        package["duration_days"],
                        package["price"],
                        package["discount_percent"],
                        package["description"],
                        package["max_pets"],
                        package["billing_mode"],
                        package["included_visits"],
                        package["service_category"],
                    ),
                )
        service_count = int(
            self.connection.execute(
                "SELECT COUNT(*) FROM service_packages WHERE is_demo = 1"
            ).fetchone()[0]
        )
        membership_count = int(
            self.connection.execute(
                "SELECT COUNT(*) FROM membership_plans WHERE code LIKE 'SVC-MEM-%'"
            ).fetchone()[0]
        )
        return service_count, membership_count

    def list_packages(
        self, search: str = "", include_inactive: bool = True
    ) -> list[sqlite3.Row]:
        conditions: list[str] = []
        parameters: list[str] = []
        if not include_inactive:
            conditions.append("is_active = 1")
        if search.strip():
            pattern = f"%{search.strip()}%"
            conditions.append("(code LIKE ? OR name LIKE ? OR category LIKE ?)")
            parameters.extend((pattern, pattern, pattern))
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        return self.connection.execute(
            f"SELECT * FROM service_packages {where} ORDER BY category, name COLLATE NOCASE",
            parameters,
        ).fetchall()

    def save_package(self, values: dict[str, Any], package_id: int | None = None) -> int:
        code = str(values.get("code", "")).strip().upper()
        category = str(values.get("category", "")).strip()
        name = str(values.get("name", "")).strip()
        species = str(values.get("species", "")).strip()
        coats = str(values.get("coat_types", "ANY")).strip().upper()
        description = str(values.get("description", "")).strip()
        min_weight = self._number(values.get("min_weight", 0), "Cân nặng tối thiểu")
        raw_max_weight = values.get("max_weight")
        max_weight = (
            None
            if raw_max_weight in (None, "")
            else self._number(raw_max_weight, "Cân nặng tối đa")
        )
        duration = int(values.get("duration_minutes", 0))
        price = self._number(values.get("list_price", 0), "Giá niêm yết")
        raw_member_price = values.get("member_price")
        member_price = (
            None
            if raw_member_price in (None, "")
            else self._number(raw_member_price, "Giá hội viên")
        )
        included_weight = self._number(
            values.get("included_weight_kg", 0), "Cân nặng đã bao gồm"
        )
        surcharge_per_kg = self._number(
            values.get("surcharge_per_kg", 0), "Phụ phí mỗi kg"
        )
        coat_surcharge = self._number(
            values.get("coat_surcharge", 0), "Phụ phí lông dày/dài"
        )
        if not code or not name or not species:
            raise ValueError("Mã, tên gói và loài áp dụng là bắt buộc.")
        if category not in SERVICE_CATEGORIES:
            raise ValueError("Loại dịch vụ không hợp lệ.")
        if duration <= 0:
            raise ValueError("Thời lượng phải lớn hơn 0.")
        if max_weight is not None and max_weight < min_weight:
            raise ValueError("Cân nặng tối đa phải lớn hơn hoặc bằng tối thiểu.")
        fields = (
            code,
            category,
            name,
            description,
            species,
            coats or "ANY",
            min_weight,
            max_weight,
            duration,
            price,
            member_price,
            included_weight,
            surcharge_per_kg,
            coat_surcharge,
            int(bool(values.get("is_demo", False))),
            int(bool(values.get("is_active", True))),
        )
        with self.connection:
            if package_id is None:
                cursor = self.connection.execute(
                    """
                    INSERT INTO service_packages
                        (code, category, name, description, species, coat_types,
                         min_weight, max_weight, duration_minutes, list_price,
                         member_price, included_weight_kg, surcharge_per_kg,
                         coat_surcharge, is_demo, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    fields,
                )
                return int(cursor.lastrowid)
            cursor = self.connection.execute(
                """
                UPDATE service_packages SET code = ?, category = ?, name = ?,
                    description = ?, species = ?, coat_types = ?, min_weight = ?,
                    max_weight = ?, duration_minutes = ?, list_price = ?,
                    member_price = ?, included_weight_kg = ?, surcharge_per_kg = ?,
                    coat_surcharge = ?, is_demo = ?, is_active = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (*fields, package_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("Không tìm thấy gói dịch vụ.")
            return package_id

    def customer_memberships(self, customer_id: int) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT m.id, m.membership_code, m.end_date, p.name AS plan_name,
                   p.billing_mode, p.discount_percent, p.included_visits,
                   p.service_category, p.max_pets,
                   MAX(0, p.included_visits - COALESCE((
                       SELECT COUNT(*) FROM membership_service_uses u
                       WHERE u.membership_id = m.id
                         AND u.cycle_number = m.renewal_count
                         AND u.status IN ('RESERVED', 'USED')
                   ), 0)) AS remaining_visits
            FROM memberships m
            JOIN membership_plans p ON p.id = m.plan_id
            WHERE m.customer_id = ? AND m.status = 'ACTIVE'
              AND m.start_date <= date('now', 'localtime')
              AND m.end_date >= date('now', 'localtime')
            ORDER BY m.end_date, m.id
            """,
            (customer_id,),
        ).fetchall()

    def quote(
        self,
        package_id: int,
        species: str,
        weight_kg: float | None,
        coat_type: str,
        membership_id: int | None = None,
    ) -> dict[str, float | int | str | None]:
        package = self.connection.execute(
            "SELECT * FROM service_packages WHERE id = ? AND is_active = 1",
            (package_id,),
        ).fetchone()
        if package is None:
            raise ValueError("Gói dịch vụ không tồn tại hoặc đã ngừng hoạt động.")
        species_aliases = {"chó": "dog", "dog": "dog", "mèo": "cat", "cat": "cat"}
        selected_species = species_aliases.get(
            species.strip().casefold(), species.strip().casefold()
        )
        allowed_species = {
            species_aliases.get(item.strip().casefold(), item.strip().casefold())
            for item in str(package["species"]).split(",")
            if item.strip()
        }
        if not selected_species or not (
            "any" in allowed_species or selected_species in allowed_species
        ):
            raise ValueError("Gói dịch vụ không áp dụng cho loài đã chọn.")
        weight = None if weight_kg is None else self._number(weight_kg, "Cân nặng")
        if weight is None and (
            float(package["min_weight"]) > 0
            or package["max_weight"] is not None
            or float(package["surcharge_per_kg"]) > 0
        ):
            raise ValueError("Cần nhập cân nặng để tính giá và kiểm tra điều kiện gói.")
        if weight is not None and not float(package["min_weight"]) <= weight:
            raise ValueError("Thú cưng chưa đạt cân nặng tối thiểu của gói.")
        if (
            weight is not None
            and package["max_weight"] is not None
            and weight > float(package["max_weight"])
        ):
            raise ValueError("Thú cưng vượt cân nặng tối đa của gói.")
        surcharge = 0.0
        if weight is not None and weight > float(package["included_weight_kg"]):
            surcharge += (
                weight - float(package["included_weight_kg"])
            ) * float(package["surcharge_per_kg"])
        normalized_coat = COAT_TYPE_CODES.get(
            coat_type.strip().upper(), coat_type.strip().upper()
        )
        if (
            float(package["coat_surcharge"]) > 0
            and normalized_coat not in COAT_SURCHARGE_TYPES
        ):
            raise ValueError("Cần chọn đúng loại lông để tính phụ phí.")
        coat_rules = {
            item.strip().upper()
            for item in str(package["coat_types"]).split(",")
            if item.strip()
        }
        if (
            normalized_coat in COAT_SURCHARGE_TYPES
            and (not coat_rules or "ANY" in coat_rules or normalized_coat in coat_rules)
        ):
            surcharge += float(package["coat_surcharge"])
        base = float(package["list_price"])
        discount = 0.0
        billing_mode: str | None = None
        if membership_id is not None:
            member = self._active_membership(membership_id)
            if member is None:
                raise ValueError("Thẻ hội viên không hoạt động hoặc đã hết hạn.")
            if member["billing_mode"] == "PREPAID_VISITS":
                self._validate_prepaid_category(member, package["category"])
                remaining = self._remaining_visits(
                    membership_id,
                    member["included_visits"],
                    member["renewal_count"],
                )
                if remaining <= 0:
                    raise ValueError("Gói hội viên đã hết lượt dịch vụ.")
                billing_mode = "PREPAID_VISITS"
                discount = base
            else:
                billing_mode = member["billing_mode"]
                if member["billing_mode"] in {"MEMBER_DISCOUNT", "RECURRING"}:
                    if package["member_price"] is not None:
                        discount = max(
                            0.0, base - float(package["member_price"])
                        )
                    else:
                        discount = base * (
                            float(member["discount_percent"]) / 100
                        )
        total = max(0.0, round(base + surcharge - discount, 2))
        return {
            "base_price": round(base, 2),
            "surcharge": round(surcharge, 2),
            "discount": round(discount, 2),
            "total_price": total,
            "billing_mode": billing_mode,
        }

    def create_appointment(self, values: dict[str, Any]) -> int:
        package_id = int(values.get("package_id", 0))
        customer_id = int(values.get("customer_id", 0))
        pet_name = str(values.get("pet_name", "")).strip()
        species = str(values.get("species", "")).strip()
        coat_type = str(values.get("coat_type", "Không rõ")).strip()
        scheduled_at = str(values.get("scheduled_at", "")).strip()
        staff = str(values.get("assigned_staff", "")).strip()
        note = str(values.get("note", "")).strip()
        raw_weight = values.get("weight_kg")
        weight = None if raw_weight in (None, "") else self._number(raw_weight, "Cân nặng")
        membership_id = values.get("membership_id")
        membership_id = None if membership_id in (None, "") else int(membership_id)
        if not pet_name or not species or not scheduled_at:
            raise ValueError("Tên thú cưng, loài và giờ hẹn là bắt buộc.")
        try:
            parsed_schedule = datetime.fromisoformat(scheduled_at)
        except ValueError as error:
            raise ValueError("Ngày giờ hẹn không hợp lệ.") from error
        customer = self.connection.execute(
            "SELECT id FROM customers WHERE id = ?", (customer_id,)
        ).fetchone()
        if customer is None:
            raise ValueError("Không tìm thấy khách hàng.")
        quote = self.quote(package_id, species, weight, coat_type, membership_id)
        with self.connection:
            package = self.connection.execute(
                "SELECT category, name, duration_minutes FROM service_packages WHERE id = ?",
                (package_id,),
            ).fetchone()
            if package is None:
                raise ValueError("Gói dịch vụ không tồn tại.")
            end_at = parsed_schedule + timedelta(
                minutes=int(package["duration_minutes"])
            )
            overlap = self.connection.execute(
                """
                SELECT a.id, a.pet_name, a.assigned_staff
                FROM service_appointments a
                WHERE a.status NOT IN ('CANCELLED', 'NO_SHOW')
                  AND datetime(a.scheduled_at) < datetime(?)
                  AND datetime(a.scheduled_at, printf('+%d minutes', a.duration_minutes))
                      > datetime(?)
                  AND (
                      (a.customer_id = ? AND lower(trim(a.pet_name)) = lower(trim(?)))
                      OR (? != '' AND lower(trim(a.assigned_staff)) = lower(trim(?)))
                  )
                LIMIT 1
                """,
                (
                    end_at.isoformat(timespec="minutes"),
                    parsed_schedule.isoformat(timespec="minutes"),
                    customer_id,
                    pet_name,
                    staff,
                    staff,
                ),
            ).fetchone()
            if overlap is not None:
                if staff and overlap["assigned_staff"].casefold() == staff.casefold():
                    raise ValueError("Nhân viên đã có lịch hẹn trùng giờ.")
                raise ValueError("Thú cưng đã có lịch hẹn trùng giờ.")
            if membership_id is not None:
                member = self._active_membership(membership_id)
                if member is None or int(member["customer_id"]) != customer_id:
                    raise ValueError("Hội viên không thuộc khách hàng đã chọn.")
                scheduled_date = parsed_schedule.date().isoformat()
                if not member["start_date"] <= scheduled_date <= member["end_date"]:
                    raise ValueError("Thẻ hội viên không còn hiệu lực vào ngày hẹn.")
                pet_key = pet_name.casefold()
                known_pets = {
                    row["pet_key"]
                    for row in self.connection.execute(
                        """
                        SELECT DISTINCT lower(trim(pet_name)) AS pet_key
                        FROM service_appointments
                        WHERE membership_id = ? AND status NOT IN ('CANCELLED', 'NO_SHOW')
                          AND date(scheduled_at) BETWEEN ? AND ?
                        """,
                        (
                            membership_id,
                            member["start_date"],
                            member["end_date"],
                        ),
                    ).fetchall()
                }
                if pet_key not in known_pets and len(known_pets) >= int(member["max_pets"]):
                    raise ValueError(
                        f"Gói hội viên chỉ áp dụng tối đa {member['max_pets']} thú cưng."
                    )
            appointment_code = self.memberships._next_code(
                "APT", parsed_schedule.year, "service_appointments"
            )
            cursor = self.connection.execute(
                """
                INSERT INTO service_appointments
                    (appointment_code, package_id, customer_id, membership_id,
                     pet_name, species, weight_kg, coat_type, scheduled_at,
                     duration_minutes, assigned_staff, base_price, surcharge,
                     discount, total_price, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    appointment_code,
                    package_id,
                    customer_id,
                    membership_id,
                    pet_name,
                    species,
                    weight,
                    coat_type,
                    parsed_schedule.isoformat(timespec="minutes"),
                    package["duration_minutes"],
                    staff,
                    quote["base_price"],
                    quote["surcharge"],
                    quote["discount"],
                    quote["total_price"],
                    note,
                ),
            )
            appointment_id = int(cursor.lastrowid)
            if quote["billing_mode"] == "PREPAID_VISITS":
                member = self._active_membership(int(membership_id))
                if member is None:
                    raise ValueError("Thẻ hội viên không hoạt động hoặc đã hết hạn.")
                cycle_number = int(member["renewal_count"])
                if self._remaining_visits(
                    int(membership_id), member["included_visits"], cycle_number
                ) <= 0:
                    raise ValueError("Gói hội viên đã hết lượt dịch vụ.")
                self.connection.execute(
                    """
                    INSERT INTO membership_service_uses
                        (membership_id, appointment_id, cycle_number, status)
                    VALUES (?, ?, ?, 'RESERVED')
                    """,
                    (membership_id, appointment_id, cycle_number),
                )
            return appointment_id

    def list_appointments(self, search: str = "") -> list[sqlite3.Row]:
        query = """
            SELECT a.*, p.code AS package_code, p.name AS package_name,
                   c.name AS customer_name, c.phone AS customer_phone,
                   m.membership_code, mp.billing_mode AS membership_mode,
                   b.bill_number, b.status AS bill_status
            FROM service_appointments a
            JOIN service_packages p ON p.id = a.package_id
            JOIN customers c ON c.id = a.customer_id
            LEFT JOIN memberships m ON m.id = a.membership_id
            LEFT JOIN membership_plans mp ON mp.id = m.plan_id
            LEFT JOIN bills b ON b.id = a.bill_id
        """
        params: tuple[str, ...] = ()
        if search.strip():
            pattern = f"%{search.strip()}%"
            query += """
                WHERE a.appointment_code LIKE ? OR a.pet_name LIKE ?
                   OR c.name LIKE ? OR p.name LIKE ?
            """
            params = (pattern, pattern, pattern, pattern)
        return self.connection.execute(
            query + " ORDER BY a.scheduled_at DESC, a.id DESC", params
        ).fetchall()

    def reschedule_appointment(self, appointment_id: int, scheduled_at: str) -> None:
        try:
            new_start = datetime.fromisoformat(scheduled_at)
        except ValueError as error:
            raise ValueError("Ngày giờ hẹn không hợp lệ.") from error
        with self.connection:
            appointment = self.connection.execute(
                """
                SELECT a.*, p.duration_minutes AS package_duration
                FROM service_appointments a
                JOIN service_packages p ON p.id = a.package_id
                WHERE a.id = ?
                """,
                (appointment_id,),
            ).fetchone()
            if appointment is None:
                raise ValueError("Không tìm thấy lịch hẹn.")
            if appointment["status"] != "SCHEDULED":
                raise ValueError("Chỉ có thể dời lịch hẹn đang ở trạng thái đã đặt.")
            if appointment["membership_id"] is not None:
                member = self.connection.execute(
                    """
                    SELECT m.status, m.start_date, m.end_date, p.billing_mode
                    FROM memberships m JOIN membership_plans p ON p.id = m.plan_id
                    WHERE m.id = ?
                    """,
                    (appointment["membership_id"],),
                ).fetchone()
                if (
                    member is None
                    or member["status"] != "ACTIVE"
                    or not member["start_date"]
                    <= new_start.date().isoformat()
                    <= member["end_date"]
                ):
                    raise ValueError("Hội viên không còn hiệu lực vào ngày hẹn mới.")
            new_end = new_start + timedelta(minutes=int(appointment["duration_minutes"]))
            overlap = self.connection.execute(
                """
                SELECT a.id, a.assigned_staff
                FROM service_appointments a
                WHERE a.id != ? AND a.status NOT IN ('CANCELLED', 'NO_SHOW')
                  AND datetime(a.scheduled_at) < datetime(?)
                  AND datetime(a.scheduled_at, printf('+%d minutes', a.duration_minutes))
                      > datetime(?)
                  AND (
                      (a.customer_id = ? AND lower(trim(a.pet_name)) = lower(trim(?)))
                      OR (? != '' AND lower(trim(a.assigned_staff)) = lower(trim(?)))
                  )
                LIMIT 1
                """,
                (
                    appointment_id,
                    new_end.isoformat(timespec="minutes"),
                    new_start.isoformat(timespec="minutes"),
                    appointment["customer_id"],
                    appointment["pet_name"],
                    appointment["assigned_staff"],
                    appointment["assigned_staff"],
                ),
            ).fetchone()
            if overlap is not None:
                if (
                    appointment["assigned_staff"]
                    and overlap["assigned_staff"].casefold()
                    == appointment["assigned_staff"].casefold()
                ):
                    raise ValueError("Nhân viên đã có lịch hẹn trùng giờ.")
                raise ValueError("Thú cưng đã có lịch hẹn trùng giờ.")
            self.connection.execute(
                """
                UPDATE service_appointments SET scheduled_at = ?,
                    updated_at = CURRENT_TIMESTAMP WHERE id = ?
                """,
                (new_start.isoformat(timespec="minutes"), appointment_id),
            )

    def update_appointment_status(self, appointment_id: int, status: str) -> None:
        with self.connection:
            appointment = self.connection.execute(
                "SELECT * FROM service_appointments WHERE id = ?",
                (appointment_id,),
            ).fetchone()
            if appointment is None:
                raise ValueError("Không tìm thấy lịch hẹn.")
            if status not in APPOINTMENT_TRANSITIONS.get(
                appointment["status"], frozenset()
            ):
                raise ValueError(
                    f"Không thể chuyển lịch hẹn từ {appointment['status']} sang {status}."
                )
            if status == "COMPLETED":
                if appointment["membership_id"] is not None:
                    use = self.connection.execute(
                        """
                        SELECT u.*, p.billing_mode, p.included_visits
                        FROM membership_service_uses u
                        JOIN memberships m ON m.id = u.membership_id
                        JOIN membership_plans p ON p.id = m.plan_id
                        WHERE u.appointment_id = ? AND u.status = 'RESERVED'
                        """,
                        (appointment_id,),
                    ).fetchone()
                    if use is not None:
                        member = self._active_membership(int(use["membership_id"]))
                        if member is None:
                            raise ValueError(
                                "Hội viên đã hết hạn; không thể sử dụng lượt trả trước."
                            )
                        self.connection.execute(
                            """
                            UPDATE membership_service_uses
                            SET status = 'USED', updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                            """,
                            (use["id"],),
                        )
                        if float(appointment["total_price"]) > 0:
                            bill_id = self._create_service_bill(appointment)
                            self.connection.execute(
                                "UPDATE service_appointments SET bill_id = ? WHERE id = ?",
                                (bill_id, appointment_id),
                            )
                    else:
                        member = self._active_membership(
                            int(appointment["membership_id"])
                        )
                        if (
                            member is not None
                            and member["billing_mode"] == "PREPAID_VISITS"
                        ):
                            raise ValueError(
                                "Không tìm thấy lượt trả trước đã giữ cho lịch hẹn."
                            )
                        bill_id = self._create_service_bill(appointment)
                        self.connection.execute(
                            "UPDATE service_appointments SET bill_id = ? WHERE id = ?",
                            (bill_id, appointment_id),
                        )
                else:
                    bill_id = self._create_service_bill(appointment)
                    self.connection.execute(
                        "UPDATE service_appointments SET bill_id = ? WHERE id = ?",
                        (bill_id, appointment_id),
                    )
            if status in {"CANCELLED", "NO_SHOW"}:
                self.connection.execute(
                    """
                    UPDATE membership_service_uses SET status = 'RELEASED',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE appointment_id = ? AND status = 'RESERVED'
                    """,
                    (appointment_id,),
                )
            self.connection.execute(
                """
                UPDATE service_appointments SET status = ?,
                    updated_at = CURRENT_TIMESTAMP WHERE id = ?
                """,
                (status, appointment_id),
            )

    def _active_membership(self, membership_id: int) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT m.*, p.billing_mode, p.discount_percent, p.included_visits,
                   p.service_category, p.max_pets
            FROM memberships m JOIN membership_plans p ON p.id = m.plan_id
            WHERE m.id = ? AND m.status = 'ACTIVE'
              AND m.start_date <= date('now', 'localtime')
              AND m.end_date >= date('now', 'localtime')
            """,
            (membership_id,),
        ).fetchone()

    def _remaining_visits(
        self, membership_id: int, included_visits: int, cycle_number: int
    ) -> int:
        used = int(
            self.connection.execute(
                """
                SELECT COUNT(*) FROM membership_service_uses
                WHERE membership_id = ? AND cycle_number = ?
                  AND status IN ('RESERVED', 'USED')
                """,
                (membership_id, cycle_number),
            ).fetchone()[0]
        )
        return max(0, int(included_visits) - used)

    @staticmethod
    def _validate_prepaid_category(member: sqlite3.Row, category: str) -> None:
        selected = str(member["service_category"]).strip()
        if selected and selected != category:
            raise ValueError("Gói trả trước không áp dụng cho loại dịch vụ này.")

    def _create_service_bill(self, appointment: sqlite3.Row) -> int:
        issued_at = date.today().isoformat()
        bill_number = self.memberships._next_code("BILL", date.today().year, "bills")
        cursor = self.connection.execute(
            """
            INSERT INTO bills
                (bill_number, customer_id, bill_type, subtotal, discount_amount,
                 total_amount, status, issued_at, paid_at)
            VALUES (?, ?, 'OTHER', ?, ?, ?, ?, ?, ?)
            """,
            (
                bill_number,
                appointment["customer_id"],
                appointment["base_price"] + appointment["surcharge"],
                appointment["discount"],
                appointment["total_price"],
                "PAID" if appointment["total_price"] == 0 else "PENDING",
                issued_at,
                issued_at if appointment["total_price"] == 0 else None,
            ),
        )
        bill_id = int(cursor.lastrowid)
        self.connection.execute(
            """
            INSERT INTO bill_items
                (bill_id, item_name, description, quantity, unit_price, discount, total)
            VALUES (?, ?, ?, 1, ?, ?, ?)
            """,
            (
                bill_id,
                appointment["pet_name"],
                f"Dịch vụ tại lịch hẹn {appointment['appointment_code']}",
                appointment["base_price"] + appointment["surcharge"],
                appointment["discount"],
                appointment["total_price"],
            ),
        )
        return bill_id

    @staticmethod
    def _number(value: Any, label: str) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError(f"{label} không hợp lệ.") from error
        if not math.isfinite(number) or number < 0:
            raise ValueError(f"{label} không hợp lệ.")
        return number
