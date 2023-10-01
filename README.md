# Tune Ease

Welcome to Tune Ease! This project provides intuitive website control and automatic package installation means for generating music with AI with the [GETMusic Framework](https://ai-muzic.github.io/getmusic/). The package provides a number of common music processing tools, architectural changes to the getmusic project, documentation and testing (including benchmarks), and more.

## Requirements

- You will need more than 8 gb of RAM for the checkpoint.pth the original researchers provided. 16 gb RAM is recommended.
- 4 gb of disk space (option 1), 16 gb or more of disk space (option 2), 6-7 gb of disk space (option 3).

## Installing

### Option 1:
**Do not run this without a virtual environment!**
1. Create a virtual environment using Python 3:
   ```sh
   python3 -m venv env
   ```
2. Activate the virtual environment:
   - On macOS/Linux: `source venv/bin/activate`
   - On Windows: `venv\Scripts\activate`
3. Quick and simple:
   ```sh
   pip install git+https://github.com/Pshah2023/TuneEase.git@main
   ```

### Option 2: Using Docker
1. Make sure you have Docker installed on your system. If not, you can download and install it from the official Docker website: https://www.docker.com/get-started
2. Clone this repository to your local machine and navigate to the project directory in a terminal.
3. Build the Docker image using the following command:
   ```sh
   docker compose up -d
   ```
   This will map port 8080 from the container to port 8080 on your host machine.
4. Access the server by opening a web browser and visiting http://localhost:8080

### Option 3: Codebase Sharing

1. Clone this repository to your local machine and navigate to the project directory in your terminal.
2. Install the [model checkpoint](https://1drv.ms/u/s!ArHNvccy1VzPkWGKXZDQY5k-kDi4?e=fFxcEq). **You must place it at <project_directory>/checkpoint.pth**
1. Create a virtual environment using Python 3:
   ```sh
   python3 -m venv venv
   ```
2. Activate the virtual environment:
   - On macOS/Linux: `source venv/bin/activate`
   - On Windows: `venv\Scripts\activate`
3. Install the project dependencies from `requirements.txt`:
   ```sh
   pip install --no-cache-dir -r requirements.txt
   ```
4. Install MuseScore. On a version of linux,
   ```sh
   mkdir temp
   cd temp
   wget https://cdn.jsdelivr.net/musescore/v4.1.1/MuseScore-4.1.1.232071203-x86_64.AppImage -O "MuseScore.AppImage"
   sudo chmod +x ./MuseScore.AppImage
   sudo apt install libfuse2 fuse3 libgl1-mesa-glx
   sudo apt-get install qtwayland5 jackd qjackctl
   ./MuseScore.AppImage
   ```
   On Windows and macOS, install MuseScore through the website: [https://musescore.org/en](https://musescore.org/en).

Remember to deactivate the virtual environment when you're done:
```sh
deactivate
```

Feel free to choose the setup option that best suits your needs. Enjoy the project!

## Changes to Getmusic

1. Introduced the ability to use a CPU or a GPU.
2. Structural changes to the structure.
   1. Instead of using a yaml to instantiate the model, I used a new train.py with a variable that contains the data from train.yaml
   2. Created a folder named pipeline that contains code that was previously duplicated many times.
   3. Prevented duplicated runs of the same code with new classes
   4. Improved the Pylint score from 1.25 to 5.12
3. Changed hierarchy and propagated changes.
4. Packaged this into a code shareable repo. This mean the install time has been reduced from the initial 4-5 hours it took me in the beginning to the more automatic install process offered here.

# Usage

Attempts are made to find your MuseScore and checkpoint path automatically. **Optionally, include your MuseScore and checkpoint path with the flag.** You do not need MuseScore most of the time, but you will need the checkpoint for the AI music.

Use the below to generate one file.
```bash
# If you installed through pip
tuneease-generate --checkpoint_path <required path>
# If you installed through code sharing
python -m tuneease.tuneease --checkpoint_path <required path>
```

If you want to use the server, the website is mainly for using the AI.
```bash
tuneease --museScore_path <optional path> --checkpoint_path <optional path>
python -m tuneease.server --museScore_path <optional path> --checkpoint_path <optional path>
```
Normally, you can access the server at http://localhost:8080, or you can follow whatever port flask tells you to go to.

You can use this as an import statement and follow the tuneease.py __name__ == "__main__" block. Try it out!
```python
from tuneease.tuneease import TuneEase
tuneease = TuneEase()
print(tuneease.generate()) # Prints the resulting file path of the AI music
```

There is documentation that I wrote to help you along the way. Just use help(tuneease) and you'll see it. If you don't see a specific item documented, it's not part of the web app I created. I'll slowly document the rest of the project later.

# From the [GETMusic Readme](https://github.com/microsoft/muzic/tree/main/getmusic)

### Usage Tips

Here are some tips to enhance your experience with GETMusic:

1.  Check MIDI program ID: GETMusic supports the following instruments (MIDI program): '0': piano, '25':guitar, '32':bass, '48':string, '80':lead melody. You do not need to worry about the percussion program. 

  -  FAQ:
   -   [What does these number mean?](https://github.com/microsoft/muzic/issues/132#issuecomment-1585748251)
   -   [How to check program ids?](https://github.com/microsoft/muzic/issues/133#issuecomment-1586022683)

2.  About 'bass': if you want to generate a 'bass' track, the default instrument in Musescore is '低音提琴' (Double Bass), which may not sound harmonious. Change it to '原音贝斯' (Electric Bass/Bass Guitar).

3.  Tune the volume: GETScore does not involve volume information. To obtain satisfactory composition results, you may tune the volume of each instrument. For example, our default volume for 'string' may be too loud that covers the lead melody, you may need to turn it down.

4.  Enable Chord Guidance: We recommend always enabling chord guidance when generating music to achieve a regular pattern in the generated music score.
    
5. Incremental generation: Our experience indicates that employing incremental generation when generating multiple tracks from scratch yields improved results in terms of both regularity in music patterns and overall quality. For example, you can conduct a two-stage generation: 

   -   Stage 1: chord -> lead  
   -   Stage 2: chord, lead -> bass, drum, guitar, piano, string

6.  Avoid Domain Gap:

   -   Consider Input Style: GETMusic is trained on a dataset of crawled pop music. If the style of your input MIDI has a significant domain gap from the training data, the generated results may not meet your expectations.
   -   Change Tracks: In some cases, even if your input music is of the pop genre, the generated results may still be unsatisfactory. One possible reason is that: for example, if you want to generate tracks based on your input guitar, and the guitar pattern in your input is more similar to the lead track in the training data, the domain gap appears. In this case, modifying the MIDI program ID of your guitar track to serve as a lead track can help reduce the track-wise domain gap.
   -   Tune the Input: You can try using a different random seed, modify the code to truncate the music length, or add [EMPTY]s in the end of the input to regenerate a result with variations.

## References

I utilized the original work from the first citation below, and I appreciate the other works below.

* [1] ***GETMusic**: Generating Any Music Tracks with a Unified Representation and Diffusion Framework*, Ang Lv, Xu Tan, Peiling Lu, Wei Ye, Shikun Zhang, Jiang Bian, Rui Yan, arXiv 2023.
* [2] ***MusicBERT**: Symbolic Music Understanding with Large-Scale Pre-Training*, Mingliang Zeng, Xu Tan, Rui Wang, Zeqian Ju, Tao Qin, Tie-Yan Liu, **ACL 2021**.  
* [Roformer (Su et al.) and transformers](https://github.com/huggingface/transformers/blob/v4.28.1/src/transformers/models/roformer/modeling_roformer.py)
* [VQ-diffusion](https://github.com/microsoft/VQ-Diffusion/tree/e227b2643f2842d562706534cb1c46301e116b1f)
