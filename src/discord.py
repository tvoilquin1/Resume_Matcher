from discord_webhook import DiscordWebhook, DiscordEmbed
from .models import JobMatch
from typing import List


class DiscordNotifier:
    def __init__(self, webhook_url: str):
        self.webhook = DiscordWebhook(url=webhook_url)

    async def send_matches(self, matches: List[JobMatch]) -> None:
        """Send job matches to Discord channel"""
        embed = DiscordEmbed(title="🎯 New Job Matches Found!", color="5865F2")

        for match in matches:
            embed.add_field(
                name=f"📌 {match.job.title} at {match.job.company}",
                value=f"""
                **Match Score:** {match.match_score * 100:.0f}%
                **Why:** {match.match_reason}
                """,
                inline=False,
            )

        self.webhook.add_embed(embed)
        await self.webhook.execute()
