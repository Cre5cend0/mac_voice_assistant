# Mac Voice Assistant
____________
This is a prototype software package which performs IO operations in the Host app via voice commands

## Dependencies
____________
Run the following commands in your project terminal in the same order before installing Mac Voice Assistant
### 1. Brew
Run this if you do not have brew installed already

`$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

### 2. Command Line Developer Tools - XCode (Mac Users)
Please ensure Xcode packages are up-to-date. Try running
- `$ sudo xcodebuild -license`
- `$ xcodebuild -runFirstLaunch`

### 3. Portaudio
`$ brew install portaudio`

### 4. PyAudio
`$ pip3 install pyaudio`

If Pyaudio could not be installed with the default pip install command, try the below code: 

`$ pip install --global-option='build_ext' --global-option='-I/usr/local/include' --global-option='-L/usr/local/lib' pyaudio` 
>Refer to [this link](https://gist.github.com/jiaaro/9767512210a1d80a8a0d#gistcomment-3023216) if you're still having trouble installing PyAudio

### 5. `Finally` Mac Voice Assistant
`$ pip install mac_voice_assistant`

## Debug:
____________
- If you run into SSL certification error, search for `Certificates.command` in spotlight and open the file. 
It should install the necessary certificates

- If voice is crackling or robotic, it is because the default voice might not be available on your local machine.
Follow the steps in the below link to add voices to your Mac, or change to one you have on your system already. 
Later Update self.default_voice with the desired voice.id
> https://support.apple.com/en-gb/guide/mac-help/mchlp2290/mac#:~:text=Add%20a%20new%20voice,may%20need%20to%20scroll%20down.)

- There are a few known issues with NSSS.py and pysstx3.py on macOS Ventura. 
Until we receive an update with those fixes, below is a temporary workaround for the errors in init stage.

In pyttsx3/drivers/nsss.py:
```
def _toVoice(self, attr) method:
    Replace:
         return Voice(attr['VoiceIdentifier'], attr['VoiceName'],
            [lang], attr['VoiceGender'],
            attr['VoiceAge'])
    With:
        return Voice(attr.get('VoiceIdentifier'), attr.get('VoiceName'),
            [attr.get('VoiceLocaleIdentifier', attr.get('VoiceLanguage'))], attr.get('VoiceGender'),
            attr.get('VoiceAge'))
```

```
class NSSpeechDriver(NSObject):
    Replace:
        self = super(NSSpeechDriver, self).init()
    With:
        self = objc.super(NSSpeechDriver, self).init()
```

> If the downloader script is broken. As a temporal workaround can manually download the punkt tokenizer from here and 
>then place the unzipped folder in the corresponding location. 
>The default folders for each OS are:
> 
>>Windows: `C:\nltk_data\tokenizers`
>
>> OSX: `/usr/local/share/nltk_data/tokenizers`
>
>> Unix: `/usr/share/nltk_data/tokenizers`
