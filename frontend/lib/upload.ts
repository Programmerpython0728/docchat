import { API_URL } from "./api";

export async function uploadDocument(
  file: File,
  onProgress?: (percent: number) => void
): Promise<{ document_id: number; filename: string; status: string }> {
  const token = localStorage.getItem("access_token");
  const formData = new FormData();
  formData.append("file", file);

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_URL}/documents/upload`);
    if (token) xhr.setRequestHeader("Authorization", `Bearer ${token}`);

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    };

    xhr.onload = () => {
      if (xhr.status === 201) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        try {
          const err = JSON.parse(xhr.responseText);
          reject(new Error(err.detail || "Upload xato"));
        } catch {
          reject(new Error(`Upload xato (${xhr.status})`));
        }
      }
    };
    xhr.onerror = () => reject(new Error("Network xato"));
    xhr.send(formData);
  });
}
