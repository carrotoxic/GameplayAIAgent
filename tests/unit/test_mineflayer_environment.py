import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from infrastructure.adapters.game.minecraft.mineflayer_environment import MineflayerEnvironmentAdapter
from domain.models.event import Event


class TestMineflayerEnvironmentAdapter(unittest.TestCase):
    """Simple unit tests for MineflayerEnvironmentAdapter"""

    def setUp(self):
        """Set up test fixtures"""
        self.adapter = MineflayerEnvironmentAdapter(
            minecraft_port=25565,
            mineflayer_port=3000,
            username="TestAgent"
        )

    def test_initialization(self):
        """Test adapter initialization"""
        self.assertEqual(self.adapter._minecraft_port, 25565)
        self.assertEqual(self.adapter._mineflayer_port, 3000)
        self.assertEqual(self.adapter._username, "TestAgent")
        self.assertFalse(self.adapter._connected)
        self.assertIsNone(self.adapter._mineflayer_process)

    @patch('infrastructure.adapters.game.minecraft.mineflayer_environment.subprocess.Popen')
    @patch('infrastructure.adapters.game.minecraft.mineflayer_environment.subprocess.run')
    @patch('infrastructure.adapters.game.minecraft.mineflayer_environment.requests.post')
    def test_reset_success(self, mock_post, mock_run, mock_popen):
        """Test successful environment reset"""
        # Mock the server response
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "state": {
                "position": {"x": 0, "y": 64, "z": 0},
                "inventory": {"wooden_pickaxe": 1},
                "health": 20.0,
                "hunger": 20.0,
                "biome": "plains",
                "nearby_blocks": ["grass", "dirt"],
                "nearby_entities": {},
                "time": "day",
                "other_blocks": [],
                "equipment": {},
                "chests": []
            }
        }
        mock_post.return_value = mock_response
        
        # Mock subprocess
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        # Execute
        event = self.adapter.reset()
        
        # Verify
        self.assertIsInstance(event, Event)
        self.assertEqual(event.position, {"x": 0, "y": 64, "z": 0})
        self.assertEqual(event.inventory, {"wooden_pickaxe": 1})
        self.assertTrue(self.adapter._connected)

    @patch('infrastructure.adapters.game.minecraft.mineflayer_environment.requests.post')
    def test_step_success(self, mock_post):
        """Test successful step execution"""
        # Setup connected state
        self.adapter._connected = True
        
        # Mock the server response
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "state": {
                "position": {"x": 1, "y": 64, "z": 0},
                "inventory": {"wooden_pickaxe": 1, "stone": 5},
                "health": 20.0,
                "hunger": 19.0,
                "biome": "plains",
                "nearby_blocks": ["grass", "dirt", "stone"],
                "nearby_entities": {},
                "time": "day",
                "other_blocks": [],
                "equipment": {},
                "chests": []
            }
        }
        mock_post.return_value = mock_response
        
        # Execute
        event = self.adapter.step("await bot.dig(block)")
        
        # Verify
        self.assertIsInstance(event, Event)
        self.assertEqual(event.position, {"x": 1, "y": 64, "z": 0})
        self.assertIn("stone", event.inventory)

    def test_step_without_reset(self):
        """Test step without reset raises error"""
        with self.assertRaises(RuntimeError) as context:
            self.adapter.step("test action")
        
        self.assertIn("must be reset", str(context.exception))

    @patch('infrastructure.adapters.game.minecraft.mineflayer_environment.requests.post')
    def test_close(self, mock_post):
        """Test environment closure"""
        # Setup connected state
        self.adapter._connected = True
        self.adapter._mineflayer_process = Mock()
        self.adapter._mineflayer_process.poll.return_value = None
        
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        
        # Execute
        self.adapter.close()
        
        # Verify
        self.assertFalse(self.adapter._connected)
        mock_post.assert_called_once()

    def test_context_manager(self):
        """Test context manager functionality"""
        with patch.object(self.adapter, 'close') as mock_close:
            with self.adapter as adapter:
                self.assertEqual(adapter, self.adapter)
            
            mock_close.assert_called_once()


if __name__ == '__main__':
    unittest.main() 