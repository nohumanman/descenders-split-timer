import unittest
from unittest.mock import AsyncMock, patch
from discord.ext import commands
from discord_bot import DiscordBot

class TestDiscordBot(unittest.TestCase):
    @unittest.skip("Not implemented")
    @patch('discord.ext.commands.Bot.get_channel')
    def test_send_message_to_channel(self, mock_get_channel):
        # Create a mock channel to be of type discord.TextChannel
        mock_channel = AsyncMock()
        mock_get_channel.return_value = mock_channel

        # Initialize the bot
        bot = DiscordBot(discord_token='dummy_token', command_prefix='!', socket_server=None, dbms=None)

        # Run the coroutine
        message = "Test message"
        channel_id = 123456789
        bot.loop.run_until_complete(bot.send_message_to_channel(message, channel_id))

        # overwrite self.get_channel to return an instance of discord.TextChannel
        mock_get_channel.return_value = mock_channel

        # Check if get_channel was called with the correct channel_id
        mock_get_channel.assert_called_with(channel_id)

        # Check if send was called on the mock channel with the correct message
        mock_channel.send.assert_awaited_with(message)

if __name__ == '__main__':
    unittest.main()