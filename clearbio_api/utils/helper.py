import inspect
from sqlalchemy.orm import Session
from clearbio_api.models.users_model import Users
from fastapi import HTTPException


def get_user_or_404(user_id: int, db: Session) -> Users:
    """
    Checks if a user exists. Returns the user object or raises 404.
    """
    user = db.query(Users).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user

def add_users(df, db: Session):
    """
    Adds all unique user_ids from a DataFrame to the users table.
    
    Args:
        df: pandas DataFrame with a 'user_id' column
        db: SQLAlchemy session
    """
    if "user_id" not in df.columns:
        raise ValueError("DataFrame must contain 'user_id' column")

    # Get unique user IDs from the DataFrame
    user_ids = df["user_id"].astype(int).unique().tolist()  # ensure it's a list of ints

    # Query existing user_ids to avoid duplicates
    existing_user_ids = [
        u[0] for u in db.query(Users.id).filter(Users.id.in_(user_ids)).all()
    ]

    # Prepare new User objects for IDs not already in the DB
    new_users = [Users(id=uid) for uid in user_ids if uid not in existing_user_ids]

    if new_users:
        db.add_all(new_users)
        db.commit()

