
from mac_voice_assistant.AI import Assistant

if __name__ == '__main__':
    mac = Assistant('mac_voice_assistant/intents.json', model_name='mac')
    mac.assist()

    # custom = {}
    # mac.set_intent_methods(custom)
