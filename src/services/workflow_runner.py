from database.connection import SessionLocal
from database.repository import workflow_repository

from src.services.project_service import project_service
from src.services.subscription_service import subscription_service
from src.services.workflow_service import workflow_to_dict

from src.controllers.planner_controller import planner_controller
from src.controllers.research_controller import research_controller
from src.controllers.architecture_controller import architecture_controller
from src.controllers.judge_controller import judge_controller
from src.controllers.pitch_deck_controller import pitch_deck_controller

from src.models.roadmap import Roadmap
from src.models.research import ResearchReport
from src.models.architecture import ArchitectureReport
from src.models.judge import JudgeReport
from src.models.pitch_deck import PitchDeck


# Stage order, matched 1:1 with the Workflow table's status columns.
STAGE_ORDER = ["planner", "research", "architecture", "judge", "pitch"]


class WorkflowRunner:
    """
    Runs exactly ONE stage of the planner -> research -> architecture
    -> judge -> pitch pipeline per call, persisting the result to the
    database before returning. This replaces the old design, which
    ran the entire pipeline inside a single FastAPI BackgroundTask
    and pushed live updates over an in-memory WebSocket manager --
    that relied on one long-lived process holding everything in
    memory, which Vercel's serverless model doesn't provide (a
    background task isn't guaranteed to keep running once the
    response is sent, and separate requests can land on completely
    different, memory-isolated instances).

    Each call here does at most one LLM stage's worth of work
    (comfortably inside any platform's function duration limit), and
    the frontend calls this repeatedly (once per stage) until
    `finished` is true -- functionally identical to the old
    stage-by-stage progress UI, just client-driven instead of
    server-pushed.

    Safe to call repeatedly for the same workflow_id: if the next
    pending stage is already "running" (e.g. a duplicate overlapping
    request), or the workflow already finished/errored, this returns
    the current state without doing any extra work.
    """

    def advance(self, workflow_id: str, user_id: str) -> dict | None:
        db = SessionLocal()

        try:
            workflow = workflow_repository.get(db, workflow_id, user_id)

            if workflow is None:
                return None

            if workflow.finished or workflow.error:
                return workflow_to_dict(workflow)

            next_stage = self._next_pending_stage(workflow)

            if next_stage is None:
                # All five stages already completed but not yet
                # finalized (save_project never ran) -- finish now.
                return self._finalize(db, workflow)

            if getattr(workflow, next_stage) == "running":
                # Another in-flight request is already working this
                # exact stage -- don't duplicate the LLM call.
                return workflow_to_dict(workflow)

            try:
                self._run_stage(db, workflow, next_stage)
            except Exception as e:
                workflow_repository.mark_failed(db, workflow, str(e))

            return workflow_to_dict(workflow)

        finally:
            db.close()

    _STAGE_DATA_COLUMN = {
        "planner": "roadmap_data",
        "research": "research_data",
        "architecture": "architecture_data",
        "judge": "judge_data",
        "pitch": "pitch_data",
    }

    def _next_pending_stage(self, workflow) -> str | None:
        for stage in STAGE_ORDER:
            data_column = self._STAGE_DATA_COLUMN[stage]

            # A stage marked "completed" whose output never actually
            # persisted (e.g. an already-affected row from before a
            # fix to how stage output gets saved) would otherwise
            # crash every later stage trying to read None data.
            # Treat it as not-completed instead, so it simply runs
            # again on the next /advance call.
            if getattr(workflow, stage) == "completed" and getattr(workflow, data_column) is None:
                return stage

            if getattr(workflow, stage) != "completed":
                return stage
        return None

    def _run_stage(self, db, workflow, stage: str):
        workflow_repository.set_stage_status(db, workflow, stage, "running")

        if stage == "planner":
            roadmap = planner_controller.generate_plan(workflow.idea)

            workflow_repository.save_stage_output(
                db, workflow, "planner", "completed", roadmap.model_dump()
            )

        elif stage == "research":
            roadmap_json = self._roadmap_json(workflow)

            research = research_controller.generate_research(roadmap_json)

            workflow_repository.save_stage_output(
                db, workflow, "research", "completed", research.model_dump()
            )

        elif stage == "architecture":
            roadmap_json = self._roadmap_json(workflow)
            research_json = ResearchReport(
                **workflow.research_data
            ).model_dump_json(indent=2)

            architecture = architecture_controller.generate_architecture(
                roadmap_json, research_json
            )

            workflow_repository.save_stage_output(
                db, workflow, "architecture", "completed", architecture.model_dump()
            )

        elif stage == "judge":
            roadmap_json = self._roadmap_json(workflow)

            judge = judge_controller.evaluate_project(roadmap_json)

            workflow_repository.save_stage_output(
                db, workflow, "judge", "completed", judge.model_dump()
            )

        elif stage == "pitch":
            roadmap_json = self._roadmap_json(workflow)

            pitch = pitch_deck_controller.generate_pitch_deck(roadmap_json)

            workflow_repository.save_stage_output(
                db, workflow, "pitch", "completed", pitch.model_dump()
            )

            # Pitch is the last stage -- finalize immediately so the
            # frontend's final /advance call returns finished=true
            # with a project_id in one round trip, exactly as before.
            self._finalize(db, workflow)

    def _roadmap_json(self, workflow) -> str:
        return Roadmap(**workflow.roadmap_data).model_dump_json(indent=2)

    def _finalize(self, db, workflow) -> dict:
        roadmap = Roadmap(**workflow.roadmap_data)
        research = ResearchReport(**workflow.research_data)
        architecture = ArchitectureReport(**workflow.architecture_data)
        judge = JudgeReport(**workflow.judge_data)
        pitch = PitchDeck(**workflow.pitch_data)

        project = project_service.save_project(
            user_id=workflow.user_id,
            idea=workflow.idea,
            roadmap=roadmap,
            research=research,
            architecture=architecture,
            judge=judge,
            pitch_deck=pitch,
        )

        # Only counts against the Free-plan quota once a project has
        # actually completed and been saved -- a failed workflow
        # shouldn't cost the user a generation.
        subscription_service.record_generation(workflow.user_id)

        workflow_repository.mark_finished(db, workflow, str(project.id))

        return workflow_to_dict(workflow)


workflow_runner = WorkflowRunner()
