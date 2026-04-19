/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useRef, useCallback } from 'react';
import { 
  FileUp, 
  FileText, 
  Trash2, 
  Download, 
  Settings2, 
  AlertCircle,
  FileSpreadsheet,
  Plus,
  ArrowRight,
  Info,
  CheckCircle2,
  X
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import * as XLSX from 'xlsx';

interface FileItem {
  id: string;
  file: File;
  name: string;
  size: string;
}

export default function App() {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [headerRows, setHeaderRows] = useState(1);
  const [autoRenumber, setAutoRenumber] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      addFiles(Array.from(e.target.files));
    }
  };

  const addFiles = (newFiles: File[]) => {
    const validFiles = newFiles.filter(file => {
      const ext = file.name.split('.').pop()?.toLowerCase();
      return ['xlsx', 'xls', 'csv'].includes(ext || '');
    });

    if (validFiles.length < newFiles.length) {
      setError('Một số tệp không phải định dạng Excel (.xlsx, .xls, .csv)');
    }

    const items: FileItem[] = validFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      name: file.name,
      size: formatFileSize(file.size)
    }));

    setFiles(prev => [...prev, ...items]);
    setError(null);
    setSuccess(false);
  };

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => {
    setIsDragging(false);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files) {
      addFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleMerge = async () => {
    if (files.length === 0) return;
    
    setIsProcessing(true);
    setError(null);
    setSuccess(false);

    try {
      const allData: any[][] = [];
      
      for (let i = 0; i < files.length; i++) {
        const fileItem = files[i];
        const arrayBuffer = await fileItem.file.arrayBuffer();
        const workbook = XLSX.read(arrayBuffer);
        const firstSheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[firstSheetName];
        
        // Convert sheet to array of arrays to handle skip logic easily
        const jsonData: any[][] = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

        if (i === 0) {
          // Keep everything from the first file
          allData.push(...jsonData);
        } else {
          // Skip header rows for subsequent files
          const dataOnly = jsonData.slice(headerRows);
          allData.push(...dataOnly);
        }
      }

      // Create a new workbook
      // Apply re-numbering if enabled
      if (autoRenumber) {
        let currentStt = 1;
        for (let j = headerRows; j < allData.length; j++) {
          if (!allData[j]) allData[j] = [];
          allData[j][0] = currentStt++;
        }
      }

      const newWS = XLSX.utils.aoa_to_sheet(allData);
      const newWB = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(newWB, newWS, "MergedData");

      // Generate filename based on first file or current timestamp
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
      const outputFilename = `merged_excel_${timestamp}.xlsx`;

      // Trigger download
      XLSX.writeFile(newWB, outputFilename);
      
      setSuccess(true);
    } catch (err) {
      console.error(err);
      setError('Có lỗi xảy ra trong quá trình ghép tệp. Vui lòng kiểm tra lại cấu trúc các tệp.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      {/* Professional Header */}
      <header className="prof-header">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-success rounded flex items-center justify-center text-white font-bold text-lg">
            <FileSpreadsheet className="w-5 h-5" />
          </div>
          <h1 className="text-xl font-medium">Excel Merger Pro</h1>
        </div>
        <div className="flex items-center gap-4">
          <span className="prof-badge italic">Phiên bản 2.5.0</span>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="prof-sidebar">
          <div className="flex flex-col gap-6 flex-1 overflow-auto pr-1">
            <div className="flex flex-col gap-2">
              <span className="prof-label">Cấu hình gộp file</span>
              <div className="flex flex-col gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-text-main">
                    Số hàng tiêu đề cần bỏ:
                  </label>
                  <input 
                    type="number" 
                    min="1" 
                    max="50" 
                    className="prof-input"
                    value={headerRows}
                    onChange={(e) => setHeaderRows(parseInt(e.target.value) || 1)}
                  />
                  <p className="text-[11px] text-text-secondary leading-tight italic">
                    Loại bỏ tiêu đề từ file thứ 2 trở đi để tránh trùng.
                  </p>
                </div>

                <div className="flex items-center gap-3 pt-2">
                  <div className="flex items-center h-5">
                    <input
                      id="autoRenumber"
                      type="checkbox"
                      checked={autoRenumber}
                      onChange={(e) => setAutoRenumber(e.target.checked)}
                      className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary cursor-pointer"
                    />
                  </div>
                  <div className="text-sm">
                    <label htmlFor="autoRenumber" className="font-medium text-text-main cursor-pointer">
                      Tự động đánh lại STT (Cột A)
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-2 pt-4 border-t border-gray-100">
              <span className="prof-label">Định dạng hỗ trợ</span>
              <div className="flex flex-col gap-1.5">
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <div className="w-1.5 h-1.5 rounded-full bg-success"></div>
                  Microsoft Excel (.xlsx)
                </div>
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <div className="w-1.5 h-1.5 rounded-full bg-success"></div>
                  Excel 97-2003 (.xls)
                </div>
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <div className="w-1.5 h-1.5 rounded-full bg-success"></div>
                  CSV (.csv)
                </div>
              </div>
            </div>

            {/* Notifications */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="p-3 bg-red-50 border border-red-100 rounded text-xs flex gap-2 items-start"
                >
                  <AlertCircle className="w-4 h-4 text-red-500 flex-none" />
                  <p className="text-red-700 font-medium">{error}</p>
                </motion.div>
              )}

              {success && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="p-3 bg-green-50 border border-green-100 rounded text-xs flex gap-2 items-start"
                >
                  <CheckCircle2 className="w-4 h-4 text-green-600 flex-none" />
                  <p className="text-green-800 font-medium">Đã ghép tệp thành công!</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <button
            disabled={files.length < 2 || isProcessing}
            onClick={handleMerge}
            className="prof-btn-primary flex items-center justify-center gap-2"
          >
            {isProcessing ? (
              <motion.div 
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
              >
                <Plus className="w-4 h-4" />
              </motion.div>
            ) : (
              <>
                <FileSpreadsheet className="w-4 h-4" />
                Bắt đầu ghép file
              </>
            )}
          </button>
        </aside>

        {/* Content Area */}
        <section className="prof-content">
          {/* Drop Zone */}
          <div 
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`
              prof-drop-zone
              ${isDragging ? 'prof-drop-zone-active' : 'hover:border-primary cursor-pointer'}
            `}
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileChange} 
              className="hidden" 
              multiple 
              accept=".xlsx,.xls,.csv"
            />
            <div className="p-3 bg-gray-50 rounded-full group-hover:bg-blue-50 transition-colors">
              <Download className="w-6 h-6 text-primary" />
            </div>
            <div className="text-center">
              <p className="font-medium text-text-main">
                Kéo thả các tệp Excel vào đây hoặc <span className="text-primary hover:underline">Chọn tệp</span>
              </p>
              <p className="text-[11px] opacity-70 mt-1">
                Hỗ trợ .xlsx, .xls, .csv (Đề xuất cấu trúc giống nhau)
              </p>
            </div>
          </div>

          {/* File List Container */}
          <div className="prof-card flex-1 flex flex-col overflow-hidden">
            <div className="prof-header-row">
              <div className="w-10 text-center">#</div>
              <div className="flex-1">Tên tệp</div>
              <div className="w-32 text-right px-4">Kích thước</div>
              <div className="w-24 text-center">Thao tác</div>
            </div>

            <div className="flex-1 overflow-auto">
              <AnimatePresence mode="popLayout">
                {files.map((file, index) => (
                  <motion.div
                    key={file.id}
                    layout
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="prof-row"
                  >
                    <div className="w-10 text-center text-text-secondary font-mono text-xs">{index + 1}</div>
                    <div className="flex-1 min-w-0 font-medium text-text-main flex items-center gap-2">
                       <FileText className="w-4 h-4 text-success shrink-0" />
                       <span className="truncate">{file.name}</span>
                    </div>
                    <div className="w-32 text-right px-4 text-text-secondary text-xs">{file.size}</div>
                    <div className="w-24 text-center">
                      <button 
                        onClick={(e) => {
                           e.stopPropagation();
                           removeFile(file.id);
                        }}
                        className="text-[#d93025] hover:bg-red-50 px-2 py-1 rounded text-xs font-semibold transition-colors"
                      >
                        Xoá
                      </button>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {files.length === 0 && (
                <div className="h-full flex flex-col items-center justify-center text-text-secondary opacity-40 py-20">
                  <FileUp className="w-12 h-12 mb-3 stroke-1" />
                  <p className="text-sm">Chưa có tệp nào trong danh sách</p>
                </div>
              )}
            </div>

            <div className="bg-gray-50/50 p-4 border-t border-border flex items-center justify-between">
              <div className="text-[13px] text-text-secondary">
                Tổng cộng: <span className="font-bold text-text-main">{files.length}</span> tệp
              </div>
              {files.length > 0 && (
                <button 
                  onClick={() => setFiles([])}
                  className="bg-white border border-border px-4 py-1.5 rounded text-[13px] font-medium hover:bg-gray-50 text-text-main transition-colors"
                >
                  Xoá tất cả
                </button>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
