from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.offering_letter import OfferingLetter
from app.models.customer import Customer
from app.schemas.common import PaginatedResponse, MessageResponse
from app.schemas.offering_letter import (
    OfferingLetterResponse,
    OfferingLetterCreate,
    OfferingLetterUpdate,
)

router = APIRouter()


@router.get("/offering-letters", response_model=PaginatedResponse[OfferingLetterResponse])
async def list_offering_letters(
    page: int = 1, page_size: int = 20, db: AsyncSession = Depends(get_db)
):
    total_result = await db.execute(select(func.count()).select_from(select(OfferingLetter).subquery()))
    total = total_result.scalar() or 0

    stmt = (
        select(OfferingLetter, Customer.name.label("customer_name"))
        .join(Customer, OfferingLetter.customer_id == Customer.id)
        .order_by(OfferingLetter.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    rows = result.all()

    items = []
    for ol, customer_name in rows:
        items.append(OfferingLetterResponse(
            id=ol.id,
            offering_letter_number=ol.offering_letter_number,
            customer_id=ol.customer_id,
            customer_name=customer_name,
            location=ol.location,
            date=ol.date,
            regarding=ol.regarding,
            receiver=ol.receiver,
            fuel_total_price=ol.fuel_total_price,
            transport_price=ol.transport_price,
            status=ol.status,
            created_at=ol.created_at,
            updated_at=ol.updated_at,
        ))
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/offering-letters/{id}", response_model=OfferingLetterResponse)
async def get_offering_letter(id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(OfferingLetter, Customer.name.label("customer_name"))
        .join(Customer, OfferingLetter.customer_id == Customer.id)
        .where(OfferingLetter.id == id)
    )
    result = await db.execute(stmt)
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    ol, customer_name = row
    return OfferingLetterResponse(
        id=ol.id, offering_letter_number=ol.offering_letter_number,
        customer_id=ol.customer_id, customer_name=customer_name,
        location=ol.location, date=ol.date, regarding=ol.regarding,
        receiver=ol.receiver, fuel_total_price=ol.fuel_total_price,
        transport_price=ol.transport_price, status=ol.status,
        created_at=ol.created_at, updated_at=ol.updated_at,
    )


@router.post("/offering-letters", response_model=OfferingLetterResponse, status_code=201)
async def create_offering_letter(body: OfferingLetterCreate, db: AsyncSession = Depends(get_db)):
    ol = OfferingLetter(**body.model_dump())
    db.add(ol)
    await db.flush()
    await db.refresh(ol)
    customer = await db.execute(select(Customer).where(Customer.id == ol.customer_id))
    c = customer.scalar_one_or_none()
    return OfferingLetterResponse(
        id=ol.id, offering_letter_number=ol.offering_letter_number,
        customer_id=ol.customer_id, customer_name=c.name if c else "",
        location=ol.location, date=ol.date, regarding=ol.regarding,
        receiver=ol.receiver, fuel_total_price=ol.fuel_total_price,
        transport_price=ol.transport_price, status=ol.status,
        created_at=ol.created_at, updated_at=ol.updated_at,
    )


@router.put("/offering-letters/{id}", response_model=OfferingLetterResponse)
async def update_offering_letter(id: str, body: OfferingLetterUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OfferingLetter).where(OfferingLetter.id == id))
    ol = result.scalar_one_or_none()
    if not ol:
        raise HTTPException(status_code=404, detail="Not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(ol, key, val)
    await db.flush()
    await db.refresh(ol)
    customer = await db.execute(select(Customer).where(Customer.id == ol.customer_id))
    c = customer.scalar_one_or_none()
    return OfferingLetterResponse(
        id=ol.id, offering_letter_number=ol.offering_letter_number,
        customer_id=ol.customer_id, customer_name=c.name if c else "",
        location=ol.location, date=ol.date, regarding=ol.regarding,
        receiver=ol.receiver, fuel_total_price=ol.fuel_total_price,
        transport_price=ol.transport_price, status=ol.status,
        created_at=ol.created_at, updated_at=ol.updated_at,
    )


@router.delete("/offering-letters/{id}", response_model=MessageResponse)
async def delete_offering_letter(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OfferingLetter).where(OfferingLetter.id == id))
    ol = result.scalar_one_or_none()
    if not ol:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(ol)
    await db.flush()
    return MessageResponse(message="Deleted", code=200)
