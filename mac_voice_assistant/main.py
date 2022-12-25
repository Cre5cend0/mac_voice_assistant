from my_assistant import Assistant


if __name__ == '__main__':
    mac = Assistant('intents.json')
    mappings = {
        # 'greeting'  : mac_voice_assistant.hello,
        'set_volume': mac.set_volume,
        'set_rate'  : mac.set_rate,
        'set_name'  : mac.set_name,
        # 'calibrate' : mac_voice_assistant.calibrate,
        'speak_time': mac.speak_time,
        # 'tell_joke' : mac.tell_joke,
    }
    # Required methods ##Do not remove
    mac.set_intent_methods(mappings)
    mac.train_model()
    mac.save_model()
    mac.load_model()
    mac.begin_assisting()
