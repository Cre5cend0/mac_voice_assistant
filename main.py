from mac_voice_assistant.AI import Assistant


if __name__ == '__main__':
    mac = Assistant('default_intents.json', model_name='mac')
    mappings = {
        # 'greeting'  : mac_voice_assistant.hello,
        'set_volume': mac.set_volume,
        'set_rate'  : mac.set_rate,
        'set_name'  : mac.set_name,
        'calibrate' : mac.recalibrate,
        'speak_time': mac.speak_time,
        'tell_joke' : mac.tell_joke,
    }
    # Required methods ##Do not remove
    mac.set_intent_methods(mappings)
    mac.train_model()
    mac.save_model()
    mac.load_model()
    mac.assist()
