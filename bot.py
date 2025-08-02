from botbuilder.core import TurnContext  # type: ignore
from botbuilder.schema import Activity, ActivityTypes  # type: ignore
import asyncio

class MyBot:
    def __init__(self, gemini_model):
        self.model = gemini_model

    async def on_turn(self, turn_context: TurnContext):
        activity_type = turn_context.activity.type

        if activity_type == ActivityTypes.message:
            user_message = turn_context.activity.text

            try:
                response = self.model.generate_content(user_message, stream=True)

                final_text = ""

                for chunk in response:
                    if chunk.text:
                        final_text += chunk.text

                        await turn_context.send_activity(
                            Activity(type="message", text=chunk.text)
                        )
                        await asyncio.sleep(0.12345)

            except Exception as e:
                await turn_context.send_activity(
                    Activity(type="message", text=f"[Gemini Hatası]: {str(e)}")
                )

        elif activity_type == ActivityTypes.conversation_update:
            if turn_context.activity.members_added:
                for member in turn_context.activity.members_added:
                    if member.id != turn_context.activity.recipient.id:
                        await turn_context.send_activity(
                            Activity(type="message", text="-> Merhaba! Sohbete Hoş Geldiniz... :)")
                        )

        elif activity_type == ActivityTypes.typing:
            return

        else:
            await turn_context.send_activity(
                Activity(type="message", text=f"Bu tipte bir mesaj işlenemiyor: {activity_type}")
            )
