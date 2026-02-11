
import React, { useCallback } from 'react';

const FileUpload = ({ onFileUpload }) => {
    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            onFileUpload(content);
        };
        reader.readAsText(file);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        const file = e.dataTransfer.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            onFileUpload(content);
        };
        reader.readAsText(file);
    }

    return (
        <div
            className="p-8 border-2 border-dashed border-gray-600 rounded-lg text-center cursor-pointer hover:border-blue-500 hover:bg-gray-800 transition-colors"
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
        >
            <input
                type="file"
                accept=".jsonl,.json,.txt"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
            />
            <label htmlFor="file-upload" className="cursor-pointer">
                <div className="text-lg font-medium mb-2">Drop your logs.jsonl file here</div>
                <div className="text-sm text-gray-400">or click to select file</div>
            </label>
        </div>
    );
};

export default FileUpload;
