
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
        <div className="flex flex-col gap-4">
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

            <div className="text-center">
                <p className="text-gray-400 mb-2">Or select an example:</p>
                <div className="flex flex-wrap gap-2 justify-center">
                    {['bipartite_center.jsonl','random_los.jsonl', 'misr.jsonl', 'sar.jsonl', 'vjepa.jsonl'].map(filename => (
                        <button
                            key={filename}
                            onClick={() => {
                                fetch(`./examples/${filename}`)
                                    .then(res => res.text())
                                    .then(content => onFileUpload(content))
                                    .catch(err => console.error("Failed to load example:", err));
                            }}
                            className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors"
                        >
                            {filename}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default FileUpload;
