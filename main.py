

if __name__ == '__main__':
    from mac_voice_assistant.AI import Assistant
    mac = Assistant('mac_voice_assistant/intents.json', model_name='mac')
    # Required methods ##Do not remove
    # custom = {}
    # mac.set_intent_methods(custom)
    mac.train_model()
    mac.save_model()
    mac.load_model()
    mac.assist()
