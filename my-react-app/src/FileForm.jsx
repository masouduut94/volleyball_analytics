import {useState} from 'react';

function FileForm() {
    const [file, setFile] = useState(null);

    const handleFileInputChange = (event) => {
        setFile(event.target.files[0]);
    }
    
    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!file) {
            alert("Please select a file to upload.");
            return;
        }
        const formData = new FormData();
        formData.append('file', file);

        try{
            const endpoint = 'http://localhost:8000/file/uploadAndProcess';
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            })
            if(response.ok){
                console.log("Filed uploaded successfully!");
            } else {
                console.error("Failed to upload file:", response.statusText);
            }
        }
        catch (error) {
            console.error("Error uploading file:", error);
        }
    }

    return(
        <div>
            <h1>Upload and Process Video</h1>
            <form onSubmit={handleSubmit}>
                <label htmlFor="file-upload" className="custom-file-upload">
                    Upload Video
                </label>
                <br />
                <input id="file-upload" type="file" accept="video/*" onChange={handleFileInputChange}/>
                <div style={{ marginTop: '20px', marginBottom: '20px' }}>
                    <button type="submit">Process Video</button>
                </div>
                    
            </form>

            { file && <p>Selected file: {file.name}</p> }

            <p>Make sure the video is in a supported format.</p>
            <p>Click the button to upload and process the video.</p>
        </div>
    )
}

export default FileForm