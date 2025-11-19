from flask import Blueprint, request
from engine.pipeline_engine import PipelineEngine

def create_webhook_blueprint(target_file):
    webhook_bp = Blueprint("webhook", __name__)
    engine = PipelineEngine()

    def extract_changed_files(data: dict) -> list[str]:
        changed_files = []
        if "commits" in data:
            for commit in data["commits"]:
                changed_files.extend(commit.get("modified", []))
                changed_files.extend(commit.get("added", []))
                changed_files.extend(commit.get("removed", []))
        return changed_files

    @webhook_bp.get("/run-pipeline")
    def run_pipeline_direct():
        pipeline = engine.load_pipeline(target_file)
        results = engine.run_pipeline(pipeline)
        if results is None:
            results = []

        # If no results were produced, treat as failure
        if results is None or len(results) == 0:
            return {
                "pipeline": target_file,
                "success": False,
                "steps": [],
                "error": "Pipeline returned no results"
            }, 500

        response = {
            "pipeline": target_file,
            "success": all(r.success for r in results),
            "steps": [r.model_dump() for r in results]
        }

        status_code = 200 if response["success"] else 500
        return response, status_code

    @webhook_bp.post("/webhook")
    def webhook():
        data = request.json

        changed_files = extract_changed_files(data)

        # Trigger ONLY when the exact input file changes
        for f in changed_files:
            if f.endswith(target_file):
                pipeline = engine.load_pipeline(target_file)
                engine.debug_print(pipeline)
                # engine.run_pipeline(pipeline)
                break

        return {"status": "ok"}

    return webhook_bp