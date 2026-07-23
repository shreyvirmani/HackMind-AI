import asyncio

from websocket_manager import manager

from src.services.project_service import project_service

from src.controllers.planner_controller import planner_controller
from src.controllers.research_controller import research_controller
from src.controllers.judge_controller import judge_controller
from src.controllers.pitch_deck_controller import pitch_deck_controller


class WorkflowRunner:

    async def run(self, workflow):

        try:

            # --------------------------
            # Planner
            # --------------------------

            workflow.planner = "running"

            await manager.send(
                workflow.workflow_id,
                {
                    "type": "planner_started"
                },
            )

            roadmap = await asyncio.to_thread(
                planner_controller.generate_plan,
                workflow.idea,
            )

            workflow.planner = "completed"

            await manager.send(
                workflow.workflow_id,
                {
                    "type": "planner_completed"
                },
            )

            roadmap_json = roadmap.model_dump_json(indent=2)

            # --------------------------
            # Research
            # --------------------------

            workflow.research = "running"

            await manager.send(
                workflow.workflow_id,
                {
                    "type": "research_started"
                },
            )

            research = await asyncio.to_thread(
                research_controller.generate_research,
                roadmap_json,
            )

            workflow.research = "completed"

            await manager.send(
                workflow.workflow_id,
                {
                    "type": "research_completed"
                },
            )

            # --------------------------
            # Judge
            # --------------------------

            workflow.judge = "running"

            await manager.send(
                workflow.workflow_id,
                {
                    "type": "judge_started"
                },
            )

            judge = await asyncio.to_thread(
                judge_controller.evaluate_project,
                roadmap_json,
            )

            workflow.judge = "completed"

            await manager.send(
                workflow.workflow_id,
                {
                    "type": "judge_completed"
                },
            )

            # --------------------------
            # Pitch Deck
            # --------------------------

            workflow.pitch = "running"

            await manager.send(
                workflow.workflow_id,
                {
                    "type": "pitch_started"
                },
            )

            pitch = await asyncio.to_thread(
                pitch_deck_controller.generate_pitch_deck,
                roadmap_json,
            )

            workflow.pitch = "completed"

            await manager.send(
                workflow.workflow_id,
                {
                    "type": "pitch_completed"
                },
            )

            # --------------------------
            # Save Project
            # --------------------------

            project = await asyncio.to_thread(
                project_service.save_project,
                user_id=workflow.user_id,
                idea=workflow.idea,
                roadmap=roadmap,
                research=research,
                judge=judge,
                pitch_deck=pitch,
            )

            workflow.project_id = str(project.id)
            workflow.finished = True

            await manager.send(
                workflow.workflow_id,
                {
                    "type": "workflow_completed",
                    "project_id": workflow.project_id,
                },
            )

        except Exception as e:

            workflow.error = str(e)

            await manager.send(
                workflow.workflow_id,
                {
                    "type": "workflow_failed",
                    "error": str(e),
                },
            )


workflow_runner = WorkflowRunner()