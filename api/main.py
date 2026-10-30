import os
import pickle
from contextlib import asynccontextmanager

try:
    import psycopg
except ImportError:  # DB driver optional when no DB is used
    psycopg = None
from fastapi import FastAPI
from pydantic import BaseModel, Field
# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

DB_URL = os.environ["DATABASE_URL"] if "DATABASE_URL" in os.environ else None

# Load the trained model created in the notebook
with open(os.path.join("model", "iris_model.pkl"), "rb") as f:
    model = pickle.load(f)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Create the log table once at startup (only if a DB is configured)
    if DB_URL is not None and psycopg is not None:
        with psycopg.connect(DB_URL) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS inferences (
                    id SERIAL PRIMARY KEY,
                    features FLOAT8[] NOT NULL,
                    prediction INT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
    yield


app = FastAPI(title="Iris API", lifespan=lifespan)


class PredictRequest(BaseModel):
    feature_array: list[float] = Field(
        ...,
        min_length=4,
        max_length=4,
        description=(
            "Exactly 4 iris flower measurements in centimetres, in this order: "
            "[0] sepal length (cm), [1] sepal width (cm), "
            "[2] petal length (cm), [3] petal width (cm)."
        ),
        json_schema_extra={"example": [5.1, 3.5, 1.4, 0.2]},
    )


class PredictResponse(BaseModel):
    prediction: dict[str, int | str] = Field(
        ...,
        description="Prediction result containing the class label and class name. The class label is an integer (0, 1, or 2) corresponding to the iris species, and the class name is a string representing the species name.",
    )



@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest):
    # model.predict returns a 1-D array for a single sample -> [class_label]
    prediction = model.predict([payload.feature_array]).tolist()

    if DB_URL is not None and psycopg is not None:
        # Log the inference (DB column is INT, so store the scalar label)
        with psycopg.connect(DB_URL) as conn:
            conn.execute(
                "INSERT INTO inferences (features, prediction) VALUES (%s, %s)",
                (payload.feature_array, prediction[0]),
            )

    return {"prediction": {
        "class_id ": prediction[0],
        "class_name": ["setosa", "versicolor", "virginica"][prediction[0]],
    }}
