from src.pdf.components import (
    create_section_title,
    create_card,
    space,
)


class PitchDeckSection:


    def build(self, pitch):

        story = []


        if not isinstance(pitch, dict):
            pitch = {}


        slides = pitch.get(
            "slides",
            []
        )


        if not slides:
            return story



        # =====================================================
        # HEADER
        # =====================================================

        story.append(

            create_section_title(
                "Business Pitch & Investor Narrative"
            )

        )

        story.append(
            space(16)
        )



        # =====================================================
        # SLIDES
        # =====================================================

        for slide in slides:


            if not isinstance(slide, dict):
                continue


            title = slide.get(
                "title",
                ""
            )


            content = slide.get(
                "content",
                []
            )


            if not title or not content:
                continue



            if isinstance(content, list):

                content_text = "<br/>".join(
                    [
                        f"• {item}"
                        for item in content
                    ]
                )

            else:

                content_text = str(content)



            story.append(

                create_card(

                    title,

                    content_text

                )

            )


            story.append(
                space(18)
            )



        story.append(
            space(30)
        )


        return story



pitch_deck_section = PitchDeckSection()