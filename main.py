import debug
from data.data_test import DataTest
from data.data import Data
from utils import args, led_matrix_options
from data.scoreboard_config import ScoreboardConfig
from renderer.main import MainRenderer
from renderer.main_test import MainRendererTest

args = args()
# Read scoreboard options from config.json if it exists
config = ScoreboardConfig("config", args)

if config.testing:
    from RGBMatrixEmulator import RGBMatrix
else:
    from rgbmatrix import RGBMatrix


SCRIPT_NAME = "Fantasy Football Scoreboard"
SCRIPT_VERSION = "1.0.0"

# Get supplied command line arguments


# Check for led configuration arguments
matrixOptions = led_matrix_options(args)

# Initialize the matrix
matrix = RGBMatrix(options=matrixOptions)

# Print some basic info on startup
debug.info("{} - v{} ({}x{})".format(SCRIPT_NAME,
           SCRIPT_VERSION, matrix.width, matrix.height))

debug.set_debug_status(config)

if config.testing:
    debug.info('testing')
    data = DataTest(config)
    MainRendererTest(matrix, data).render()
else:
    data = Data(config)
    MainRenderer(matrix, data).render()
