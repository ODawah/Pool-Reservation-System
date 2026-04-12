from datetime import datetime
from io import BytesIO
from typing import Any, List, Optional
from xml.sax.saxutils import escape
import json
import zipfile

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from data.data import SessionLocal
from revenue import revenue
from expense.expense import Expense
from reciept.reciept import Reciept

router = APIRouter(prefix="/revenue", tags=["revenue"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def list_revenues(db: Session = Depends(get_db)):
    return db.query(revenue.Revenue).all()

@router.post("/")
async def create_revenue(
    source: str, amount: float, date: Optional[datetime] = None, db: Session = Depends(get_db)
):
    revenue_record = revenue.Revenue(
        source=source,
        amount=amount,
        date=date or datetime.now(),
    )
    db.add(revenue_record)
    db.commit()
    return {"message": "Revenue record created successfully"}


def _month_window(now: datetime):
    start_current_month = datetime(now.year, now.month, 1)
    if now.month == 1:
        start_last_month = datetime(now.year - 1, 12, 1)
    else:
        start_last_month = datetime(now.year, now.month - 1, 1)
    return start_last_month, start_current_month


def _column_name(index: int) -> str:
    name = ""
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def _cell_xml(col: int, row: int, value: Any) -> str:
    cell_ref = f"{_column_name(col)}{row}"
    if value is None:
        return f'<c r="{cell_ref}" t="inlineStr"><is><t></t></is></c>'

    if isinstance(value, (int, float)):
        return f'<c r="{cell_ref}"><v>{value}</v></c>'

    text = escape(str(value))
    return f'<c r="{cell_ref}" t="inlineStr"><is><t>{text}</t></is></c>'


def _build_report_xlsx(rows: List[List[Any]]) -> bytes:
    sheet_rows: List[str] = []
    for row_index, values in enumerate(rows, start=1):
        cells = "".join(
            _cell_xml(col=index, row=row_index, value=value)
            for index, value in enumerate(values, start=1)
        )
        sheet_rows.append(f'<row r="{row_index}">{cells}</row>')

    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<sheetData>{''.join(sheet_rows)}</sheetData>"
        "</worksheet>"
    )

    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/styles.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        "</Types>"
    )

    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        "</Relationships>"
    )

    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Monthly Report" sheetId="1" r:id="rId1"/></sheets>'
        "</workbook>"
    )

    workbook_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/>'
        "</Relationships>"
    )

    styles_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="1"><fill><patternFill patternType="none"/></fill></fills>'
        '<borders count="1"><border/></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>'
        "</styleSheet>"
    )

    output = BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("_rels/.rels", rels_xml)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)
        zf.writestr("xl/styles.xml", styles_xml)
    return output.getvalue()


def _extract_payment_source(payment_type: Optional[str], items: Any) -> str:
    if payment_type:
        source = payment_type.strip().lower()
        if source in {"cash", "visa"}:
            return source
        return "unknown"

    payload = items
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            return "unknown"

    if isinstance(payload, dict):
        for key, value in payload.items():
            if str(key).lower() == "payment":
                source = str(value).strip().lower()
                if source in {"cash", "visa"}:
                    return source
                return "unknown"

    return "unknown"


@router.post("/last-month/closeout")
async def download_last_month_closeout(db: Session = Depends(get_db)):
    now = datetime.now()
    start_last_month, start_current_month = _month_window(now)

    receipts = (
        db.query(Reciept)
        .filter(
            Reciept.timestamp >= start_last_month,
            Reciept.timestamp < start_current_month,
        )
        .order_by(Reciept.timestamp.asc(), Reciept.id.asc())
        .all()
    )

    expenses = (
        db.query(Expense)
        .filter(Expense.date >= start_last_month, Expense.date < start_current_month)
        .order_by(Expense.date.asc(), Expense.id.asc())
        .all()
    )

    revenue_rows = []
    for item in receipts:
        source = _extract_payment_source(item.payment_type, item.items)
        revenue_rows.append(
            {
                "id": item.id,
                "table_id": item.table_id,
                "source": source,
                "amount": float(item.total_price or 0),
                "date": item.timestamp,
            }
        )

    cash_total = sum(r["amount"] for r in revenue_rows if r["source"] == "cash")
    visa_total = sum(r["amount"] for r in revenue_rows if r["source"] == "visa")
    unknown_total = sum(r["amount"] for r in revenue_rows if r["source"] == "unknown")
    total_revenue = sum(r["amount"] for r in revenue_rows)
    total_expenses = sum(e.amount or 0 for e in expenses)
    net_total = total_revenue - total_expenses

    rows: List[List[Any]] = [
        ["Last Month Financial Closeout"],
        ["Period Start", start_last_month.strftime("%Y-%m-%d")],
        ["Period End", (start_current_month).strftime("%Y-%m-%d")],
        [],
        ["Revenues (from reciepts)"],
        ["Receipt ID", "Table ID", "Source", "Amount", "Date"],
    ]

    for item in revenue_rows:
        rows.append(
            [
                item["id"],
                item["table_id"],
                item["source"],
                item["amount"],
                item["date"].strftime("%Y-%m-%d %H:%M:%S") if item["date"] else "",
            ]
        )

    rows.extend([[], ["Expenses"], ["ID", "Description", "Amount", "Date"]])

    for item in expenses:
        rows.append(
            [
                item.id,
                item.description,
                float(item.amount or 0),
                item.date.strftime("%Y-%m-%d %H:%M:%S") if item.date else "",
            ]
        )

    rows.extend(
        [
            [],
            ["Summary"],
            ["Cash Revenue", float(cash_total)],
            ["Visa Revenue", float(visa_total)],
            ["Unknown Source Revenue", float(unknown_total)],
            ["Total Revenue", float(total_revenue)],
            ["Total Expenses", float(total_expenses)],
            ["Net Revenue (Revenue - Expenses)", float(net_total)],
        ]
    )

    workbook_bytes = _build_report_xlsx(rows)

    db.query(Reciept).filter(
        Reciept.timestamp >= start_last_month,
        Reciept.timestamp < start_current_month,
    ).delete(synchronize_session=False)
    db.query(revenue.Revenue).filter(
        revenue.Revenue.date >= start_last_month,
        revenue.Revenue.date < start_current_month,
    ).delete(synchronize_session=False)
    db.query(Expense).filter(
        Expense.date >= start_last_month,
        Expense.date < start_current_month,
    ).delete(synchronize_session=False)
    db.commit()

    filename = f"financial_closeout_{start_last_month.strftime('%Y_%m')}.xlsx"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        BytesIO(workbook_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
