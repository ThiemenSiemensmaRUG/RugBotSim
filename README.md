# Setup

Run the setup.sh file

In order to run the python scripts, you need to install the dependencies. You can do this by running the following command:

```bash
pip install -r requirements.txt
```

Then, you need to compile the Webots controller. You can do this by running the following command both in the `controllers/cpp_supervisor` and `controllers/inspection_controller` directories:

```bash
make clean && make
```

# Usage

Second, you need to generate some dummy data. You can do this by running the following command from the root directory:

```bash
python3 python/generate_dummy_data.py
```

Then, you can run the main scripts by running the following command:

```bash
python3 python/webots.py
```

