# Tune Ease

Welcome to Tune Ease! This project allows you to  for generating music with AI, converting music to different file types, interpreting music, and more.

## Requirements

- You will need more than 8 gb of RAM for the checkpoint.pth the original researchers provided. 16 gb is recommended.
- 5 gb or more of disk space

## Installing
Listed by the number of times I tried it. (Way too many times!)

### Option 1:
If you cloned it, you can do:
`pip install -e .`
If you have yet to, you can do:
`pip install -e git+https://github.com/Pshah2023/TuneEase.git@main#egg=TuneEase --upgrade`

Maybe in the future, you'll be able to `pip install tuneease`. I'm going to ask the authors first.

### Option 2: Using Docker
1. Make sure you have Docker installed on your system. If not, you can download and install it from the official Docker website: https://www.docker.com/get-started
2. Clone this repository to your local machine.
3. Open a terminal and navigate to the project directory.
4. Build the Docker image using the following command:
   ```sh
   docker compose up -d
   ```
   This will map port 8080 from the container to port 8080 on your host machine.
6. Access the server by opening a web browser and visiting http://localhost:8080

### Option 3: Using a Virtual Environment
- This setup has been developed on Windows and WSL. Most Ubuntu, online coding environments, and other linux environments will be supported with this method.
- MacOS is supportable, but I won't be able to do that because I don't have access to that development environment. If you have some time, add the file paths for museScore and run the test cases.

1. Clone this repository to your local machine and navigate to the project directory in your terminal.
2. Install the model checkpoint with the below:
   ```sh
   wget https://github.com/Pshah2023/TuneEase/releases/download/0.1.0/checkpoint.pth -O backend/getmusic/checkpoint.pth -4
   ```
   The above is the command if necessary. Using your browser to download this link is faster (at least on Windows) and has a better GUI too. **You must place it at backend/getmusic/checkpoint.pth**
3. Create a virtual environment using Python 3:
   ```sh
   python3 -m venv venv
   ```
4. Activate the virtual environment:
   - On macOS/Linux: `source venv/bin/activate`
   - On Windows: `venv\Scripts\activate`
5. Install the project dependencies from `requirements.txt`:
   ```sh
   pip install --no-cache-dir -r requirements.txt
   ```
6. Install MuseScore. On a version of linux,
   ```sh
   mkdir temp
   cd temp
   wget https://cdn.jsdelivr.net/musescore/v4.1.1/MuseScore-4.1.1.232071203-x86_64.AppImage -O "MuseScore.AppImage"
   sudo chmod +x 'Muse
   sudo apt install libfuse2 fuse3 libgl1-mesa-glx
   sudo apt-get install qtwayland5 jackd qjackctl
   ./MuseScore.AppImage
   ```
   On Windows and macOS, install MuseScore through the website: [https://musescore.org/en](https://musescore.org/en).
7. Build the website: (may not be necessary)
   ```sh
   cd frontend
   npm install
   npm run build
   ```
8. Run the Python server script:
   ```sh
   cd backend
   python server.py
   ```
   **Optionally, include your MuseScore path with the flag**
   ```sh
   python server.py --museScore_path <path>
   ```
9.  Access the server by opening a web browser and visiting http://localhost:8080 or wherever port flask tells you to go to in the above command.

Remember to deactivate the virtual environment when you're done:
```sh
deactivate
```

Feel free to choose the setup option that best suits your needs. Enjoy the project!

## Changes to Getmusic

1. Introduced the ability to use both a CPU or a GPU.
2. Structural changes to the structure.
   1. Instead of using a yaml to instantiate the model, I used a new train.py with a variable that contains the data from train.yaml
   2. Created a folder named pipeline that contains code that was previously duplicated many times. (Quite painful...)
   3. Improved the Pylint score from 1.25 to 2.46
3. Changed hierarchy and propagated changes.

# From the previous getmusic readme
## Usage Tips

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

### 5. Acknowledgement

We appreciate to the following authors who make their code available:

1. [VQ-diffusion](https://github.com/microsoft/VQ-Diffusion/tree/e227b2643f2842d562706534cb1c46301e116b1f)

2. [MusicBert](https://github.com/microsoft/muzic/tree/main/musicbert)

3. [Roformer (Su et al.) and transformers](https://github.com/huggingface/transformers/blob/v4.28.1/src/transformers/models/roformer/modeling_roformer.py)
