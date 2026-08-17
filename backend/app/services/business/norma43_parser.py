"""Spanish Norma 43 (CSB 43 / AEB 43) Bank Statement Parser."""

from typing import List, Optional, Union
from app.core.exceptions import ExtractionError
from app.domain.business_models import BankMovementLine, Norma43ParseResult


class Norma43Parser:
    """Parses standard Spanish banking Norma 43 fixed-width electronic statements."""

    def parse(self, content: Union[str, bytes]) -> Norma43ParseResult:
        if isinstance(content, bytes):
            text = content.decode("latin-1", errors="ignore")
        else:
            text = content

        lines = [l.strip("\r\n") for l in text.splitlines() if l.strip()]
        if not lines:
            raise ExtractionError("El archivo Norma 43 está vacío.")

        bank_code = ""
        branch_code = ""
        account_number = ""
        currency = "EUR"
        initial_balance = 0.0
        final_balance = 0.0
        total_debit = 0.0
        total_credit = 0.0

        movements: List[BankMovementLine] = []
        current_movement: Optional[BankMovementLine] = None

        for line in lines:
            if len(line) < 2:
                continue

            rec_type = line[:2]

            # 11: Header record
            if rec_type == "11":
                bank_code = line[2:6].strip()
                branch_code = line[6:10].strip()
                account_number = line[10:20].strip()
                if len(line) >= 47:
                    sign_init = -1.0 if line[32:33] == "1" else 1.0
                    try:
                        raw_amt = float(line[33:47].strip()) / 100.0
                        initial_balance = round(sign_init * raw_amt, 2)
                    except ValueError:
                        pass
                if len(line) >= 50:
                    curr_code = line[47:50].strip()
                    currency = "EUR" if curr_code in ("EUR", "978", "") else curr_code

            # 22: Principal movement line
            elif rec_type == "22":
                op_date_raw = line[6:12].strip()  # YYMMDD
                val_date_raw = line[12:18].strip()  # YYMMDD
                common_concept = line[18:20].strip()
                own_concept = line[20:23].strip()
                debit_credit = "D" if line[23:24] == "1" else "C"

                try:
                    amount_raw = float(line[24:38].strip()) / 100.0
                except ValueError:
                    amount_raw = 0.0

                doc_num = line[38:48].strip()
                concept_desc = line[50:80].strip() if len(line) >= 51 else ""

                current_movement = BankMovementLine(
                    operation_date=self._format_date(op_date_raw),
                    value_date=self._format_date(val_date_raw),
                    common_concept=common_concept,
                    own_concept=own_concept,
                    debit_or_credit=debit_credit,
                    amount=round(amount_raw, 2),
                    document_number=doc_num if doc_num else None,
                    extended_concept=concept_desc,
                )
                movements.append(current_movement)

            # 23: Complementary concept line
            elif rec_type == "23":
                if current_movement and len(line) >= 4:
                    extra_text = line[4:80].strip()
                    if extra_text:
                        existing = current_movement.extended_concept or ""
                        current_movement.extended_concept = (existing + " " + extra_text).strip()

            # 33: End of account summary
            elif rec_type == "33":
                if len(line) >= 72:
                    try:
                        total_debit = round(float(line[24:38].strip()) / 100.0, 2)
                        total_credit = round(float(line[43:57].strip()) / 100.0, 2)
                        sign_final = -1.0 if line[57:58] == "1" else 1.0
                        final_balance = round(sign_final * (float(line[58:72].strip()) / 100.0), 2)
                    except ValueError:
                        pass

        # If summary wasn't in file, compute from movements
        if total_debit == 0.0 and total_credit == 0.0 and movements:
            total_debit = round(sum(m.amount for m in movements if m.debit_or_credit == "D"), 2)
            total_credit = round(sum(m.amount for m in movements if m.debit_or_credit == "C"), 2)
            final_balance = round(initial_balance + total_credit - total_debit, 2)

        return Norma43ParseResult(
            bank_code=bank_code or "0000",
            branch_code=branch_code or "0000",
            account_number=account_number or "0000000000",
            currency=currency,
            initial_balance=initial_balance,
            final_balance=final_balance,
            total_debit_amount=total_debit,
            total_credit_amount=total_credit,
            movements_count=len(movements),
            movements=movements,
        )

    def _format_date(self, yymmdd: str) -> str:
        if len(yymmdd) == 6 and yymmdd.isdigit():
            yy, mm, dd = yymmdd[:2], yymmdd[2:4], yymmdd[4:6]
            year = f"20{yy}" if int(yy) < 80 else f"19{yy}"
            return f"{year}-{mm}-{dd}"
        return yymmdd
