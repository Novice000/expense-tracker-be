from typing import Annotated
from fastapi import APIRouter, HTTPException
from models import Expense, User
from schemas import ExpenseIn, ReturnMessage
from db import session_dependency
from sqlmodel import select
from fastapi import Depends
from utils.utils import get_current_user


expense_router = APIRouter(prefix='/api/expense', tags=['expense'])

@expense_router.post("/")
async def add_expense(expense: ExpenseIn, session: session_dependency, current_user: Annotated[User, Depends(get_current_user)]) -> ReturnMessage:
    """
    Add a new expense to the database.

    Args:
    expense (ExpenseIn): The expense to be added.
    session (session_dependency): The database session.
    current_user (Annotated[User, Depends(get_current_user)]): The current user.

    Returns:
    ReturnMessage: A message indicating whether the expense was added successfully.
    """
    new_expense = Expense(amount=expense.amount, description=expense.description, user_id=current_user.id, user=current_user)
    session.add(new_expense)
    session.commit()
    session.refresh(new_expense)
    return ReturnMessage(success=True, message="Expense added successfully", payload= new_expense.model_dump())

@expense_router.get("/")
async def get_expenses(session: session_dependency, current_user: Annotated[User, Depends(get_current_user)], month: int | None = None, year: int | None = None,) -> list[Expense]:
    """
    Get all the expenses of the current user filtered by month and year.

    Args:
    session (session_dependency): The database session.
    current_user (Annotated[User, Depends(get_current_user)]): The current user.
    month (int | None): The month to filter by. Defaults to None.
    year (int | None): The year to filter by. Defaults to None.

    Returns:
    list[Expenses]: A list of all the expenses of the current user filtered by month and year.
    """
    if month and year:
        month = int(month)
        year = int(year)
        query = select(Expense).where(Expense.user_id == current_user.id, Expense.timestamp.month == month, Expense.timestamp.year == year)
    else:
        query = select(Expense).where(Expense.user_id == current_user.id)
    return  query

@expense_router.get("/{expense_id}")
async def read_expense_by_id(expense_id: int, current_user: Annotated[User, Depends(get_current_user)], session: session_dependency) -> Expense:
    """
    Get an expense by its id.

    Args:
    expense_id (int): The id of the expense to be retrieved.
    current_user (Annotated[User, Depends(get_current_user)]): The current user.
    session (session_dependency): The database session.

    Returns:
    Expenses: The expense with the given id.
    """
    expense = session.get(Expense, expense_id)
    if expense.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="You are not authorized to view this expense")
    return expense



@expense_router.delete("/{expense_id}")
async def delete_expense(expense_id: int, session: session_dependency, current_user: Annotated[User, Depends(get_current_user)]) -> ReturnMessage:
    """
    Delete an expense by its id.

    Args:
    expense_id (int): The id of the expense to be deleted.
    session (session_dependency): The database session.
    current_user (Annotated[User, Depends(get_current_user)]): The current user.

    Returns:
    ReturnMessage: A message indicating whether the expense was deleted successfully.
    """
    expense = session.get(Expense, expense_id)
    if not expense:
        return ReturnMessage(success=False, message="Expense not found", payload=None)
    if expense.user_id != current_user.id:
        return ReturnMessage(success=False, message="You are not authorized to delete this expense", payload=None)
    session.delete(expense)
    session.commit()
    return ReturnMessage(success=True, message="Expense deleted successfully", payload=None)


@expense_router.put("/{expense_id}")
async def update_expense(expense_id: int, expense: ExpenseIn, session: session_dependency, current_user: Annotated[User, Depends(get_current_user)]) -> ReturnMessage:
    """
    Update an expense by its id.

    Args:
    expense_id (int): The id of the expense to be updated.
    expense (ExpenseIn): The updated expense.
    session (session_dependency): The database session.
    current_user (Annotated[User, Depends(get_current_user)]): The current user.

    Returns:
    ReturnMessage: A message indicating whether the expense was updated successfully.
    """
    expense = session.get(Expense, expense_id)
    if not expense:
        return ReturnMessage(success=False, message="Expense not found", payload=None)
    if expense.user_id != current_user.id:
        return ReturnMessage(success=False, message="You are not authorized to update this expense", payload=None)
    expense.amount = expense.amount
    expense.description = expense.description
    session.commit()
    session.refresh(expense)
    return ReturnMessage(success=True, message="Expense updated successfully", payload=expense.model_dump())
