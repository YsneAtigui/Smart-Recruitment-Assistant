import React, { useRef, useState } from 'react';
import { UploadCloud, FileText, XCircle } from './Icons';

interface FileUploadProps {
  label: string;
  accept?: string;
  multiple?: boolean;
  onFilesSelected: (files: File[]) => void;
  color?: 'blue' | 'green';
}

export const FileUpload: React.FC<FileUploadProps> = ({ 
  label, 
  accept = ".pdf,.docx", 
  multiple = false, 
  onFilesSelected,
  color = 'blue'
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFiles = (newFiles: File[]) => {
    // If not multiple, replace. If multiple, append.
    const updated = multiple ? [...files, ...newFiles] : newFiles;
    setFiles(updated);
    onFilesSelected(updated);
  };

  const removeFile = (index: number) => {
    const updated = files.filter((_, i) => i !== index);
    setFiles(updated);
    onFilesSelected(updated);
  };

  const borderColor = isDragging 
    ? (color === 'blue' ? 'border-recruiter-500 bg-recruiter-50' : 'border-candidate-500 bg-candidate-50') 
    : 'border-slate-300 bg-slate-50';

  const iconColor = color === 'blue' ? 'text-recruiter-500' : 'text-candidate-500';

  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-slate-700 mb-2">{label}</label>
      <div 
        className={`relative border-2 border-dashed rounded-lg p-8 transition-all duration-200 ease-in-out flex flex-col items-center justify-center text-center cursor-pointer hover:bg-white ${borderColor}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input 
          type="file" 
          ref={inputRef} 
          className="hidden" 
          accept={accept} 
          multiple={multiple} 
          onChange={(e) => e.target.files && handleFiles(Array.from(e.target.files))}
        />
        <div className={`p-3 rounded-full bg-white shadow-sm mb-3 ${iconColor}`}>
          <UploadCloud size={32} />
        </div>
        <p className="text-sm text-slate-600 font-medium">
          Click or drag to upload {multiple ? 'files' : 'a file'}
        </p>
        <p className="text-xs text-slate-400 mt-1">
          Supported: PDF, DOCX
        </p>
      </div>

      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          {files.map((file, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 bg-white border border-slate-200 rounded-md shadow-sm animate-in fade-in slide-in-from-top-1">
              <div className="flex items-center space-x-3 overflow-hidden">
                <FileText className="text-slate-400 flex-shrink-0" size={18} />
                <span className="text-sm text-slate-700 truncate">{file.name}</span>
                <span className="text-xs text-slate-400">({(file.size / 1024).toFixed(0)} KB)</span>
              </div>
              <button 
                onClick={() => removeFile(idx)}
                className="text-slate-400 hover:text-red-500 transition-colors"
              >
                <XCircle size={18} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};