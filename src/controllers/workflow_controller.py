from src.controllers.planner_controller import planner_controller
from src.controllers.research_controller import research_controller
from src.controllers.judge_controller import judge_controller
from src.controllers.pitch_deck_controller import pitch_deck_controller
from src.services.project_service import project_service


class WorkflowController:

    def build_project(
        self,
        idea: str,
        user_id: str,
    ):
        print("WorkflowController.build_project() called")

        result = {
            "project_id": None,
            "status": "success",
            "roadmap": None,
            "research": None,
            "judge": None,
            "pitch_deck": None,
            "errors": {},
        }

        # ---------------------------------
        # Planner
        # ---------------------------------

        try:
            roadmap = planner_controller.generate_plan(idea)

            result["roadmap"] = roadmap

            roadmap_json = roadmap.model_dump_json(indent=2)

        except Exception as e:

            result["status"] = "failed"
            result["errors"]["planner"] = str(e)

            return result

        # ---------------------------------
        # Research
        # ---------------------------------

        try:

            result["research"] = (
                research_controller.generate_research(
                    roadmap_json
                )
            )

        except Exception as e:

            result["status"] = "partial_success"
            result["errors"]["research"] = str(e)

        # ---------------------------------
        # Judge
        # ---------------------------------

        try:

            result["judge"] = (
                judge_controller.evaluate_project(
                    roadmap_json
                )
            )

        except Exception as e:

            result["status"] = "partial_success"
            result["errors"]["judge"] = str(e)

        # ---------------------------------
        # Pitch Deck
        # ---------------------------------

        try:

            result["pitch_deck"] = (
                pitch_deck_controller.generate_pitch_deck(
                    roadmap_json
                )
            )

        except Exception as e:

            result["status"] = "partial_success"
            result["errors"]["pitch_deck"] = str(e)

        print("Reached save block")

        print("Roadmap:", roadmap is not None)
        print("Research:", result["research"] is not None)
        print("Judge:", result["judge"] is not None)
        print("Pitch:", result["pitch_deck"] is not None)
        
        # ---------------------------------
        # Save Project
        # ---------------------------------

        try:

            project = project_service.save_project(
                user_id=user_id,
                idea=idea,
                roadmap=roadmap,
                research=result["research"],
                judge=result["judge"],
                pitch_deck=result["pitch_deck"],
            )

            result["project_id"] = str(project.id)

            print(
                f"✅ Project saved successfully: {result['project_id']}"
            )

        except Exception as e:

            result["status"] = "partial_success"
            result["errors"]["database"] = str(e)

            print(
                "❌ Database save failed:",
                str(e),
            )

        return result


workflow_controller = WorkflowController()