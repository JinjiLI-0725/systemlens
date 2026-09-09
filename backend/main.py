from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="SystemLens API")


class AnalyzeRequest(BaseModel):
    problem: str


class Node(BaseModel):
    id: str
    label: str
    category: str
    description: str


class Edge(BaseModel):
    source: str
    target: str
    relationship: str
    polarity: str


class Insight(BaseModel):
    title: str
    explanation: str


class SystemAnalysis(BaseModel):
    title: str
    boundary: str
    actors: List[str]
    nodes: List[Node]
    edges: List[Edge]
    feedback_loops: List[Insight]
    leverage_points: List[Insight]
    risks: List[Insight]
    unknowns: List[str]


@app.get("/")
def root():
    return {
        "name": "SystemLens API",
        "status": "running"
    }


@app.post("/analyze", response_model=SystemAnalysis)
def analyze(request: AnalyzeRequest):
    return SystemAnalysis(
        title="Demo System Analysis",
        boundary=f"System boundary for: {request.problem}",
        actors=[
            "Actor A",
            "Actor B",
            "Actor C"
        ],
        nodes=[
            Node(
                id="1",
                label="Input Pressure",
                category="driver",
                description="A force acting on the system"
            ),
            Node(
                id="2",
                label="System Response",
                category="outcome",
                description="How the system responds"
            ),
        ],
        edges=[
            Edge(
                source="1",
                target="2",
                relationship="increases",
                polarity="positive"
            )
        ],
        feedback_loops=[
            Insight(
                title="Reinforcing Loop",
                explanation="An increase in one variable strengthens another."
            )
        ],
        leverage_points=[
            Insight(
                title="Primary leverage point",
                explanation="Change the input pressure."
            )
        ],
        risks=[
            Insight(
                title="Model uncertainty",
                explanation="The current model is only a placeholder."
            )
        ],
        unknowns=[
            "Missing external data",
            "Causal relationships not yet verified"
        ]
    )