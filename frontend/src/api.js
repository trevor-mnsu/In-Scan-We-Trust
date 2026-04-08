const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

export async function scanImage(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/scan`, {
    method: "POST",
    body: formData
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Scan request failed.");
  }
  return data;
}

export async function saveManualRecord(payload) {
  const formData = new FormData();
  formData.append("medicine_name", payload.medicine_name);
  formData.append("brand_name", payload.brand_name);
  formData.append("dose_strength", payload.dose_strength);
  formData.append("manual_notes", payload.manual_notes || "");
  if (payload.file) {
    formData.append("file", payload.file);
  }

  const response = await fetch(`${API_BASE}/manual`, {
    method: "POST",
    body: formData
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Manual save failed.");
  }
  return data;
}

export async function getRecords() {
  const response = await fetch(`${API_BASE}/records`);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Could not load records.");
  }
  return data.records || [];
}

export async function deleteRecord(recordId) {
  const response = await fetch(`${API_BASE}/records/${recordId}`, {
    method: "DELETE"
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Could not delete record.");
  }
  return data;
}
