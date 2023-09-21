# Tune Ease

Everything here is still in development. Still working on it!

Welcome to Tune Ease! This project allows you to  for generating music with AI, converting music to different file types, interpreting music, and more. 

## Requirements

- You will need more than 8 gb of RAM for the checkpoint.pth the original researchers provided. 16 gb is recommended.
- Still working on my quantized model, but 8 GB should be fine.
- 5 gb or less (unmeasured, but more likely less than more) of disk space
- Docker or run this on Ubuntu (requires MuseScore 4)


## Installing
You have two options to set up and use the code. The first option is preferred. The second option is a manual setup for developers.


### Option 1:
In the works.
Maybe in the future, you'll be able to `pip install tuneease`.
For now, you can try the below:
`pip install -e git+https://github.com/Pshah2023/TuneEase.git@main#egg=TuneEase --upgrade`

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
- MacOS is supportable, but I won't be able to do that because I don't have access to that development environment. If you have some time, add the file paths for museScore and run the potential (but not yet written) tests.

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

1. In every spot where a GPU was used, I changed the device to CPU
2. Structural changes to the structure.
   1. Instead of using a yaml to instantiate the model, I used a new train.py with a variable that contains the data from train.yaml
   2. Remvoe components from the train.yaml and propagated changes as necessary for using a new architecture
3. Rewrote a number of large files (600+ lines) to prevent duplicates of functions from existing.
4. Changed hierarchy and propagated changes.