# Team 3

# Requirements

- https://people.csail.mit.edu/hubert/pyaudio/
- mac `brew install portaudio`
- linux `sudo apt-get install portaudio19-dev`

## test install

```sh
cd client/
python3 test.py
```

# play the game

run these commands to use the client

```sh
make setup
make
```

or

```sh
cd client/
python3 main.py
```

# run local server

to run the client locally run these 3 commands in 3 terminals

1. `make server`
2. `make database`
3. `make`

# lint the python files

```sh
make lint
```

# delete the team3 environment after you are done with this project

```sh
make remove-env
```

# Sources

- https://ak.picdn.net/shutterstock/videos/1036373483/thumb/1.jpg
- https://wallpaper.dog/large/10896556.png
- https://cartoonsmartstreaming.s3.amazonaws.com/wp-content/uploads/2014/12/05001234/plane_preview.png
- https://www.vhv.rs/dpng/d/118-1189537_clouds-png-animated-cute-cartoon-cloud-png-transparent.png

# Resources

- https://kiwidamien.github.io/save-the-environment-with-conda-and-how-to-let-others-run-your-programs.html
