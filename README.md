
<h1 align="center">
    🏐 Volleyball Analytics
</h1>
<h1 align="center">
    <img src="assets/readme/coach2.jpg">
</h1>

[image source](https://sportsedtv.com/blog/what-to-pack-on-a-volleyball-trip-volleyball)

## 📌 Overview

**Volleyball Analytics** is an end-to-end computer vision project that turns volleyball match video into structured, queryable information—so you can move from “watching footage” to **measuring what happened**. It’s built for practical, real-time workflows where coaches, analysts, and developers want automated tagging, breakdowns, and visual overlays from broadcast-style games.

At its core, the system combines **game-state understanding** (SERVICE / PLAY / NO-PLAY) with **action and object detection** (serve/receive/set/spike/block + ball) and **court segmentation**. These signals can be streamed into a live demo, exported as annotated video, and used as building blocks for higher-level KPIs (e.g., rally segmentation, action counts, and moment extraction like ace points).

The project also includes a **FastAPI backend** (optional) for storing and retrieving results, making it easier to integrate this pipeline into larger applications (dashboards, scouting tools, or data pipelines). The machine learning functionality is organized through a unified **ML Manager** module (included as a git submodule) to keep training/inference components reusable and cleanly separated.

## 🚀 Quick Start

### 📥 Clone the Repository (Important!)

This repository uses **Git submodules** for the ML Manager. You must clone it correctly:

```bash
# Clone with submodules (RECOMMENDED)
git clone --recursive https://github.com/masouduut94/volleyball_analytics.git

# OR if already cloned, initialize submodules
git submodule update --init --recursive
```

### 🎯 What You'll Get

- **🏐 ML Pipeline**: Video classification + Object detection for volleyball analysis
- **🎮 Game State Classification**: Service, Play, No-Play detection using VideoMAE
- **🎭 Action Detection**: 6 volleyball actions (serve, receive, set, spike, block, ball)
- **🏟️ Court Segmentation**: Court boundary detection
- **📊 Analytics**: Real-time statistics and insights
- **🌐 API Backend**: FastAPI-based backend for data storage and retrieval

## 🏗️ Project Architecture

This machine learning project runs in real-time on top of **2 deep learning models**:

### 🎬 Video Classification Model (VideoMAE)
In a live broadcast game, it's important to run processes only when the game is on. To extract the periods when the game is active, [HuggingFace VideoMAE](https://huggingface.co/docs/transformers/en/tasks/video_classification) is utilized.

**🎯 Purpose**: Game state classification with 3 labels
- **🏐 SERVICE**: Start of play when a player tosses the ball to serve
- **🎮 PLAY**: Active game periods where players are playing
- **⏸️ NO-PLAY**: Inactive periods where players are not playing

**🏗️ Architecture**: 
![videomae architecture](assets/readme/videomae_architecture.jpeg)

[image source](https://huggingface.co/docs/transformers/model_doc/videomae)

### 🎯 YOLOv8 Object Detection Model
This state-of-the-art model is trained on a custom volleyball dataset for object detection and action recognition.

**🏗️ Architecture**: 
![Yolov8](assets/readme/t.webp)

[image source](https://medium.com/@syedzahidali969/principles-of-yolov8-6a90564e16c3)

**🎨 Detection Classes** (6 different objects with color-coded bounding boxes):
- 🔴 **Red box**: Volleyball ball
- 🟤 **Brown box**: Volleyball service action
- 🟢 **Green box**: Volleyball reception action
- 🔵 **Blue box**: Volleyball setting action
- 🟣 **Purple box**: Volleyball blocking action
- 🟠 **Orange box**: Volleyball spike action

## 🎥 Demo Results

The system provides real-time analysis with:
- **🎮 Game State**: Displayed in top-left corner (SERVICE/PLAY/NO-PLAY)
- **🎯 Object Detection**: Color-coded bounding boxes (only on SERVICE and PLAY frames)
- **📊 Analytics**: Real-time statistics and insights

### 🏆 Demo Videos

#### 🇫🇷 France vs 🇵🇱 Poland
![demo1](assets/readme/11_f1.gif)

#### 🇺🇸 USA vs 🇨🇦 Canada
![demo2](assets/readme/20_2_demo.gif)

#### 🇺🇸 USA vs 🇵🇱 Poland
![demo3](assets/readme/22_2_DEMO.gif)

### 🎯 Ace Point Detection
The system can extract specific game moments, like ace points:
![ace](assets/readme/ace.gif)

## 🛠️ Setup & Installation

### 📋 Prerequisites

- **🐍 Python**: 3.11 or higher
- **💾 PostgreSQL**: For database functionality (optional)
- **🎮 GPU**: Recommended for real-time inference (CUDA compatible)

### 🚀 Installation Steps

1. **Clone with Submodules**
   ```bash
   git clone --recursive https://github.com/masouduut94/volleyball_analytics.git
   cd volleyball_analytics
   ```

2. **Install Dependencies**
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip with pyproject.toml
   pip install -e .
   
   # Or using pip with dependencies from pyproject.toml
   pip install torch torchvision ultralytics transformers opencv-python pillow numpy
   ```

3. **Fix PyTorchVideo Compatibility** (⚡ **IMPORTANT!**)
   ```bash
   # Uninstall old pytorchvideo to avoid compatibility issues
   pip uninstall pytorchvideo -y
   
   # Install latest version from GitHub (fixes torchvision compatibility)
   pip install git+https://github.com/facebookresearch/pytorchvideo
   ```

4. **Download Model Weights**
   ```bash
   # Create weights directory
   mkdir -p weights
   
   # Download weights (see Weights section below)
   ```

### 🎯 Model Weights Setup

The system requires pre-trained models for inference. **Weights are automatically downloaded** when you first run the system, or you can download them manually.

#### 🚀 Automatic Download (Recommended)
```python
from ml_manager import MLManager

# Weights are automatically downloaded if missing
manager = MLManager()
```

#### 📥 Manual Download
```python
from ml_manager.utils.downloader import download_all_models

# Download all models in one ZIP file
success = download_all_models()
```

#### 📁 Final Directory Structure
```
weights/
├── 🏐 ball/weights/best.pt           # Ball detection & segmentation
├── 🎭 action/weights/best.pt         # Action detection (6 classes)  
├── 🏟️ court/weights/best.pt          # Court segmentation
└── 🎮 game_state/                    # Game state classification
    └── [checkpoint files]
```

**Download Source**: [Complete Weights ZIP](https://drive.google.com/file/d/1__zkTmGwZo2z0EgbJvC14I_3kOpgQx3o/view)

## 🧪 Testing & Inference

### 🎬 Quick Test Script

Use our comprehensive test script to validate the ML Manager with your video:

```bash
# Run complete test with your video
python test_ml_manager.py --video_path path/to/your/video.mp4

# Test only object detection
python test_ml_manager.py --video_path path/to/your/video.mp4 --mode detection

# Test only video classification
python test_ml_manager.py --video_path path/to/your/video.mp4 --mode classification

# Custom output directory
python test_ml_manager.py --video_path path/to/your/video.mp4 --output_dir my_results/
```

### 📺 Download Test Video

For testing the ML models, download a volleyball video clip from **[this YouTube video](https://www.youtube.com/watch?v=G9Ox3d62B_o&t=193s)** (starts at 3:13). This video contains excellent examples of volleyball actions and game states for testing.

**Why this video is perfect for testing:**
- 🏐 Clear volleyball actions (serve, spike, block, set)
- 🎮 Multiple game states (service, play, no-play)
- 📹 Good video quality and camera angles
- ⏱️ Multiple rallies and game situations

**How to use:**
1. Download the video using any YouTube downloader
2. Save it as `volleyball_test.mp4` (or any name you prefer)  
3. Run the test script: `python test_ml_manager.py --video_path volleyball_test.mp4`

### 🎯 Individual Model Testing

Test specific components individually:

```bash
# Basic inference test using demo.py
python src/demo.py --video_path path/to/your/video.mp4

# VideoMAE only (game state classification)
python src/VideoMAE_inference.py

# YOLO only (object detection)
python src/yolo_inference.py
```

### 🎯 ML Manager Integration

The system uses a unified **ML Manager** module for all machine learning operations:

```python
from src.ml_manager import MLManager

# Initialize ML Manager
ml_manager = MLManager(verbose=True)

# Game state classification
game_state = ml_manager.classify_game_state(frames)

# Action detection
actions = ml_manager.detect_actions(frame)

# Ball detection
ball_detections = ml_manager.detect_ball(frame)
```

**📚 ML Manager Documentation**: See [src/ml_manager/README.md](src/ml_manager/README.md) for comprehensive usage.

### 🧪 Testing the Setup

The `test_ml_manager.py` script provides comprehensive testing of all ML Manager functionality:

**🔍 What the test script does:**
- ✅ Validates video file format and properties
- ✅ Tests ML Manager initialization and model loading
- ✅ Verifies all detection models (ball, actions, players) 
- ✅ Tests game state classification with video sequences
- ✅ Runs full pipeline demos with visualization
- ✅ Generates output videos for verification

**📊 Test modes available:**
- `full`: Complete testing with both detection and classification demos
- `detection`: Object detection testing only (ball, actions, players)
- `classification`: Video classification testing only (game states)

```bash
# Comprehensive test (recommended for first-time setup)
python test_ml_manager.py --video_path path/to/volleyball_video.mp4

# Quick model validation (no video output)
python test_ml_manager.py --video_path path/to/volleyball_video.mp4 --mode detection

# Legacy testing methods
cd src/ml_manager
python test_ml_manager.py

# Test integration
cd ../..
python src/ml_manager/example_usage.py
```

## 🗄️ Database Setup (Optional)

For storing results and analytics, set up PostgreSQL:

### 1. Install PostgreSQL
Follow the [PostgreSQL installation guide](https://www.cherryservers.com/blog/how-to-install-and-setup-postgresql-server-on-ubuntu-20-04)

### 2. Create Configuration
```bash
# Create database config
cp conf/sample.env conf/.env

# Edit conf/.env with your database credentials
MODE=development
DEV_USERNAME=your_username
DEV_PASSWORD=your_password
DEV_HOST=localhost
DEV_DB=volleyball_development
DEV_PORT=5432
DEV_DRIVER=postgresql
TEST_DB_URL=sqlite:///./vb.db
```

### 3. Initialize Database
```bash
# Start the API server
uvicorn src.backend.app.app:app --reload

# In another terminal, seed the database
python src/api_init_data.py

# Run the main pipeline
python src/main.py
```

## 📊 Data Sources

The video clips used for training and testing are sourced from:
- **📺 YouTube Channel**: [Volleyball Watchdog](https://www.youtube.com/@VolleyballWatchdog/videos)
- **🏆 Content**: International volleyball matches and tournaments

## 🔮 Future Development

### 📈 Planned Features
1. **📊 Data Analysis**: Advanced KPIs and analytics
   - Service success rate analysis
   - Service zone analysis
   - Reception success rate
   - Player performance metrics
   - Team strategy analysis

2. **📚 Dataset Publication**: Open-source datasets
   - Video classification dataset
   - Volleyball object detection dataset
   - Annotated training data

3. **🎯 Real-time Analytics**: Live match analysis
   - Real-time statistics
   - Live performance metrics
   - Instant insights for coaches

## 🏗️ Project Structure

```
volleyball_analytics/
├── 🧠 src/                           # Main source code
│   ├── 🎮 ml_manager/               # ML Manager submodule
│   ├── 🌐 backend/                  # FastAPI backend
│   ├── 🎬 main.py                   # Main ML pipeline
│   ├── 🎥 demo.py                   # Demo application
│   └── 🛠️ utilities/               # Utility functions
├── 📊 data/                         # Datasets and processed data
├── 🎯 weights/                      # Model weights (download required)
├── 📚 notebooks/                    # Jupyter notebooks
├── 🛠️ scripts/                     # Utility scripts
├── 📋 conf/                         # Configuration files
└── 📖 README.md                     # This file
```

## 🆘 Troubleshooting

### Common Issues

1. **🚫 Import Errors**
   ```bash
   # Ensure submodules are initialized
   git submodule update --init --recursive
   
   # Check Python path
   python -c "from src.ml_manager import MLManager; print('Success!')"
   ```

2. **🎯 Model Weights Missing**
   - Verify weights directory structure
   - Check download links above
   - Ensure file permissions are correct

3. **🐍 Dependencies Issues**
   ```bash
   # Reinstall dependencies
   uv sync --reinstall
   
   # Or using pip
   pip install -e .
   
   # Or reinstall specific packages
   pip install torch torchvision ultralytics transformers pytorchvideo opencv-python pillow numpy
   ```

4. **🎯 PyTorchVideo Compatibility Error** (⚡ **EASIEST SOLUTION**)
   ```
   ModuleNotFoundError: No module named 'torchvision.transforms.functional_tensor'
   ```
   
   **💡 Quick Fix** (Recommended):
   ```bash
   # Uninstall old pytorchvideo
   pip uninstall pytorchvideo -y
   
   # Install latest version from GitHub (fixes compatibility)
   pip install git+https://github.com/facebookresearch/pytorchvideo
   ```
   
   **📝 Alternative Manual Fix**:
   If you encounter this error in your own code, replace:
   ```python
   import torchvision.transforms.functional_tensor as F_t
   ```
   with:
   ```python
   import torchvision.transforms.functional as F_t
   ```

5. **💾 Database Connection**
   - Verify PostgreSQL is running
   - Check `.env` file configuration
   - Ensure database exists and is accessible

## 🤝 Contributing

1. **🔀 Fork** the repository
2. **🌿 Create** a feature branch
3. **💻 Make** your changes
4. **🧪 Add** tests if applicable
5. **📝 Submit** a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Additional Resources

- **📚 Wiki**: [Datasets and Weights](https://github.com/masouduut94/volleyball_analytics/wiki/Datasets-and-Weights)
- **🌐 API Documentation**: [API Guide](https://github.com/masouduut94/volleyball_analytics/wiki/API)
- **🎮 ML Manager**: [Comprehensive Documentation](src/ml_manager/README.md)
- **📊 Examples**: [Usage Examples](src/ml_manager/example_usage.py)

---

**🏐 Happy Volleyball Analytics! Let's revolutionize the game with AI! 🚀✨**
