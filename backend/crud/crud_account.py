from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from model.models import Address, Notification, SavedPaymentMethod, User
from schemas import AddressCreate, SavedPaymentMethodCreate


async def get_profile(user_id: int, session: AsyncSession) -> User | None:
    statement = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.addresses))
        .options(selectinload(User.saved_payment_methods))
        .options(selectinload(User.notifications))
    )
    result = await session.exec(statement)
    return result.one_or_none()


async def create_address(user_id: int, data: AddressCreate, session: AsyncSession) -> Address:
    if data.is_default:
        await clear_default_addresses(user_id=user_id, session=session)
    address = Address.model_validate(data, update={"user_id": user_id})
    session.add(address)
    await session.commit()
    await session.refresh(address)
    return address


async def clear_default_addresses(user_id: int, session: AsyncSession) -> None:
    result = await session.exec(select(Address).where(Address.user_id == user_id))
    for address in result.all():
        address.is_default = False
        session.add(address)


async def delete_address(user_id: int, address_id: int, session: AsyncSession) -> bool:
    address = await session.get(Address, address_id)
    if not address or address.user_id != user_id:
        return False
    await session.delete(address)
    await session.commit()
    return True


async def create_payment_method(
    user_id: int,
    data: SavedPaymentMethodCreate,
    session: AsyncSession,
) -> SavedPaymentMethod:
    if data.is_default:
        result = await session.exec(select(SavedPaymentMethod).where(SavedPaymentMethod.user_id == user_id))
        for method in result.all():
            method.is_default = False
            session.add(method)
    method = SavedPaymentMethod.model_validate(data, update={"user_id": user_id})
    session.add(method)
    await session.commit()
    await session.refresh(method)
    return method


async def delete_payment_method(user_id: int, method_id: int, session: AsyncSession) -> bool:
    method = await session.get(SavedPaymentMethod, method_id)
    if not method or method.user_id != user_id:
        return False
    await session.delete(method)
    await session.commit()
    return True


async def create_notification(user_id: int, title: str, message: str, session: AsyncSession) -> Notification:
    notification = Notification(user_id=user_id, title=title, message=message)
    session.add(notification)
    await session.commit()
    await session.refresh(notification)
    return notification
