# Iris Classifier API

This directory contains a FastAPI service that serves the trained Iris
classification model in `model/iris_model.pkl`. The model predicts one of
three Iris species:

| Class ID | Species |
|---:|---|
| 0 | setosa |
| 1 | versicolor |
| 2 | virginica |

## Run locally

From this directory, create and activate a virtual environment, then install
the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Start the API:

```powershell
uvicorn main:app --reload
```

The service listens at <http://localhost:8000>. Interactive API documentation
is available at <http://localhost:8000/docs>.

## Predict a species

Send exactly four numeric measurements in centimetres, in this order:
sepal length, sepal width, petal length, and petal width.

```powershell
Invoke-RestMethod `
  -Uri http://localhost:8000/predict `
  -Method Post `
  -ContentType 'application/json' `
  -Body '{"feature_array":[5.1,3.5,1.4,0.2]}'
```

The response contains the predicted class ID and species name. For example:

```json
{
  "prediction": {
    "class_id ": 0,
    "class_name": "setosa"
  }
}
```

The current response key is `class_id `, including a trailing space.

## Run with Docker

Build and run the image from this directory:

```powershell
docker build -t iris-api .
docker run --rm -p 8000:8000 iris-api
```

The API will then be available at <http://localhost:8000>; see `/docs` for
interactive documentation.

## Optional PostgreSQL inference logging

If `DATABASE_URL` is set, the API creates an `inferences` table at startup and
stores each prediction's four input measurements, predicted class ID, and
timestamp. If the variable is not set, predictions are served without database
logging. The PostgreSQL server must be reachable by the API, and the configured
database credentials must permit creating the table and inserting rows.

For a local run, set `DATABASE_URL` in the environment or in an `api/.env` file
before starting the service. When running in Docker, pass it as an environment
variable, for example:

```powershell
docker run --rm -p 8000:8000 `
  -e DATABASE_URL='postgresql://user:password@host:5432/database' `
  iris-api
```

Replace the example connection details with values for your PostgreSQL
instance. When connecting from a container, `host` must resolve to the database
from inside that container.
