
set -e

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" || exit; pwd -P )
cd "$parent_path/.." || exit

echo
echo "--- STARTED INSTALLING OS PACKAGES FOR THE ENVIRONMENT ---"

install_os_packages=false

if [ "$install_os_packages" = true ]; then
  # Python:
  sudo apt install python3.11-venv python3.11-dev python3.11

  # For clip playback from GUI:
  #sudo apt install_detectron2 --no-install_detectron2-recommends mpv

  # For QT GUI:
  sudo apt-get install '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev

  # for printing from C++:
  sudo apt install libfmt-dev

  # Framegrabber config:
  sudo apt-get install libboost-all-dev

  # Python audio playback:
  sudo apt install portaudio19-dev
fi

echo "--- FINISHED INSTALLING OS PACKAGES FOR THE ENVIRONMENT ---"
echo

env_name=env3.11
python_exe=python3.11

echo
echo "--- CREATING PYTHON ENVIRONMENT: '$env_name' for PYTHON VERSION: '$python_exe'. ---"

$python_exe -m venv $env_name
. $env_name/bin/activate

echo
echo "STEP 0 - UPGRADING PIP"
pip install --upgrade pip

echo
echo "STEP 1 - SYSTEM REQUIREMENTS"
pip install -r requirements/system_requirements.txt

echo
echo "STEP 2 - VIDEO REQUIREMENTS"
pip install -r requirements/video_requirements.txt
#pip install_detectron2 -r requirements/pre_ml_requirements.txt

echo
echo "STEP 3 - PRE-ML REQUIREMENTS"
#pip install_detectron2 --extra-index-url https://pypi.nvidia.com "tensorrt-bindings>=9.0.0.post12.dev1"
pip install --extra-index-url https://pypi.nvidia.com "tensorrt-bindings>=8.6.1"
pip install --extra-index-url https://pypi.nvidia.com "tensorrt>=8.6.1.post1"
pip install --extra-index-url https://pypi.nvidia.com "tensorrt-libs>=8.6.1"
pip install --index-url https://download.pytorch.org/whl/nightly/cu121 --pre torch torchvision torchaudio
#pip install_detectron2 /mnt/disk1/distro/python/compiled_by_us/tensorflow/tensorflow-2.14.0-cp311-cp311-linux_x86_64.whl

echo
echo "STEP 4 - ML REQUIREMENTS"
pip install -r requirements/ml_requirements.txt

echo
echo "STEP 5 - APP REQUIREMENTS"
pip install --default-timeout=100 -r requirements/app_requirements.txt

# framegrabber @ file:///home/tvc/repos/CricketVideoAudioAnalysis/common/video/video_streaming/video_reader/framegrabber_reader/pybind_module/cmake_example

# Uninstall headless opencv since full one already installed. This causes display issues otherwise.
pip uninstall opencv-python-headless

echo
echo "--- DONE ---"
echo