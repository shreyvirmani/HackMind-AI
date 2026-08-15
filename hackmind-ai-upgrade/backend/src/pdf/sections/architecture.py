from src.pdf.components import create_section_title, create_card, create_table, subsection, space


class ArchitectureSection:
    def build(self, architecture):
        if not isinstance(architecture, dict):
            return []
        story = [create_section_title("System Architecture") , space(14)]

        overview = architecture.get("architecture_overview")
        pattern = architecture.get("architectural_pattern")
        if overview:
            story += [create_card("Architecture Overview", overview), space(16)]
        if pattern:
            story += [create_card("Architectural Pattern", pattern), space(16)]

        components = architecture.get("components", [])
        if components:
            rows = [[c.get("name", ""), c.get("type", ""), c.get("technology", ""), c.get("responsibility", "")] for c in components if isinstance(c, dict)]
            if rows:
                story += [subsection("Architecture Components"), create_table(["Component", "Type", "Technology", "Responsibility"], rows), space(20)]

        flow = architecture.get("data_flow", [])
        if flow:
            rows = [[str(x.get("step", "")), x.get("from_component", ""), x.get("to_component", ""), x.get("data", "")] for x in flow if isinstance(x, dict)]
            if rows:
                story += [subsection("End-to-End Data Flow"), create_table(["Step", "From", "To", "Data"], rows), space(20)]

        apis = architecture.get("api_contracts", [])
        if apis:
            rows = [[x.get("method", ""), x.get("path", ""), x.get("purpose", ""), x.get("request", ""), x.get("response", "")] for x in apis if isinstance(x, dict)]
            if rows:
                story += [subsection("API Contracts"), create_table(["Method", "Path", "Purpose", "Request", "Response"], rows), space(20)]

        db = architecture.get("database_design", [])
        if db:
            rows = [[x.get("name", ""), x.get("purpose", ""), ", ".join(x.get("key_fields", []))] for x in db if isinstance(x, dict)]
            if rows:
                story += [subsection("Database Design"), create_table(["Entity", "Purpose", "Key Fields"], rows), space(20)]

        for title, key in [
            ("Authentication & Security", "authentication_and_security"),
            ("Scalability Strategy", "scalability"),
            ("Deployment Plan", "deployment"),
            ("Folder Structure", "folder_structure"),
            ("Implementation Order", "implementation_order"),
            ("Key Architecture Decisions", "key_architecture_decisions"),
        ]:
            values = architecture.get(key, [])
            if values:
                text = "<br/>".join(f"• {v}" for v in values)
                story += [create_card(title, text), space(16)]

        diagram = architecture.get("mermaid_diagram")
        if diagram:
            story += [create_card("Architecture Diagram (Mermaid)", f"<font name='Courier'>{diagram}</font>"), space(16)]

        return story


architecture_section = ArchitectureSection()
