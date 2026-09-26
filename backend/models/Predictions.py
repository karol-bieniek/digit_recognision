from typing import ClassVar

from sqlalchemy import Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from backend.database import BASE


class Predictions(BASE):
    __tablename__ = "predictions"
    __table_args__: ClassVar[dict] = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Prediction and correction data
    predicted_digit: Mapped[int] = mapped_column(
        nullable=False
    )  # What the model predicted
    correct_digit: Mapped[int] = mapped_column(
        nullable=False
    )  # True digit (user label)
    confidence: Mapped[float] = mapped_column(
        Float, nullable=True
    )  # Model confidence (e.g. 0.87)
    is_correct: Mapped[bool] = mapped_column(
        Boolean, nullable=False
    )  # 1 if prediction is correct, 0 if incorrect

    # File location
    image_path: Mapped[str] = mapped_column(String(512), nullable=False)

    # MLOps metadata
    model_version: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # np. "mnist_v1.2.0"
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )  # Event timestamp
