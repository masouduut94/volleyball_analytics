import axios from 'axios';
import {
  FileAudio,
  FileIcon,
  FileImage,
  FileText,
  FileVideo,
  Plus,
  Trash2,
  Upload,
  X,
} from 'lucide-react';
import { useRef, useState, useEffect } from 'react';

export function FileForm() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/progress");
    ws.onmessage = (event) => {
      const backendProgress = Number(event.data);
      console.log("Backend progress:", backendProgress);
      setFiles((prevFiles) =>
        prevFiles.map((file) =>
          file.processing
            ? { ...file, backendProgress }
            : file
        )
      );
    };
    return () => ws.close();
  }, []);

  function handleFileSelect(e) {
    if (!e.target.files?.length) return;

    const newFiles = Array.from(e.target.files).map((file) => ({
      file,
      uploadProgress: 0,
      backendProgress: 0,
      uploaded: false,
      processing: false,
      processed: false,
      id: file.name,
    }));

    setFiles((prev) => [...prev, ...newFiles]);

    if (inputRef.current) {
      inputRef.current.value = '';
    }
  }

  async function handleUpload() {
    if (files.length === 0 || uploading) return;
    setUploading(true);

    const uploadPromises = files.map(async (fileWithProgress) => {
      const formData = new FormData();
      formData.append('file', fileWithProgress.file);

      try {
        const endpoint = 'http://localhost:8000/file/uploadAndProcess';
        await axios.post(endpoint, formData, {
          onUploadProgress: (event) => {
            const progress = Math.round((event.loaded * 100) / (event.total || 1));
            setFiles((prevFiles) =>
              prevFiles.map((file) =>
                file.id === fileWithProgress.id
                  ? { ...file, uploadProgress: progress }
                  : file
              )
            );
          },
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        setFiles((prevFiles) =>
          prevFiles.map((file) =>
            file.id === fileWithProgress.id
              ? { ...file, uploaded: true, processing: true }
              : file
          )
        );
      } catch (err) {
        console.error(err);
      }
    });

    await Promise.all(uploadPromises);
    setUploading(false);
  }

  function removeFile(id) {
    setFiles((prev) => prev.filter((file) => file.id !== id));
  }

  function handleClear() {
    setFiles([]);
  }

  return (
    <div className="file-form">
      <h2 className="file-form-title">File Upload</h2>
      <div className="file-form-controls">
        <FileInput
          inputRef={inputRef}
          disabled={uploading}
          onFileSelect={handleFileSelect}
        />
        <ActionButtons
          disabled={files.length === 0 || uploading}
          onUpload={handleUpload}
          onClear={handleClear}
        />
      </div>
      <FileList files={files} onRemove={removeFile} uploading={uploading} />
    </div>
  );
}

function FileInput({ inputRef, disabled, onFileSelect }) {
  return (
    <>
      <input
        type="file"
        ref={inputRef}
        onChange={onFileSelect}
        multiple
        className="hidden-input"
        id="file-upload"
        disabled={disabled}
      />
      <label htmlFor="file-upload" className="button-like">
        <Plus size={18} />
        Select Files
      </label>
    </>
  );
}

function ActionButtons({ disabled, onUpload, onClear }) {
  return (
    <div className="action-buttons">
      <button
        onClick={onUpload}
        disabled={disabled}
        className="button-like"
      >
        <Upload size={18} />
        Upload
      </button>

      <button
        onClick={onClear}
        disabled={disabled}
        className="button-like"
      >
        <Trash2 size={18} />
        Clear All
      </button>
    </div>
  );
}

function FileList({ files, onRemove, uploading }) {
  if (files.length === 0) return null;

  return (
    <div className="file-list">
      <h3 className="file-list-title">Files:</h3>
      <div className="file-list-items">
        {files.map((file) => (
          <FileItem
            key={file.id}
            file={file}
            onRemove={onRemove}
            uploading={uploading}
          />
        ))}
      </div>
    </div>
  );
}

function FileItem({ file, onRemove, uploading }) {
  const Icon = getFileIcon(file.file.type);

  return (
    <div className="file-item">
      <div className="file-item-header">
        <div className="file-item-details">
          <Icon size={40} className="file-icon" />
          <div className="file-meta">
            <span className="file-name">{file.file.name}</span>
            <div className="file-info">
              <span>{formatFileSize(file.file.size)}</span>
              <span>•</span>
              <span>{file.file.type || 'Unknown type'}</span>
            </div>
          </div>
        </div>
        {!uploading && (
          <button onClick={() => onRemove(file.id)} className="remove-button">
            <X size={16} className="remove-icon" />
          </button>
        )}
      </div>
      <div className="file-progress-text" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontWeight: 500 }}>upload status:</span>
        <span>
          {file.uploaded && (file.processing && file.uploadProgress === 100)
            ? 'Completed'
            : `${Math.round(file.uploadProgress)}%`}
        </span>
      </div>
      <ProgressBar progress={file.uploadProgress}/>
      <div className="file-progress-text" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontWeight: 500 }}>processing status:</span>
        <span>
          {file.processed && (file.processing && file.backendProgress === 100)
            ? 'Completed'
            : `${Math.round(file.backendProgress)}%`}
        </span>
      </div>
      <ProgressBar progress={file.backendProgress} />
    </div>
  );
}


function ProgressBar({ progress }) {
  return (
    <div className="progress-bar">
      <div
        className="progress-bar-inner"
        style={{ width: `${progress}%` }}
      />
    </div>
  );
}


function getFileIcon(mimeType) {
  if (mimeType.startsWith('image/')) return FileImage;
  if (mimeType.startsWith('video/')) return FileVideo;
  if (mimeType.startsWith('audio/')) return FileAudio;
  if (mimeType === 'application/pdf') return FileText;
  return FileIcon;
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}


export default FileForm