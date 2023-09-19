# Tune Ease
``
Welcome to Tune Ease! This project allows you to run a Python server for generating music, converting music to different file types, interpreting music, and more. 

## Requirements

- 5 gb or less (unmeasured, but more likely less than more) of disk space
- Docker or run this on Ubuntu (requires MuseScore 4)


## Installing
You have two options to set up and use the code. The first option is preferred. The second option is a manual setup for developers.

### Option 1: Using Docker

1. Make sure you have Docker installed on your system. If not, you can download and install it from the official Docker website: https://www.docker.com/get-started
2. Clone this repository to your local machine.
3. Open a terminal and navigate to the project directory.
4. Build the Docker image using the following command:
   ```sh
   docker compose up -d
   ```
   This will map port 8080 from the container to port 8080 on your host machine.
6. Access the server by opening a web browser and visiting http://localhost:8080

### Option 2: Using a Virtual Environment

This option was tested only on Ubuntu. If it works on another operating system, please inform me, but if not, use Docker instead.
1. Clone this repository to your local machine.
2. Navigate to the project directory in your terminal.
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
6. Run the Python server script:
   ```sh
   cd backend
   python server.py
   ```
7. Access the server by opening a web browser and visiting http://localhost:8080
8. Remember to deactivate the virtual environment when you're done:
   ```sh
   deactivate
   ```

Feel free to choose the setup option that best suits your needs. Enjoy the project!
```