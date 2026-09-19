from datetime import datetime
import re

class LegalMetrologyValidator:
    """Validates extracted packaging declarations against The Legal Metrology

    (Packaged Commodities) Rules, 2011 (with subsequent amendments).
    """
    VALID_METRIC_UNITS = {"g", "kg", "ml", "l", "m", "cm", "mm", "n", "u", "units"}

    def __init__(self, parsed_data: dict, category: str):
        self.data = parsed_data
        self.category = category
        self.violations = []

    def evaluate(self) -> dict:
        self._validate_manufacturer_details()
        self._validate_country_of_origin()
        self._validate_net_quantity()
        self._validate_mrp()
        self._validate_manufacturing_date()
        self._validate_consumer_care()

        is_compliant = len(self.violations) == 0
        return {
            "compliant": is_compliant,
            "violations_count": len(self.violations),
            "violations": self.violations,
            "category": self.category,
            "inspected_fields": self.data
        }

    def _validate_manufacturer_details(self):
        # Rule 6(1)(a): Name and complete address of the manufacturer / packer / importer
        if not self.data.get("manufacturer_name"):
            self.violations.append("Rule 6(1)(a) Violation: Name of manufacturer/packer/importer is missing.")
        if not self.data.get("manufacturer_address"):
            self.violations.append("Rule 6(1)(a) Violation: Registered address of manufacturer/packer is missing.")

    def _validate_country_of_origin(self):
        # Rule 6(1)(aa): Mandatory Country of Origin declaration
        if not self.data.get("country_of_origin"):
            self.violations.append("Rule 6(1)(aa) Violation: 'Country of Origin' is missing.")

    def _validate_net_quantity(self):
        # Rule 6(1)(c): Net quantity expressed in standard units of weight, measure or number
        qty = self.data.get("net_quantity")
        unit = self.data.get("quantity_unit")

        if not qty or not unit:
            self.violations.append("Rule 6(1)(c) Violation: Net quantity or measurement unit not found.")
            return

        if unit.lower() not in self.VALID_METRIC_UNITS:
            self.violations.append(
                f"Rule 6(1)(c) Violation: Non-standard unit '{unit}'. Use metric SI units (g, kg, ml, l, or units)."
            )

    def _validate_mrp(self):
        # Rule 6(1)(da): Retail sale price with 'inclusive of all taxes'
        mrp = self.data.get("mrp")
        if mrp is None:
            self.violations.append("Rule 6(1)(da) Violation: Maximum Retail Price (MRP) declaration is missing.")
            return

        if mrp <= 0:
            self.violations.append("Rule 6(1)(da) Violation: Invalid MRP value declared.")

        if not self.data.get("mrp_inclusive_of_taxes", False):
            self.violations.append("Rule 6(1)(da) Violation: MRP must state 'Inclusive of all taxes'.")

    def _validate_manufacturing_date(self):
        # Rule 6(1)(d): Month and year of manufacture or packaging
        date_str = self.data.get("mfg_date")
        if not date_str:
            self.violations.append("Rule 6(1)(d) Violation: Month and year of manufacture/packing is missing.")
            return

        # Syntax and post-dating validation (MM/YYYY)
        match = re.match(r"^(\d{1,2})[\/\-](\d{2,4})$", date_str)
        if match:
            month = int(match.group(1))
            year = int(match.group(2))
            if year < 100:
                year += 2000

            if not (1 <= month <= 12):
                self.violations.append(f"Rule 6(1)(d) Violation: Invalid month '{month}' in manufacturing date.")
            else:
                now = datetime.now()
                if (year > now.year) or (year == now.year and month > now.month):
                    self.violations.append("Rule 6(1)(d) Violation: Manufacturing date cannot be in the future.")

    def _validate_consumer_care(self):
        # Rule 6(2): Consumer care details (name/designation, address, phone, and email)
        care = self.data.get("consumer_care", {})
        has_phone = bool(care.get("phone"))
        has_email = bool(care.get("email"))

        if not (has_phone or has_email):
            self.violations.append(
                "Rule 6(2) Violation: Consumer care contact details (phone or email) are missing."
            )