import json


class BootstrapPromptService:
    """Builds the implementation brief downloaded from a project page."""

    @staticmethod
    def _dump(value) -> str:
        if isinstance(value, (dict, list)):
            return json.dumps(value, indent=2, ensure_ascii=False, default=str)
        return str(value or "")

    def generate(self, project) -> str:
        return f"""# HackMind AI Project Implementation Brief

## 1. ROLE
Act as one senior engineering team working together: software architect, frontend engineer, backend engineer, database engineer, UI/UX engineer, DevOps engineer, and QA engineer. Make sound implementation decisions while respecting this specification.

## 2. SOURCE OF TRUTH
The attached HackMind AI Startup Intelligence PDF is the primary source of truth for this project.

Read the ENTIRE PDF before writing code. Treat it as the complete product and technical specification. Use this brief as structured companion data for the same project; if there is a conflict, follow the PDF unless it is technically impossible.

## 3. PROJECT UNDERSTANDING
Before implementation, extract and understand the project idea, problem, solution, target users, features, MVP scope, technology stack, roadmap, research, architecture, database requirements, API requirements, authentication, security, integrations, deployment, judge/evaluation, recommendations, and future scope.

## 4. REPOSITORY INSPECTION
Before writing code, inspect the existing repository and environment. Determine whether an existing project exists; its frontend and backend frameworks; programming languages; package manager; folder structure; database; authentication; APIs; existing components and services; environment configuration; tests; and deployment configuration.

If an existing repository is present, extend and improve it instead of blindly rebuilding the project from scratch. Preserve existing working functionality unless the PDF explicitly requires changing it.

## 5. ARCHITECTURE IMPLEMENTATION
The Architecture section in the PDF is not merely informational; it is the implementation blueprint. Translate it into actual frontend modules, backend modules, services, controllers, routes, middleware, database models, API contracts, authentication flow, external integrations, data flow, and deployment structure. Follow the specified architecture and do not introduce contradictory technologies without a compelling technical reason.

## 6. COMPLETE IMPLEMENTATION
Actually build the project. Do not merely explain the implementation. Do not substitute fake buttons, placeholder screens, dummy APIs, static mock data, TODOs, or "coming soon" functionality for the MVP. Implement every MVP capability described in the PDF.

## 7. FRONTEND
Implement the required pages/screens, navigation, reusable components, forms, validation, loading states, empty states, error states, success states, responsive design, authentication UI, and accessibility while following the product and UI direction in the PDF.

## 8. BACKEND
Implement routes, controllers, services, validation, authentication, authorization, database operations, error handling, logging, and appropriate HTTP responses.

## 9. DATABASE
Implement the PDF's database requirements, including entities, relationships, indexes, constraints, validation, and timestamps.

## 10. API CONTRACTS
Keep frontend and backend synchronized. For every important API, define and implement its endpoint, HTTP method, request, response, authentication, validation, and error handling.

## 11. SECURITY
Validate user input; secure authentication; enforce authorization; protect sensitive endpoints; prevent injection attacks; never expose secrets; use environment variables; configure CORS correctly; and securely handle third-party services.

## 12. IMPLEMENTATION ORDER
Work through this order:
1. Project setup
2. Database
3. Authentication
4. Backend foundation
5. APIs
6. Frontend foundation
7. Core user flows
8. Integrations
9. Advanced MVP features
10. Error handling
11. Security
12. Testing
13. Optimization
14. Deployment

## 13. MVP PRIORITY
Clearly distinguish CORE MVP, SECONDARY, and FUTURE SCOPE work. Complete the core MVP before spending significant effort on future-scope features.

## 14. TESTING
Before declaring completion, install dependencies; run the application; type-check; lint; run tests; verify database connectivity, authentication, APIs, primary user flows, error states, responsive behavior; and fix all build or runtime errors found.

## 15. ERROR HANDLING
When something fails, identify the root cause, fix the actual problem, rerun the affected check, check for regressions, and continue implementation. Do not hide errors with arbitrary fallbacks.

## 16. CODE QUALITY
Use modular architecture, reusable components, clean naming, separation of concerns, typed interfaces where applicable, minimal duplication, and maintainable production-quality code.

## 17. DOCUMENTATION
Document project setup, environment variables, database setup, API usage, development commands, testing, deployment, and important architectural decisions.

## 18. FINAL VERIFICATION
Verify that the project builds and starts; the database, authentication, and APIs work; frontend and backend communicate; the primary user journey and core features work; no secrets are committed; and no critical errors remain.

## 19. PROJECT DATA
The following is the actual HackMind AI data for this project. Use it directly; do not replace it with generic placeholders.

### PROJECT TITLE
{project.project_title}

### ORIGINAL IDEA
{project.idea}

### ROADMAP
{self._dump(project.roadmap)}

### RESEARCH
{self._dump(project.research)}

### ARCHITECTURE
{self._dump(getattr(project, "architecture", None))}

### JUDGE
{self._dump(project.judge)}

### PITCH DECK
{self._dump(project.pitch_deck)}

## 20. FINAL RESPONSE
After implementation, report what was built, files created, files modified, database changes, environment variables, commands to run, tests performed, known limitations, and recommended next steps.

Now read the attached HackMind AI PDF completely, inspect the existing repository/environment, create an implementation plan, and then start building the project. Do not merely describe how to build it. Actually implement it and verify that it works.
"""


bootstrap_prompt_service = BootstrapPromptService()
