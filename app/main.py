from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Incident
from app.schemas import IncidentCreate, IncidentResponse

app = FastAPI(title="Ops DashBoard API")

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}



@app.post("/incidents", response_model=IncidentResponse)
def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db),
):
    db_incident = Incident(**incident.model_dump())
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)

    return db_incident


@app.get("/incidents", response_model=list[IncidentResponse])
def get_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).all()


@app.get("/incidents/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident

""" if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", reload=True) """