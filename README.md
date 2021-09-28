### 1. Brew
- Run the following in your project terminal if you do not have bew installed already
`$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

### 2. Portaudio
`$ brew install portaudio`

### 3. PyAudio
`$ pip3 install pyaudio`
> If Pyaudio cannot be installed with the default pip install command, Use instead the following:
`$ pip install --global-option='build_ext' --global-option='-I/usr/local/include' --global-option='-L/usr/local/lib' pyaudio` 
>Refer to [this link](https://gist.github.com/jiaaro/9767512210a1d80a8a0d#gistcomment-3023216) if this is not working

###4. NeuralIntents
`$ pip install neuralintents` (Run this only if neuralintents.py file is missing)

## Start
While being in the venv `$ python main.py`
- If you run into SSL certification error, search for `Certificates.command` in spotlight and open the file. 
It should install the necessary certificates
>> The downloader script is broken. As a temporal workaround can manually download the punkt tokenizer from here and 
>then place the unzipped folder in the corresponding location. 
>The default folders for each OS are:
> 
>Windows: `C:\nltk_data\tokenizers`
>
> OSX: `/usr/local/share/nltk_data/tokenizers`
>
> Unix: `/usr/share/nltk_data/tokenizers`
>
>Required libraries:
- `$ pip install keyboard`
- `$ pip install pyjokes`
- `$ pip install playsound`
