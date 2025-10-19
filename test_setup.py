#!/usr/bin/env python3
"""
Quick test script to verify the project setup.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 60)
print("Ol-GUI Setup Test")
print("=" * 60)

# Test 1: Import core modules
print("\n1. Testing imports...")
try:
    import src
    print(f"   ✓ src package (version {src.__version__})")
except ImportError as e:
    print(f"   ✗ src package: {e}")
    sys.exit(1)

try:
    from utils import config
    print(f"   ✓ utils.config")
    print(f"     - App name: {config.APP_NAME}")
    print(f"     - Config dir: {config.CONFIG_DIR}")
except ImportError as e:
    print(f"   ✗ utils.config: {e}")
    sys.exit(1)

try:
    from utils.database import Database
    print("   ✓ utils.database.Database")
except ImportError as e:
    print(f"   ✗ utils.database: {e}")
    sys.exit(1)

try:
    from models.message import Message
    from models.conversation import Conversation
    print("   ✓ models.message.Message")
    print("   ✓ models.conversation.Conversation")
except ImportError as e:
    print(f"   ✗ models: {e}")
    sys.exit(1)

try:
    from services.settings_manager import SettingsManager
    from services.conversation_manager import ConversationManager
    print("   ✓ services.settings_manager.SettingsManager")
    print("   ✓ services.conversation_manager.ConversationManager")
except ImportError as e:
    print(f"   ✗ services: {e}")
    sys.exit(1)

# Test 2: Create a test database
print("\n2. Testing database initialization...")
try:
    test_db_path = Path("/tmp/test_ol_gui.db")
    if test_db_path.exists():
        test_db_path.unlink()

    db = Database(test_db_path)
    print(f"   ✓ Database created at {test_db_path}")

    # Verify tables exist
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"   ✓ Tables created: {', '.join(tables)}")

    # Cleanup
    test_db_path.unlink()
    print("   ✓ Test database cleaned up")
except Exception as e:
    print(f"   ✗ Database test failed: {e}")
    sys.exit(1)

# Test 3: Test settings manager
print("\n3. Testing settings manager...")
try:
    test_settings_file = Path("/tmp/test_ol_gui_settings.json")
    if test_settings_file.exists():
        test_settings_file.unlink()

    settings = SettingsManager(test_settings_file)
    print(f"   ✓ Settings file created at {test_settings_file}")
    print(f"   ✓ Default theme: {settings.get('theme')}")

    # Test set/get
    settings.set("test_key", "test_value")
    assert settings.get("test_key") == "test_value"
    print("   ✓ Set/get functionality works")

    # Cleanup
    test_settings_file.unlink()
    print("   ✓ Test settings file cleaned up")
except Exception as e:
    print(f"   ✗ Settings manager test failed: {e}")
    sys.exit(1)

# Test 4: Test data models
print("\n4. Testing data models...")
try:
    msg = Message(role="user", content="Hello!")
    print(f"   ✓ Message created: {msg.role}")

    conv = Conversation(title="Test", model="llama3.2")
    conv.add_message(msg)
    print(f"   ✓ Conversation created with {len(conv.messages)} message(s)")

    history = conv.get_message_history()
    assert len(history) == 1
    assert history[0]["role"] == "user"
    print("   ✓ Message history format correct")
except Exception as e:
    print(f"   ✗ Data models test failed: {e}")
    sys.exit(1)

# Test 5: Test conversation manager
print("\n5. Testing conversation manager...")
try:
    test_db_path = Path("/tmp/test_ol_gui_conv.db")
    if test_db_path.exists():
        test_db_path.unlink()

    db = Database(test_db_path)
    conv_manager = ConversationManager(db)

    # Create conversation
    conv = conv_manager.create_conversation("Test Chat", "llama3.2")
    print(f"   ✓ Conversation created with ID: {conv.id}")

    # Add messages
    msg1 = conv_manager.add_message(conv.id, "user", "Hello")
    msg2 = conv_manager.add_message(conv.id, "assistant", "Hi there!")
    print(f"   ✓ Added 2 messages")

    # Retrieve conversation
    loaded_conv = conv_manager.get_conversation(conv.id)
    assert len(loaded_conv.messages) == 2
    print(f"   ✓ Retrieved conversation with {len(loaded_conv.messages)} messages")

    # List conversations
    convs = conv_manager.list_conversations()
    assert len(convs) == 1
    print(f"   ✓ Listed {len(convs)} conversation(s)")

    # Delete conversation
    conv_manager.delete_conversation(conv.id)
    convs = conv_manager.list_conversations()
    assert len(convs) == 0
    print(f"   ✓ Conversation deleted successfully")

    # Cleanup
    test_db_path.unlink()
    print("   ✓ Test database cleaned up")
except Exception as e:
    print(f"   ✗ Conversation manager test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ All tests passed!")
print("=" * 60)
print("\nProject setup is ready. Next steps:")
print("  1. Install dependencies: pip install -r requirements.txt")
print("  2. Run the app: python src/main.py")
print("  3. Start building UI components")
