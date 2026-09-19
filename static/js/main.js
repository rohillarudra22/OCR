document.addEventListener("DOMContentLoaded", () => {
  const frontInput = document.getElementById("import-front");
  const backInput = document.getElementById("import-back");

  // Maximum allowed file size in bytes (16 MB)
  const MAX_SIZE = 16 * 1024 * 1024;

  function validateFileSize(inputElement) {
    if (inputElement && inputElement.files.length > 0) {
      const file = inputElement.files[0];
      if (file.size > MAX_SIZE) {
        alert(`File "${file.name}" exceeds the 16 MB size limit. Please upload a smaller image.`);
        inputElement.value = "";
        return false;
      }
    }
    return true;
  }

  if (frontInput) {
    frontInput.addEventListener("change", () => validateFileSize(frontInput));
  }

  if (backInput) {
    backInput.addEventListener("change", () => validateFileSize(backInput));
  }
});